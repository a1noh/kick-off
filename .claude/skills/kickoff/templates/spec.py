"""The kit's rule checker for a /kickoff project. Runs from the kit, in the project folder; writes no files.

  .venv/bin/python <kit>/templates/spec.py check      plan + code + docs obey the rules (the Stop hook runs it)
  .venv/bin/python <kit>/templates/spec.py verify N   run phase N's requirement tests + Try-it screen claims, print them

The rules are written once, in the project's CLAUDE.md ("Plan-driven" and "Coding standards"); this file enforces them.
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import progress  # noqa: E402  (the kit's plan parser, next to this file)

ROOT = Path.cwd()
SOURCE = re.compile(r"\bB\d+\b|raw\.md:L\d+|data/[\w.\-]+|plan\.md|user \d{4}-\d{2}-\d{2}")
QUOTED = re.compile(r'"[^"]+"')
FILE_LINE = re.compile(r"\b[\w/.\-]+\.(?:py|jsx?|md):\d+")
CALL = re.compile(r"`([A-Za-z_][\w.]*)\(")
SCAFFOLDING = re.compile(
    r"^(scripts/(spec|render_docs|check_llm)\.py|ui/progress\.py|\.claude/hooks/|\.claude/skills/impeccable/"
    r"|\.claude/agents/impeccable-|docs/specs/|BUILD_LOG\.md|PRODUCT\.md|CHEATSHEET\.md|docs/[^/]+\.html$)"
)
MAX_FILE, MAX_FUNCTION = 150, 30
VENV_PY = ROOT / ".venv" / "bin" / "python"
PY = str(VENV_PY) if VENV_PY.exists() else sys.executable
ENV = {k: v for k, v in os.environ.items() if k != "__PYVENV_LAUNCHER__"}  # macOS python3 leaks this into children


def plan_problems() -> list[str]:
    """Approval gate + every requirement grounded, quoted and (once its phase is ticked) backed by a citing test."""
    if not progress.plan_text():
        return []
    state, problems = progress.status(), []
    if not state:
        problems.append("plan.md: the first lines need '**Status:** draft' or '**Status:** approved <date>'")
    rules = rule_ids()
    for n, (done, _) in sorted(progress.phases().items()):
        if done and not state.startswith("approved"):
            problems.append(f"phase {n} is ticked but plan.md is not approved (Status: {state or 'missing'})")
        for req in progress.requirements(n):
            problems += requirement_problems(req, done, rules)
    return problems


def requirement_problems(req: dict, built: bool, rules: set[str]) -> list[str]:
    """Problems with one requirement: source, quoted acceptance, cited business rule, and its test once built."""
    rid, problems = req["id"], []
    if not SOURCE.search(req["traces"]):
        problems.append(f"{rid}: 'Traces to:' must cite B<n>, raw.md:L<n>, data/<file> or user <date>")
    problems += [
        f"{rid}: cites {b}, which docs/requirements.md doesn't define"
        for b in re.findall(r"\bB\d+\b", req["traces"])
        if rules and b not in rules
    ]
    if not QUOTED.search(req["acceptance"]):
        problems.append(f"{rid}: 'Acceptance:' needs the exact expected value in \"quotes\"")
    if not req["test"]:
        return problems + [f"{rid}: 'Test:' must name tests/<file>.py::<test_name>"]
    if built:
        path, name = req["test"]
        source = (ROOT / path).read_text() if (ROOT / path).exists() else ""
        body = re.search(rf"^def {name}\(.*?(?=^def |\Z)", source, re.M | re.S)
        if not body:
            problems.append(f"{rid}: test {path}::{name} does not exist")
        elif rid not in body[0]:
            problems.append(f"{rid}: test {name} must cite 'plan.md {rid}' in its docstring")
    return problems


def rule_ids() -> set[str]:
    """The business-rule ids B1..Bn defined in docs/requirements.md (empty when there is no such file)."""
    path = ROOT / "docs" / "requirements.md"
    return set(re.findall(r"^\s*- \*\*(B\d+)\*\*", path.read_text(), re.M)) if path.exists() else set()


def product_files() -> list[Path]:
    """Every Python file of the product that the coding standards cover: src/**/*.py and ui/*.py."""
    return sorted([*ROOT.glob("src/**/*.py"), *ROOT.glob("ui/*.py")])


def code_problems() -> tuple[list[str], list[str]]:
    """Coding standards: (failures, warnings) for docstrings, the §5c file list, §5c signatures and sizes."""
    listed, fails, warns = progress.interfaces(), [], []
    for path in product_files():
        rel = str(path.relative_to(ROOT))
        tree = ast.parse(path.read_text())
        if not ast.get_docstring(tree):
            fails.append(f"{rel}: starts with no docstring (what it does + where it sits in the S1 flow)")
        if rel not in listed:
            fails.append(f"{rel}: not listed in plan.md §5c (every file has a job named there)")
        lines = len(path.read_text().splitlines())
        if lines > MAX_FILE:
            warns.append(f"{rel}: {lines} lines (aim for ~{MAX_FILE})")
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not ast.get_docstring(node):
                    fails.append(f"{rel}:{node.lineno} {node.name}() has no docstring")
                if node.end_lineno - node.lineno + 1 > MAX_FUNCTION:
                    warns.append(
                        f"{rel}: {node.name}() is {node.end_lineno - node.lineno + 1} lines (aim for ~{MAX_FUNCTION})"
                    )
        fails += [f"{rel}: §5c {p}" for p in signature_problems(tree, listed.get(rel, []))]
    return fails, warns


def signature_problems(tree: ast.Module, entries: list[dict]) -> list[str]:
    """§5c lines that don't match the code: a missing function, other parameters, or a different docstring line 1."""
    problems = []
    for entry in entries:
        node = find(tree, entry["name"])
        if node is None:
            problems.append(f"{entry['name']}() is listed but not defined")
            continue
        func = (
            next((n for n in node.body if getattr(n, "name", "") == "__init__"), node)
            if isinstance(node, ast.ClassDef)
            else node
        )
        params = (
            []
            if isinstance(func, ast.ClassDef)
            else [a.arg for a in [*func.args.args, *func.args.kwonlyargs] if a.arg not in ("self", "cls")]
        )
        if params != entry["params"]:
            problems.append(f"{entry['name']}({', '.join(entry['params'])}) but the code takes ({', '.join(params)})")
        doc = (ast.get_docstring(node) or "").splitlines()
        if doc and plain(doc[0]) != plain(entry["summary"]):
            problems.append(f"{entry['name']}: docstring line 1 {doc[0]!r} must match §5c {entry['summary']!r}")
    return problems


def find(tree: ast.Module, dotted: str) -> ast.AST | None:
    """The function or class named 'name' or 'Class.method' at the top of a module, or None."""
    scope: list = tree.body
    node = None
    for part in dotted.split("."):
        node = next(
            (
                n
                for n in scope
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == part
            ),
            None,
        )
        if node is None:
            return None
        scope = getattr(node, "body", [])
    return node


def plain(text: str) -> str:
    """Text compared loosely: one space between words, no backticks, no final period, case-insensitive."""
    return re.sub(r"\s+", " ", text.replace("`", "")).strip().rstrip(".").casefold()


def doc_problems() -> list[str]:
    """Docs stay accurate: no file:line references, and every named function exists in the code."""
    problems, names = [], defined_names()
    for rel in ("docs/talk.md", "docs/plan.md"):
        text = (ROOT / rel).read_text() if (ROOT / rel).exists() else ""
        problems += [f"{rel}: '{ref}' goes stale; name the function instead" for ref in FILE_LINE.findall(text)]
    talk = (ROOT / "docs" / "talk.md").read_text() if (ROOT / "docs" / "talk.md").exists() else ""
    checked = [("docs/talk.md", talk, progress.ticked(1)), ("plan.md §5e", progress.section("5e"), progress.ticked(2))]
    for where, text, live in checked:
        lines = [line for line in text.splitlines() if live and not line.lstrip().startswith("_")]
        for call in {c for line in lines for c in CALL.findall(line)}:
            if call.split(".")[-1] not in names:
                problems.append(f"{where}: `{call}()` is not defined in src/, ui/, evals/ or scripts/")
    return problems


def defined_names() -> set[str]:
    """Every function, method and class name defined in the product, its evals and scripts."""
    files = [*product_files(), *ROOT.glob("evals/*.py"), *ROOT.glob("scripts/*.py")]
    return {
        node.name
        for path in files
        for node in ast.walk(ast.parse(path.read_text()))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def repo_problems() -> list[str]:
    """Kit scaffolding never lands in the project's git history (it runs from the kit)."""
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    return [
        f"{f} is kit scaffolding: remove it from the repo (it runs from the kit)"
        for f in tracked
        if SCAFFOLDING.match(f)
    ]


def run_tests(ids: list[str]) -> dict[str, bool]:
    """Run the given pytest ids; test name -> passed."""
    with tempfile.TemporaryDirectory() as tmp:
        xml = Path(tmp) / "r.xml"
        run = subprocess.run(
            [PY, "-m", "pytest", "-q", f"--junitxml={xml}", *ids], cwd=ROOT, capture_output=True, text=True, env=ENV
        )
        if not xml.exists():
            print(f"FAIL pytest did not run:\n{(run.stdout + run.stderr)[-800:]}")
            return {}
        return {
            c.get("name"): not any(x.tag in ("failure", "error", "skipped") for x in c)
            for c in ET.parse(xml).iter("testcase")
        }


def render_screen() -> str:
    """The app as the user sees it now (api.screen_text, or an AppTest of ui/app.py), rendered in the project's venv."""
    run = subprocess.run([PY, __file__, "_render"], cwd=ROOT, capture_output=True, text=True, env=ENV)
    out = run.stdout.split("<<<SCREEN>>>\n", 1)
    return (
        out[1].rstrip()
        if len(out) == 2
        else f"APP EXCEPTION: could not render the app\n{(run.stdout + run.stderr)[-800:]}"
    )


def _render() -> str:
    """Inside the venv: the screen text from ui/api.py (React) or an AppTest of ui/app.py (Streamlit)."""
    sys.path[:0] = [str(ROOT / "src"), str(ROOT / "ui"), str(ROOT)]
    if (ROOT / "ui" / "api.py").exists():
        try:
            import api

            return api.screen_text()
        except Exception as error:  # noqa: BLE001  (any crash is shown as the failure)
            return f"APP EXCEPTION: {type(error).__name__}: {error}"
    if not (ROOT / "ui" / "app.py").exists():
        return "APP EXCEPTION: no ui/api.py or ui/app.py"
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(ROOT / "ui" / "app.py"), default_timeout=60).run()
    if app.exception:
        return f"APP EXCEPTION: {app.exception[0].value}"
    lines = ["[tabs] " + " | ".join(t.label for t in app.tabs), "[sidebar]", *[m.value for m in app.sidebar.markdown]]
    lines += [f"[row] {e.label}" for e in app.sidebar.expander] + [
        "[main]",
        *[f"[info] {i.value}" for i in app.main.info],
    ]
    return "\n".join(lines)


def screen_claims(n: int, screen: str) -> tuple[list[str], list[str]]:
    """Each "quoted" text in a phase-n Try-it line without an input must be on the screen: (report rows, missing)."""
    lines = progress.try_it(n)
    shown = "\n".join(x for x in screen.splitlines() if not any(x.endswith(line) for line in lines))
    rows, missing = [], []
    for line in lines:
        if "`" in line:  # a line with an input describes the reply to it: its tests check that, not the screen
            continue
        for quote in QUOTED.findall(line):
            ok = quote.strip('"') in shown
            rows.append(f"  {'✅' if ok else '❌'} {quote}")
            missing += [] if ok else [quote]
    return rows, missing


def cmd_check() -> int:
    """Print every rule problem (and warning); exit 1 when any rule fails."""
    fails, warns = code_problems()
    problems = plan_problems() + fails + doc_problems() + repo_problems()
    if progress.last_ticked() and any((ROOT / "ui" / f).exists() for f in ("api.py", "app.py")):
        _, missing = screen_claims(progress.last_ticked(), render_screen())
        problems += [f"phase {progress.last_ticked()} Try it says {q} is on screen, but it isn't" for q in missing]
    for line in [*(f"FAIL {p}" for p in problems), *(f"WARN {w}" for w in warns)]:
        print(line)
    print("SPEC OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


def cmd_verify(n: int) -> int:
    """Run phase n's requirement tests and Try-it screen claims, print them, exit 1 on any failure."""
    reqs = progress.requirements(n)
    results = run_tests(sorted({f"{r['test'][0]}::{r['test'][1]}" for r in reqs if r["test"]}))
    failed = [r["id"] for r in reqs if not (r["test"] and results.get(r["test"][1]))]
    print(f"Phase {n} · {len(reqs)} requirements")
    for r in reqs:
        print(
            f"  {'❌' if r['id'] in failed else '✅'} {r['id']}  {'::'.join(r['test']) if r['test'] else '(no test)'}"
        )
    screen = render_screen()
    rows, missing = screen_claims(n, screen)
    print("Try-it screen claims:", *(rows or ["  (none)"]), sep="\n")
    bad = (
        failed
        or (["app exception"] if "APP EXCEPTION" in screen else [])
        or missing
        or ([] if reqs else ["no requirements"])
    )
    print("VERIFY OK" if not bad else f"VERIFY FAIL: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["check"]:
        sys.exit(cmd_check())
    if args[:1] == ["_render"]:
        print("<<<SCREEN>>>\n" + _render())
        sys.exit(0)
    if args[:1] == ["verify"] and len(args) == 2 and args[1].isdigit():
        sys.exit(cmd_verify(int(args[1])))
    sys.exit(__doc__)
