"""The kit's rule checker for a /kickoff project. Runs from the kit, in the project folder; writes no files.

  .venv/bin/python <kit>/templates/spec.py check      plan + code + docs obey the rules (the Stop hook runs it)
  .venv/bin/python <kit>/templates/spec.py verify N   run phase N's requirement tests + Try-it screen claims, print them

The rules are written once, in the project's CLAUDE.md ("Plan-driven" and "Coding standards"); this file enforces them.
"""

from __future__ import annotations

import ast
import json
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
SOURCE = re.compile(r"\b[BD]\d+\b|raw\.md:L\d+|data/[\w.\-]+|plan\.md|spec\.md|user \d{4}-\d{2}-\d{2}")
QUOTED = re.compile(r'"[^"]+"')
FILE_LINE = re.compile(r"\b[\w/.\-]+\.(?:py|jsx?|md):\d+")
CALL = re.compile(r"`([A-Za-z_][\w.]*)\(")
CODE_IN_TEXT = re.compile(r"\b[A-Z]\w*\(")  # e.g. Store("out") or Path("out") written as text
PRODUCT_PATH = re.compile(r"\b((?:src/[\w/]+|ui/\w+)\.py)\b")
SCAFFOLDING = re.compile(
    r"^(scripts/(spec|check_llm)\.py|ui/progress\.py|\.claude/hooks/|docs/specs/|BUILD_LOG\.md|CHEATSHEET\.md)"
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
        problems.append(f"{rid}: 'Traces to:' must cite spec.md (B<n>, D<n>), raw.md:L<n>, data/<file> or user <date>")
    problems += [
        f"{rid}: cites {b}, which docs/spec.md doesn't define"
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
    """The business-rule ids B1..Bn defined in docs/spec.md (empty when there is no such file)."""
    path = ROOT / "docs" / "spec.md"
    return set(re.findall(r"^\s*- \*\*(B\d+)\*\*", path.read_text(), re.M)) if path.exists() else set()


def product_files() -> list[Path]:
    """Every Python file the coding standards cover: src/**, ui/*.py, evals/*.py and scripts/*.py."""
    return sorted(
        [*ROOT.glob("src/**/*.py"), *ROOT.glob("ui/*.py"), *ROOT.glob("evals/*.py"), *ROOT.glob("scripts/*.py")]
    )


def file_problems() -> list[str]:
    """plan.md Files + How it works show every file the build writes and what goes in and out of each function."""
    if not progress.plan_text():
        return []
    table, problems = progress.file_table(), []
    covered = lambda rel: any(rel == row or (row.endswith("/") and rel.startswith(row)) for row in table)  # noqa: E731
    for path in [*product_files(), *ROOT.glob("tests/*.py")]:
        rel = str(path.relative_to(ROOT))
        if not covered(rel):
            problems.append(f"{rel}: missing from plan.md Files (every file the build writes is listed)")
    for row, phase in table.items():
        if progress.ticked(phase) and not (ROOT / row).exists():
            problems.append(f"plan.md Files: {row} belongs to phase {phase}, which is ticked, but it doesn't exist")
    for rel, entries in progress.interfaces().items():
        problems += [f"{rel}: plan.md {p}" for e in entries for p in shape_problems(e)]
    return problems


def shape_problems(entry: dict) -> list[str]:
    """One plan.md function: it has In and Out, In names exactly its parameters, each with its type, and Out its return type."""
    name = entry["name"]
    if entry["in"] == "" or entry["out"] == "":
        return [f"{name}() needs an **In** and an **Out** block (```jsonc, ```json or ```text)"]
    problems = [] if entry["does"] else [f"{name}() needs a **Does** list: what it does, in order, as numbered steps"]
    if isinstance(entry["in"], dict) and set(entry["in"]) - {"…"} != set(entry["params"]):
        problems.append(f"{name}(): In must name exactly its parameters {entry['params']}, not {list(entry['in'])}")
    for param, kind in entry["types"].items():
        note = entry["in_notes"].get(param, "")
        if kind and note.split("·")[0].strip().replace(" ", "") != kind.replace(" ", ""):
            problems.append(f"{name}(): In {param!r} needs the comment `// {kind} · <what it is>`")
    if entry["returns"] and entry["out_type"].replace(" ", "") != entry["returns"].replace(" ", ""):
        problems.append(f"{name}(): the Out label must say its return type: **Out** · `{entry['returns']}`")
    return problems


def code_problems() -> tuple[list[str], list[str]]:
    """Coding standards: (failures, warnings) for docstrings, the functions plan.md explains (signatures) and sizes."""
    listed, fails, warns = progress.interfaces(), [], []
    for path in product_files():
        rel = str(path.relative_to(ROOT))
        tree = ast.parse(path.read_text())
        if not ast.get_docstring(tree):
            fails.append(f"{rel}: starts with no docstring (what it does + where it sits in the system)")
        if rel.startswith(("src/", "evals/")) and rel not in listed:  # §3 explains the backend, §5 the evals; ui/ gets a §2 line
            fails.append(f"{rel}: no function of it is explained in plan.md Functions (src/) or Evals (evals/)")
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
        for problem in signature_problems(tree, listed.get(rel, [])):
            # A planned function a later phase adds is only a warning until every phase is ticked.
            planned = problem.endswith("listed but not defined") and not all(d for d, _ in progress.phases().values())
            (warns if planned else fails).append(f"{rel}: plan.md: {problem}")
    return fails, warns


def signature_problems(tree: ast.Module, entries: list[dict]) -> list[str]:
    """plan.md function blocks that don't match the code: a missing function, other parameters, or a different docstring line 1."""
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
            problems.append(f"{entry['name']}: docstring line 1 {doc[0]!r} must match plan.md {entry['summary']!r}")
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
        if rel == "docs/plan.md":
            problems += json_problems(text) + hidden_tag_problems(text)
        for diagram in re.findall(r"```mermaid\n(.*?)```", text, re.S):
            problems += [f"{rel}: diagram node {node} is a dead end (no arrow out)" for node in dead_ends(diagram)]
    problems += architecture_problems()
    problems += arrow_number_problems()
    talk = (ROOT / "docs" / "talk.md").read_text() if (ROOT / "docs" / "talk.md").exists() else ""
    checked = [("docs/talk.md", talk, progress.ticked(1)), ("plan.md How it works", progress.section("How it works"), progress.ticked(2))]
    for where, text, live in checked:
        lines = [line for line in text.splitlines() if live and not line.lstrip().startswith("_")]
        for call in {c for line in lines for c in CALL.findall(line)}:
            if call.split(".")[-1] not in names:
                problems.append(f"{where}: `{call}()` is not defined in src/, ui/, evals/ or scripts/")
    return problems


def architecture_problems() -> list[str]:
    """The architecture diagram matches the code plan: one box per product file in plan.md Files, and no other files."""
    planned = {f for f in progress.file_table() if re.match(r"(src/.+|ui/[^/]+)\.py$", f)}
    talk = (ROOT / "docs" / "talk.md").read_text() if (ROOT / "docs" / "talk.md").exists() else ""
    diagrams = [("plan.md How it works", progress.section("How it works"), bool(planned))]
    diagrams.append(("docs/talk.md §3", talk, progress.ticked(4)))  # talk.md copies the diagram in phase 4
    problems = []
    for where, text, live in diagrams:
        drawn = {f for block in re.findall(r"```mermaid\n(.*?)```", text, re.S) for f in PRODUCT_PATH.findall(block)}
        if not live:
            continue
        problems += [f"{where}: no box for {f} (every product file in plan.md Files is drawn)" for f in sorted(planned - drawn)]
        problems += [f"{where}: a box for {f}, which plan.md Files doesn't list" for f in sorted(drawn - planned)]
    return problems


def arrow_number_problems() -> list[str]:
    """The How-it-works diagram numbers the arrows of one request's path 1, 2, 3, … once each, in the order drawn."""
    diagrams = re.findall(r"```mermaid\n(.*?)```", progress.section("How it works"), re.S)
    numbers = [int(n) for n in re.findall(r'-- "(\d+) ', diagrams[0] if diagrams else "")]
    if numbers and numbers != list(range(1, len(numbers) + 1)):
        return [f"plan.md How it works: number the request's arrows 1, 2, 3, … once each, in order (found {numbers})"]
    return []


def json_problems(text: str) -> list[str]:
    """Every ```json block in plan.md is valid JSON, pretty-printed: one key per line, 2-space indent."""
    problems = []
    for kind, raw in re.findall(r"```(jsonc|json)\n(.*?)\n```", text, re.S):
        block = progress.without_comments(raw)[0] if kind == "jsonc" else raw
        try:
            value = json.loads(block)
        except json.JSONDecodeError as error:
            problems.append(f"docs/plan.md: a ```json block isn't valid JSON ({error.msg}): {block[:50]!r}")
            continue
        if block != json.dumps(value, indent=2, ensure_ascii=False):
            problems.append(f"docs/plan.md: pretty-print this ```json block (one key per line, 2-space indent): {block[:50]!r}")
        problems += [
            f"docs/plan.md: {text!r} is code, not data: show what it holds (a Store → its files, a path → \"out\")"
            for text in strings(value)
            if '"' in text or CODE_IN_TEXT.search(text)
        ]
    return problems


def hidden_tag_problems(text: str) -> list[str]:
    """A bare <name> outside code is hidden by markdown (it reads as an HTML tag): it must sit inside backticks."""
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    prose = re.sub(r"`[^`\n]*`", "", prose)
    tags = set(re.findall(r"<[a-z_]+>", prose)) - {"<details>", "<summary>"}  # the dropdowns are meant as HTML
    return [f"docs/plan.md: {tag} outside backticks is hidden by markdown: write `{tag}`" for tag in sorted(tags)]


def strings(value: object) -> list[str]:
    """Every text value inside a JSON value (keys excluded), so each can be checked for readability."""
    if isinstance(value, dict):
        return [s for item in value.values() for s in strings(item)]
    if isinstance(value, list):
        return [s for item in value for s in strings(item)]
    return [value] if isinstance(value, str) else []


def dead_ends(diagram: str) -> list[str]:
    """Mermaid nodes with no arrow out that are neither an end point (["…"]) nor a store [("…")]."""
    shapes = dict(re.findall(r"\b([A-Za-z]\w*)(\(\[|\[\(|\{\{|\[|\()\"", diagram))
    sources = set(re.findall(r"^\s*([A-Za-z]\w*)\b[^\n]*?--", diagram, re.M))
    return sorted(node for node, shape in shapes.items() if node not in sources and shape not in ("([", "[("))


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
    """The app as the user sees it now (api.screen_text), rendered in the project's venv."""
    run = subprocess.run([PY, __file__, "_render"], cwd=ROOT, capture_output=True, text=True, env=ENV)
    out = run.stdout.split("<<<SCREEN>>>\n", 1)
    if len(out) == 2:
        return out[1].rstrip()
    return f"APP EXCEPTION: could not render the app\n{(run.stdout + run.stderr)[-800:]}"


def _render() -> str:
    """Inside the venv: the screen as text from ui/api.py, the same JSON the browser renders."""
    sys.path[:0] = [str(ROOT / "src"), str(ROOT / "ui"), str(ROOT)]
    if not (ROOT / "ui" / "api.py").exists():
        return "APP EXCEPTION: no ui/api.py"
    try:
        import api

        return api.screen_text()
    except Exception as error:  # noqa: BLE001  (any crash is shown as the failure)
        return f"APP EXCEPTION: {type(error).__name__}: {error}"


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
    problems = plan_problems() + fails + file_problems() + doc_problems() + repo_problems()
    if progress.last_ticked() and (ROOT / "ui" / "api.py").exists():
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
