"""Kit self-test: proves /kickoff builds a minimal classroom whose rules (plan, coding standards, docs) are enforced.

  python3 ~/.claude/skills/kickoff/tests/selftest.py          (add --keep to leave the temp classroom for a look)

It extracts the REAL setup + verify blocks from ../SKILL.md (so it tests what /kickoff runs), runs them in a temp
folder, then plants good and broken plans, code and docs and checks that the kit's spec.py and hooks react correctly.
"""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
SKILL = (KIT / "SKILL.md").read_text()
SPEC = KIT / "templates" / "spec.py"
results: list[tuple[str, bool, str]] = []

PLAN = """# Plan: probe

**Status:** {status}

## 3. Files
| File | Phase | Job | Takes in | Gives back |
|---|---|---|---|---|
| `src/agent.py` | 1 | brain | a message | the reply |
| `ui/api.py` | 1 | door | — | the screen |
| `tests/test_phase1.py` | 1 | proves P1.R1 | — | — |

## 4. Functions
### `src/agent.py` · brain: replies
- `reply(text: str) -> str` · Reply to one message · probe
  - in: `text` "hi"
  - out: "hello"
### `ui/api.py` · door: the screen
- `screen_text() -> str` · The screen as text · probe
  - in: nothing
  - out: "[tabs] door | …"

## 6. Flow (S1)
| # | Call | Returns |
|---|---|---|
| 1 | `reply("hi")` | "hello" |

## 7. Phases
- [{tick}] Phase 1: probe
  - **On screen (before → after):** nothing → Board S1 ⬜→✅
  - **Try it:**
    1. Sidebar shows "{claim}"
  - **Requirements:**
    - **P1.R1** · greeting
      - Traces to: {traces}
      - Acceptance: input `hi` → reply {acceptance}
      - Test: tests/test_phase1.py::{test}
- [ ] Phase 2: next
"""
GOOD = {
    "status": "approved 2026-01-01",
    "tick": " ",
    "claim": "✅ P1: probe",
    "traces": "B1 · raw.md:L3",
    "acceptance": '"hello"',
    "test": "test_r1_greeting",
}
AGENT = '"""Probe agent: replies to one message (S1, step 1)."""\n\n\ndef reply(text: str) -> str:\n    """Reply to one message."""\n    return "hello"\n'
API = '"""Probe screen: the door (S1 ends here)."""\n\n\ndef screen_text() -> str:\n    """The screen as text."""\n    return "[tabs] door | 📊 Owner dashboard\\n[sidebar]\\n✅ P1: probe"\n'
TEST = 'from agent import reply\n\n\ndef test_r1_greeting():\n    """plan.md P1.R1: hi -> hello."""\n    assert reply("hi") == "{want}"\n'


def block(title: str) -> str:
    """The bash block under a '## <title>' heading in SKILL.md."""
    found = re.search(rf"^## {re.escape(title)}\b.*?\n```bash\n(.*?)\n```\n", SKILL, re.M | re.S)
    assert found, f"no '{title}' block in SKILL.md"
    return found[1]


def sh(cmd: str, cwd: Path, stdin: str = "") -> subprocess.CompletedProcess:
    """Run a bash command in cwd with the classroom's environment."""
    env = {
        **{k: v for k, v in os.environ.items() if k != "__PYVENV_LAUNCHER__"},
        "CLAUDE_PROJECT_DIR": str(cwd),
        "DEST": str(cwd),
        "KIT_HOME": str(KIT),
    }
    return subprocess.run(["bash", "-c", cmd], cwd=cwd, input=stdin, capture_output=True, text=True, env=env)


def expect(name: str, ok: bool, detail: str = "") -> None:
    """Record and print one check."""
    results.append((name, ok, detail))
    print(f"{'✅' if ok else '❌'} {name}" + (f"  · {detail[:400]}" if detail and not ok else ""))


def write(c: Path, rel: str, text: str) -> None:
    """Write a file inside the classroom, creating folders."""
    (c / rel).parent.mkdir(parents=True, exist_ok=True)
    (c / rel).write_text(text)


def check(c: Path) -> subprocess.CompletedProcess:
    """The kit's spec.py check, run in the classroom."""
    return sh(f".venv/bin/python {SPEC} check", c)


def plan(c: Path, **changes: str) -> None:
    """Write the probe plan with some fields changed."""
    write(c, "docs/plan.md", PLAN.format(**{**GOOD, **changes}))


def rejects(c: Path, name: str, needle: str) -> None:
    """Expect spec.py check to fail with a message containing needle."""
    run = check(c)
    expect(name, run.returncode == 1 and needle in run.stdout, run.stdout)


def setup(c: Path) -> None:
    """T1–T5: the setup + verify blocks, a minimal repo, and the import paths."""
    run = sh(block("Setup block"), c)
    expect("T1 setup block runs (SETUP OK)", "SETUP OK" in run.stdout, run.stdout[-300:] + run.stderr[-300:])
    run = sh(block("Verify block"), c)
    expect(
        "T2 verify block: all 6 checks OK", len(re.findall(r"^OK \d/6", run.stdout, re.M)) == 6, run.stdout + run.stderr
    )
    tracked = set(sh("git ls-files", c).stdout.split())
    want = {".claude/settings.json", ".gitignore", "CLAUDE.md", "docs/talk.md", "notes/raw.md", "pyproject.toml"}
    expect("T3 the repo holds only project files (no kit scaffolding)", tracked == want, f"{sorted(tracked ^ want)}")
    expect("T4 fresh classroom passes spec check", check(c).returncode == 0, check(c).stdout)
    write(c, "src/zz_mod.py", "X = 1\n")
    write(c, "ui/zz_ui.py", "Y = 2\n")
    run = sh(f"{c}/.venv/bin/python -c 'import zz_mod, zz_ui, progress; print(zz_mod.X + zz_ui.Y)'", c.parent)
    expect(
        "T5 src/, ui/ and the kit's progress import from anywhere (classroom.pth)",
        run.stdout.strip() == "3",
        run.stderr,
    )
    (c / "src/zz_mod.py").unlink()
    (c / "ui/zz_ui.py").unlink()


def plan_rules(c: Path) -> None:
    """T6–T13: requirements are grounded, quoted and tested, behind the approval gate."""
    write(c, "docs/spec.md", "# Spec: probe\n## Business rules\n- **B1** greet back · raw.md:L3\n")
    write(c, "src/agent.py", AGENT)
    write(c, "ui/api.py", API)
    write(c, "tests/test_phase1.py", TEST.format(want="hello"))
    plan(c)
    expect("T6 good plan, phase not ticked → SPEC OK", check(c).returncode == 0, check(c).stdout)
    plan(c, traces="my intuition")
    rejects(c, "T7 untraced requirement rejected", "Traces to")
    plan(c, acceptance="it works")
    rejects(c, "T8 acceptance without a quoted value rejected", "quotes")
    plan(c, traces="B9 · raw.md:L3")
    rejects(c, "T9 a business rule spec.md doesn't define is rejected", "B9")
    plan(c, tick="x", test="test_r1_missing")
    rejects(c, "T10 ticked phase whose test doesn't exist rejected", "does not exist")
    write(c, "tests/test_phase1.py", TEST.format(want="hello").replace("plan.md P1.R1", "greets"))
    plan(c, tick="x")
    rejects(c, "T11 test that doesn't cite its requirement rejected", "must cite")
    write(c, "tests/test_phase1.py", TEST.format(want="hello"))
    plan(c, tick="x", status="draft")
    rejects(c, "T12 ticked phase under a draft plan rejected (approval gate)", "not approved")
    plan(c, tick="x")
    expect("T13 approved + ticked + tested + on screen → SPEC OK", check(c).returncode == 0, check(c).stdout)


def code_rules(c: Path) -> None:
    """T14–T18: the coding standards, enforced on src/ and ui/*.py."""
    cases = {
        "T14 file without a docstring rejected": ("src/agent.py", AGENT.split("\n", 1)[1], "no docstring"),
        "T15 function without a docstring rejected": (
            "src/agent.py",
            AGENT.replace('    """Reply to one message."""\n', ""),
            "has no docstring",
        ),
        "T16 plan.md Functions parameters that differ from the code rejected": (
            "src/agent.py",
            AGENT.replace("text: str", "message: str"),
            "takes",
        ),
        "T17 plan.md Functions line that differs from docstring line 1 rejected": (
            "src/agent.py",
            AGENT.replace("Reply to one message.", "Answer."),
            "must match",
        ),
        "T18 a file with no section in plan.md Functions rejected": ("src/extra.py", '"""Extra."""\n', "has no section"),
    }
    for name, (rel, text, needle) in cases.items():
        write(c, rel, text)
        rejects(c, name, needle)
        write(c, "src/agent.py", AGENT)
        if (c / "src/extra.py").exists():
            (c / "src/extra.py").unlink()


def planned_functions(c: Path) -> None:
    """T18b: a planned function a later phase adds warns while phases are open, fails once all are ticked."""
    extra = "- `greet(name: str) -> str` · Greet someone · a later phase\n  - in: `name` \"Dev\"\n  - out: \"hi Dev\"\n### `ui/api.py`"
    text = PLAN.format(**GOOD).replace("\n### `ui/api.py`", "\n" + extra, 1)
    write(c, "docs/plan.md", text)
    open_run = check(c)
    write(c, "docs/plan.md", text.replace("- [ ] Phase 2: next", "- [x] Phase 2: next").replace("- [ ] Phase 1", "- [x] Phase 1"))
    done_run = check(c)
    plan(c, tick="x")
    expect("T18b a planned function warns while phases are open, fails once all are ticked",
           open_run.returncode == 0 and "WARN" in open_run.stdout and done_run.returncode == 1 and "greet" in done_run.stdout,
           open_run.stdout + done_run.stdout)


def file_rules(c: Path) -> None:
    """T18c–T18e: plan.md Files + Functions list every file the build writes, with in/out shapes, and ticked phases' files exist."""
    plan(c, tick="x")
    text = (c / "docs/plan.md").read_text()
    write(c, "docs/plan.md", text.replace('  - in: `text` "hi"\n', ""))
    rejects(c, "T18c a function without its in: shape rejected", "needs an '- in:'")
    write(c, "docs/plan.md", text)
    write(c, "scripts/demo.py", '"""Demo."""\n')
    rejects(c, "T18d a code file missing from plan.md Files rejected", "missing from plan.md Files")
    (c / "scripts/demo.py").unlink()
    write(c, "docs/plan.md", text.replace("| `tests/test_phase1.py` | 1 |", "| `tests/test_phase1.py` | 1 |\n| `src/later.py` | 1 | x | x | x |"))
    rejects(c, "T18e a ticked phase's planned file that doesn't exist rejected", "doesn't exist")
    write(c, "docs/plan.md", text)


def doc_rules(c: Path) -> None:
    """T19–T22: docs stay accurate, and kit scaffolding stays out of git."""
    talk = (c / "docs/talk.md").read_text()
    cases = [
        ("T19 a file:line reference in talk.md rejected", "See `src/agent.py:12`.\n", "goes stale"),
        ("T20 talk.md naming a function that doesn't exist rejected", "It calls `send_sms()`.\n", "send_sms"),
        ("T21 a diagram dead end rejected", '```mermaid\nflowchart LR\n  A["a"] -- "x" --> B["b"]\n```\n', "dead end"),
    ]
    for name, extra, needle in cases:
        write(c, "docs/talk.md", talk + extra)
        rejects(c, name, needle)
    write(c, "docs/talk.md", talk)
    shutil.copy(SPEC, c / "scripts" / "spec.py")
    sh("git add scripts/spec.py", c)
    rejects(c, "T22 committed kit scaffolding rejected", "kit scaffolding")
    sh("git rm -q --cached scripts/spec.py && rm scripts/spec.py", c)


def verify_and_hooks(c: Path) -> None:
    """T23–T27: verify prints (no files), screen claims, the Stop hook, the Streamlit path."""
    before = set((c / "docs").rglob("*"))
    write(c, "tests/test_phase1.py", TEST.format(want="bye"))
    bad = sh(f".venv/bin/python {SPEC} verify 1", c)
    write(c, "tests/test_phase1.py", TEST.format(want="hello"))
    good = sh(f".venv/bin/python {SPEC} verify 1", c)
    expect(
        "T23 verify: failing test → VERIFY FAIL, passing → VERIFY OK, and it writes no files",
        bad.returncode == 1 and good.returncode == 0 and "✅ P1.R1" in good.stdout and set((c / "docs").rglob("*")) == before,
        bad.stdout[-300:] + good.stdout[-300:],
    )
    plan(c, tick="x", claim="words the screen never shows")
    run = sh(f".venv/bin/python {SPEC} verify 1", c)
    expect(
        "T24 a Try-it screen claim missing from the screen fails verify + check",
        run.returncode == 1 and check(c).returncode == 1,
        run.stdout[-300:],
    )
    read = "import json;print(json.load(open('.claude/settings.json'))['hooks']['Stop'][0]['hooks'][0]['command'])"
    hook = sh(f'.venv/bin/python -c "{read}"', c).stdout.strip()
    blocked = sh(hook, c, stdin=json.dumps({}))
    plan(c, tick="x")
    passed = sh(hook, c, stdin=json.dumps({}))
    expect(
        "T25 Stop hook (run from the kit) blocks a rule problem, passes once fixed",
        blocked.returncode == 2 and passed.returncode == 0,
        blocked.stderr + passed.stderr,
    )
    write(c, "ui/api.py", API.replace('    return "', '    raise RuntimeError("boom")\n    return "'))
    out = sh(f".venv/bin/python {SPEC} _render", c).stdout
    expect("T26 a crashing ui/api.py shows as APP EXCEPTION", "APP EXCEPTION" in out and "boom" in out, out)
    (c / "ui/api.py").unlink()
    write(
        c,
        "ui/app.py",
        'import streamlit as st\nst.sidebar.markdown("✅ P1: streamlit probe")\nst.tabs(["door", "📊 Owner dashboard"])\n',
    )
    out = sh(f".venv/bin/python {SPEC} _render", c).stdout
    expect("T27 Streamlit mode renders with AppTest", "✅ P1: streamlit probe" in out and "door" in out, out[-300:])
    (c / "ui/app.py").unlink()
    write(c, "ui/api.py", API)


def parser(c: Path) -> None:
    """T28: progress.py reads the plan's Status, requirements, Functions and Flow."""
    code = "import progress as p; print(p.status(), p.requirements(1)[0]['id'], p.interfaces()['src/agent.py'][0]['params'], p.flow())"
    out = sh(f'.venv/bin/python -c "{code}"', c).stdout.strip()
    expect(
        "T28 progress parses Status, requirements, Functions params and Flow",
        out == "approved 2026-01-01 P1.R1 ['text'] [('reply(\"hi\")', 'hello')]",
        out,
    )


def kit_files(c: Path, tmp: Path) -> None:
    """T29–T36: the welcome, /demo, the secrets guard, the talk template, the kit's own code, React, the installer."""
    first, second = (
        sh(f"python3 {KIT}/bin/guide.py setup", c).stdout,
        sh(f"python3 {KIT}/bin/guide.py setup", tmp).stdout,
    )
    status = sh(f"python3 {KIT}/bin/guide.py status", c)
    expect(
        "T29 welcome is fixed (≤ 15 lines, no /rehearse) + status names the next step",
        first == second
        and 0 < len(first.splitlines()) <= 15
        and "/demo" in first
        and "rehearse" not in first
        and "Next    /build" in status.stdout,
        status.stdout + status.stderr,
    )
    sh("git stash -q -u", c)
    seeded, again = sh(f"python3 {KIT}/bin/demo.py seed", c), sh(f"python3 {KIT}/bin/demo.py seed", c)
    expect(
        "T30 /demo seeds empty notes once, then refuses",
        seeded.returncode == 0 and "Spoke & Chain" in (c / "notes/raw.md").read_text() and again.returncode == 1,
        seeded.stdout + again.stdout,
    )
    sh("git checkout -q -- notes/raw.md && git stash pop -q", c)

    env_leak = sh("git add -f .env && git commit -q -m leak", c)
    sh("git reset -q .env", c)
    write(c, "src/leak.py", 'KEY = "' + "AIza" + "B" * 35 + '"\n')
    key_leak = sh("git add src/leak.py && git commit -q -m leak", c)
    sh("git reset -q src/leak.py && rm -f src/leak.py", c)
    clean = sh("git add docs/spec.md && git commit -q -m fine", c)
    expect(
        "T31 pre-commit blocks .env and API keys, allows clean commits",
        env_leak.returncode != 0 and key_leak.returncode != 0 and clean.returncode == 0,
        env_leak.stderr + key_leak.stderr + clean.stderr,
    )

    body = re.search(r"```mermaid\n(.*?)```", (c / "docs/talk.md").read_text(), re.S)[1]
    files = ("ui/api.py", "src/guards.py", "src/agent.py", "src/llm.py", "src/tools.py", "src/data.py", "evals/")
    safe = body.startswith("flowchart LR") and not re.search(r"-\.|<-->|<(?!br/>)[a-z]+>|flowchart TD", body)
    sh(f".venv/bin/python {KIT}/templates/render_docs.py", c)
    page = (c / "docs/talk.html").read_text() if (c / "docs/talk.html").exists() else ""
    ignored = sh("git check-ignore -q docs/talk.html", c).returncode == 0
    expect(
        "T32 talk template: file names, safe mermaid; talk.html renders and is git-ignored",
        all(f in body for f in files) and safe and "mermaid@11.12.2" in page and ignored,
        f"safe={safe} ignored={ignored}",
    )

    kit_py = [
        *KIT.glob("templates/*.py"),
        *KIT.glob("templates/hooks/*.py"),
        *KIT.glob("bin/*.py"),
        KIT / "templates/react/api_template.py",
        Path(__file__),
    ]
    missing = [
        f"{p.name}:{getattr(n, 'name', 'module')}"
        for p in kit_py
        for n in ast.walk(ast.parse(p.read_text()))
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef)) and not ast.get_docstring(n)
    ]
    expect(
        "T33 the kit's own Python follows the coding standards (every file and function documented)",
        not missing,
        str(missing),
    )

    react = KIT / "templates" / "react"
    need = [
        "api_template.py",
        "test_screen_api.py",
        "package.json",
        "vite.config.js",
        "index.html",
        "src/App.jsx",
        "src/main.jsx",
        "src/App.test.jsx",
    ]
    pkg = json.loads((react / "package.json").read_text())
    versions = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    skills = KIT.parent
    expect(
        "T34 React templates complete + pinned, Impeccable runs from the kit, /rehearse gone",
        all((react / n).exists() for n in need)
        and not any(v[:1] in "^~" for v in versions.values())
        and all((KIT / "vendor/impeccable" / f).exists() for f in ("skill/SKILL.md", "LICENSE", "PINNED"))
        and "vendor/impeccable" in (skills / "build" / "SKILL.md").read_text()
        and not (skills / "rehearse").exists()
        and (KIT / "CHEATSHEET.md").exists(),
    )
    node = sh("bash -lc 'node -v' 2>/dev/null", tmp).stdout.strip()
    if re.match(r"v(1[89]|[2-9]\d)\.", node):
        web = tmp / "react-web"
        shutil.copytree(react, web, ignore=shutil.ignore_patterns("*.py", "__pycache__"))
        run = sh("bash -lc 'npm install --no-audit --no-fund --loglevel=error && npm run build && npm test'", web)
        expect(
            f"T35 React template builds + its UI test passes (node {node})",
            run.returncode == 0,
            (run.stdout + run.stderr)[-500:],
        )
    else:
        expect(f"T35 React template build (skipped: node {node or 'missing'} < 18)", True)

    repo = KIT.parents[2]
    if (repo / "install.sh").exists():
        home, names = tmp / "home", ("kickoff", "discovery", "build", "demo")
        inst = sh(f"HOME={home} bash {repo}/install.sh", tmp)
        copied = all((home / ".claude/skills" / s / "SKILL.md").exists() for s in names)
        sh(f"HOME={home} bash {repo}/install.sh --link", tmp)
        linked = all((home / ".claude/skills" / s).is_symlink() for s in names)
        sh(f"HOME={home} bash {repo}/install.sh --uninstall", tmp)
        gone = not any((home / ".claude/skills" / s).exists() for s in names)
        expect(
            "T36 install.sh copies, links and uninstalls the 4 skills",
            copied and linked and gone,
            inst.stdout + inst.stderr,
        )
    else:
        expect("T36 install.sh (skipped: running from an installed copy, not the repo)", True)


def main() -> int:
    """Run every check in a temp classroom; exit 1 if any fails."""
    tmp = Path(tempfile.mkdtemp(prefix="kickoff-selftest-"))
    c = tmp / "classroom"
    c.mkdir()
    print(f"temp classroom: {c}\n")
    setup(c)
    plan_rules(c)
    code_rules(c)
    planned_functions(c)
    file_rules(c)
    doc_rules(c)
    verify_and_hooks(c)
    parser(c)
    kit_files(c, tmp)
    passed = sum(ok for _, ok, _ in results)
    print(f"\n{passed}/{len(results)} passed")
    if "--keep" in sys.argv:
        print(f"kept: {c}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
