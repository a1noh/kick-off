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

## 2. Files
| File | Phase | Job | Takes in | Gives back |
|---|---|---|---|---|
| `src/agent.py` | 1 | brain | a message | the reply |
| `ui/api.py` | 1 | door | — | the screen |
| `tests/test_phase1.py` | 1 | proves P1.R1 | — | — |

## 3. How it works
```mermaid
flowchart LR
  U(["user"])
  API["ui/api.py<br/>door"]
  AG["src/agent.py<br/>brain"]

  U -- "1 hi" --> API
  API -- "2 hi" --> AG
  AG -- "3 hello" --> U
```

## 4. Functions

### `src/agent.py` — brain: replies

#### `reply` — answer a message
Reply to one message.

**In** · the arguments, by name
```jsonc
{{
  "text": "hi"  // str · the message
}}
```

**Out** · `str`
```text
hello
```

<details><summary>How it does it: signature, why, steps</summary>

`reply(text: str) -> str`

**Why** probe.

**Does**
1. Returns "hello" for any message.

</details>

### `ui/api.py` — door

#### `screen_text` — the screen as text
The screen as text.

`screen_text() -> str`

**Does**
1. Returns the screen as lines of text.

**In** · the arguments, by name
```jsonc
{{}}
```

**Out** · `str`
```text
[tabs] door | …
```

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

STORY = '\n**Phase {n} · probe** · Was broken: nothing · Fixed by: `reply()` · Say it: "it replies"\n'
REQ2 = (
    '    - **P1.R2** · bye\n      - Traces to: B2 · user 2026-01-02: "say bye too"\n'
    '      - Acceptance: input `bye` → reply "hello"\n      - Test: tests/test_phase1.py::test_r2_bye\n'
)
PHASE = (
    "- [{tick}] Phase {n}: {name}\n  - **On screen (before → after):** same → same\n  - **Requirements:**\n"
    "    - **P{n}.R1** · {name}\n      - Traces to: {rule} · raw.md:L9\n"
    '      - Acceptance: input `yo` → reply "hello"\n      - Test: tests/test_phase{n}.py::test_r1_{name}\n'
)
PHASE_TEST = 'from agent import reply\n\n\ndef test_r1_{name}():\n    """plan.md P{n}.R1: yo -> hello."""\n    assert reply("yo") == "hello"\n'


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
    rejects(c, "T12b ticked phase with no Build-story entry in talk.md rejected", "no Build-story entry")
    write(c, "docs/talk.md", (c / "docs/talk.md").read_text() + STORY.format(n=1))
    expect("T13 approved + ticked + tested + story told + on screen → SPEC OK", check(c).returncode == 0, check(c).stdout)


def code_rules(c: Path) -> None:
    """T14–T18: the coding standards, enforced on src/ and ui/*.py."""
    cases = {
        "T14 file without a docstring rejected": ("src/agent.py", AGENT.split("\n", 1)[1], "no docstring"),
        "T15 function without a docstring rejected": (
            "src/agent.py",
            AGENT.replace('    """Reply to one message."""\n', ""),
            "has no docstring",
        ),
        "T16 plan.md function parameters that differ from the code rejected": (
            "src/agent.py",
            AGENT.replace("text: str", "message: str"),
            "takes",
        ),
        "T17 a plan.md function line that differs from docstring line 1 rejected": (
            "src/agent.py",
            AGENT.replace("Reply to one message.", "Answer."),
            "must match",
        ),
        "T18 a src/ file with no function explained in plan.md rejected": (
            "src/extra.py",
            '"""Extra."""\n',
            "no function of it is explained",
        ),
    }
    for name, (rel, text, needle) in cases.items():
        write(c, rel, text)
        rejects(c, name, needle)
        write(c, "src/agent.py", AGENT)
        if (c / "src/extra.py").exists():
            (c / "src/extra.py").unlink()


def planned_functions(c: Path) -> None:
    """T18b: a planned function a later phase adds warns while phases are open, fails once all are ticked."""
    extra = (
        "#### `greet` — say hi\nGreet someone.\n\n`greet(name: str) -> str`\n\n**Does**\n1. Says hi.\n\n"
        '**In** · the arguments, by name\n```jsonc\n{\n  "name": "Dev"  // str · who to greet\n}\n```\n\n**Out** · `str`\n```text\nhi Dev\n```\n\n'
    )
    text = PLAN.format(**GOOD).replace("### `ui/api.py` — door\n", extra + "### `ui/api.py` — door\n", 1)
    write(c, "docs/plan.md", text)
    open_run = check(c)
    write(
        c,
        "docs/plan.md",
        text.replace("- [ ] Phase 2: next", "- [x] Phase 2: next").replace("- [ ] Phase 1", "- [x] Phase 1"),
    )
    done_run = check(c)
    plan(c, tick="x")
    expect(
        "T18b a planned function warns while phases are open, fails once all are ticked",
        open_run.returncode == 0
        and "WARN" in open_run.stdout
        and done_run.returncode == 1
        and "greet" in done_run.stdout,
        open_run.stdout + done_run.stdout,
    )


def file_rules(c: Path) -> None:
    """T18c–T18e: plan.md Files + How it works list every file the build writes, each function with its In and Out, and ticked phases' files exist."""
    plan(c, tick="x")
    text = (c / "docs/plan.md").read_text()
    in_block = '**In** · the arguments, by name\n```jsonc\n{\n  "text": "hi"  // str · the message\n}\n```\n\n'
    write(c, "docs/plan.md", text.replace(in_block, "", 1))
    rejects(c, "T18c a function without its In block rejected", "needs an **In**")
    write(c, "docs/plan.md", text.replace('"text": "hi"  // str · the message', '"text": "hi"  // int · the message', 1))
    rejects(c, "T18g an In comment whose type differs from the signature rejected", "needs the comment `// str")
    write(c, "docs/plan.md", text.replace("**Why** probe.", "**Why** reads out/<name>.jsonl.", 1))
    rejects(c, "T18h a bare <tag> that markdown would hide rejected", "outside backticks")
    write(c, "docs/plan.md", text.replace("**Does**\n1. Returns \"hello\" for any message.\n\n", "", 1))
    rejects(c, "T18f a function without its Does steps rejected", "needs a **Does** list")
    write(c, "docs/plan.md", text.replace('API -- "2 hi" --> AG', 'API -- "5 hi" --> AG'))
    rejects(c, "T18j the diagram's request arrows must be numbered 1, 2, 3, … in order", "number the request's arrows")
    write(c, "docs/plan.md", text)
    write(c, "scripts/demo.py", '"""Demo."""\n')
    rejects(c, "T18d a code file missing from plan.md Files rejected", "missing from plan.md Files")
    (c / "scripts/demo.py").unlink()
    write(
        c,
        "docs/plan.md",
        text.replace(
            "| `tests/test_phase1.py` | 1 |", "| `tests/test_phase1.py` | 1 |\n| `src/later.py` | 1 | x | x | x |"
        ),
    )
    rejects(c, "T18e a ticked phase's planned file that doesn't exist rejected", "doesn't exist")
    write(c, "docs/plan.md", text)


def doc_rules(c: Path) -> None:
    """T19–T22: docs stay accurate, and kit scaffolding stays out of git."""
    talk = (c / "docs/talk.md").read_text()
    cases = [
        ("T19 a file:line reference in talk.md rejected", "See `src/agent.py:12`.\n", "goes stale"),
        ("T20 talk.md naming a function that doesn't exist rejected", "It calls `send_sms()`.\n", "send_sms"),
        ("T21b a ```json block in plan.md that isn't pretty-printed rejected", None, "pretty-print"),
        ("T21 a diagram dead end rejected", '```mermaid\nflowchart LR\n  A["a"] -- "x" --> B["b"]\n```\n', "dead end"),
    ]
    for name, extra, needle in cases:
        if extra is None:  # a plan.md rule: one-line JSON in the Out block
            plan_text = (c / "docs/plan.md").read_text()
            write(c, "docs/plan.md", plan_text + '\n**Out**\n```json\n{"a": 1, "b": 2}\n```\n')
            rejects(c, name, needle)
            write(c, "docs/plan.md", plan_text)
            continue
        write(c, "docs/talk.md", talk + extra)
        rejects(c, name, needle)
    write(c, "docs/talk.md", talk)
    plan_text = (c / "docs/plan.md").read_text()
    write(c, "docs/plan.md", plan_text + '\n**In**\n```json\n{\n  "store": "Store(out)"\n}\n```\n')
    rejects(c, "T21c code written as text inside a plan JSON value rejected", "is code, not data")
    write(c, "docs/plan.md", plan_text)
    shutil.copy(SPEC, c / "scripts" / "spec.py")
    sh("git add scripts/spec.py", c)
    rejects(c, "T22 committed kit scaffolding rejected", "kit scaffolding")
    sh("git rm -q --cached scripts/spec.py && rm scripts/spec.py", c)


def verify_and_hooks(c: Path) -> None:
    """T23–T27: verify prints (no files), screen claims, the Stop hook, a crashing screen, the architecture match."""
    before = set((c / "docs").rglob("*"))
    write(c, "tests/test_phase1.py", TEST.format(want="bye"))
    bad = sh(f".venv/bin/python {SPEC} verify 1", c)
    write(c, "tests/test_phase1.py", TEST.format(want="hello"))
    good = sh(f".venv/bin/python {SPEC} verify 1", c)
    expect(
        "T23 verify: failing test → VERIFY FAIL, passing → VERIFY OK, and it writes no files",
        bad.returncode == 1
        and good.returncode == 0
        and "✅ P1.R1" in good.stdout
        and set((c / "docs").rglob("*")) == before,
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
    write(c, "ui/api.py", API)
    text = (c / "docs/plan.md").read_text()
    write(c, "docs/plan.md", text.replace('  AG["src/agent.py<br/>brain"]\n', '  AG["src/brain.py<br/>brain"]\n'))
    run = check(c)
    expect(
        "T27 the architecture matches plan.md Files: a missing box and a box for an unlisted file are both rejected",
        run.returncode == 1 and "no box for src/agent.py" in run.stdout and "a box for src/brain.py" in run.stdout,
        run.stdout,
    )
    write(c, "docs/plan.md", text)


def parser(c: Path) -> None:
    """T28: progress.py reads the plan's Status, requirements and function blocks (Does, In, Out)."""
    code = (
        "import progress as p; f = p.interfaces()['src/agent.py'][0]; print(p.status(), p.requirements(1)[0]['id'],"
        " f['does'], f['in'], f['in_notes'], f['out'], f['out_type'], sorted(p.interfaces()))"
    )
    out = sh(f'.venv/bin/python -c "{code}"', c).stdout.strip()
    want = "approved 2026-01-01 P1.R1 ['Returns \"hello\" for any message.'] {'text': 'hi'} {'text': 'str · the message'} hello str ['src/agent.py', 'ui/api.py']"
    expect("T28 progress parses Status, requirements and function blocks (Does, In, Out)", out == want, out)


def changes(c: Path) -> None:
    """T28b: spec.py changes N lists the functions a phase added (vs. the previous tag), and only those."""
    sh("git add -A && git commit -qm base && git tag -f plan", c)
    write(c, "src/agent.py", AGENT + '\n\ndef extra() -> str:\n    """An extra function."""\n    return "x"\n')
    sh("git add -A && git commit -qm p1 && git tag -f phase-1", c)
    out = sh(f".venv/bin/python {SPEC} changes 1", c).stdout
    added = out.split("🔜")[0]
    expect("T28b spec.py changes N lists what the phase added, not what was already there",
           "+ extra" in added and "reply" not in added and "🔜" in out, out)
    write(c, "src/agent.py", AGENT)
    sh("git add -A && git commit -qm restore", c)


def amend(c: Path, rel: str, old: str, new: str) -> None:
    """Replace old with new once in a classroom file (old must be there)."""
    text = (c / rel).read_text()
    assert old in text, f"{rel}: no {old!r}"
    write(c, rel, text.replace(old, new, 1))


def new_phase(c: Path, n: int, name: str, rule: str, before: str) -> None:
    """Add rule to spec.md and an unticked phase n (one requirement tracing to it, its test file in Files) before a plan line."""
    amend(c, "docs/spec.md", "- **B1**", f"- **{rule}** {name} back · raw.md:L9\n- **B1**")
    amend(c, "docs/plan.md", before, PHASE.format(tick=" ", n=n, name=name, rule=rule) + before.replace("- [ ] Phase 2: next\n", ""))
    row = "| `tests/test_phase1.py` | 1 | proves P1.R1 | — | — |\n"
    amend(c, "docs/plan.md", row, row + f"| `tests/test_phase{n}.py` | {n} | proves P{n}.R1 | — | — |\n")


def build_phase(c: Path, n: int, name: str) -> None:
    """What /build leaves behind for phase n, minus the docs: an approved plan, the test, the tick."""
    amend(c, "docs/plan.md", "**Status:** draft", "**Status:** approved 2026-01-03")
    write(c, f"tests/test_phase{n}.py", PHASE_TEST.format(n=n, name=name))
    amend(c, "docs/plan.md", f"- [ ] Phase {n}:", f"- [x] Phase {n}:")


def mid_build(c: Path) -> None:
    """M1–M12: a tweak, a feature folded into an unbuilt phase, and a phase added after everything was built keep the three docs in step."""
    start = sh("git add -A && git commit -qm before-scenarios; git rev-parse HEAD", c).stdout.split()[-1]
    plan(c, tick="x")
    command = '.venv/bin/python -c "import progress as p; print(p.status(), p.next_command())"'

    # scenario 1: a small tweak, told to /build
    amend(c, "docs/spec.md", "- **B1**", "- **B2** say bye back · decided with user 2026-01-02\n- **B1**")
    rejects(c, "M1 tweak: a new spec.md rule with no requirement is rejected", "B2: no requirement")
    amend(c, "docs/plan.md", "- [ ] Phase 2: next", REQ2 + "- [ ] Phase 2: next")
    rejects(c, "M2 tweak: the new requirement's test must exist before the phase stays ticked", "test_r2_bye does not exist")
    amend(c, "tests/test_phase1.py", "hello\"\n", 'hello"\n\n\ndef test_r2_bye():\n    """plan.md P1.R2: bye -> hello."""\n    assert reply("bye") == "hello"\n')
    expect("M3 tweak: rule + requirement + test → SPEC OK", check(c).returncode == 0, check(c).stdout)
    out = sh(f".venv/bin/python {SPEC} changes 1", c).stdout
    expect("M4 tweak: the handover's 📚 Docs lines name what each doc gained", "+ B2" in out and "P1.R2" in out and "📚" in out, out)

    amend(c, "docs/plan.md", '1. Returns "hello" for any message.', '1. Returns "hello" for any message, bye included (B2).')
    out = sh(f".venv/bin/python {SPEC} changes 1", c).stdout
    expect("M4b tweak: a reworded function block shows as changed (~)", "~ reply" in out and "~ screen_text" not in out, out)

    # scenario 2: a real feature mid-build (/discovery re-run), folded into the phase not built yet
    new_phase(c, 2, "wave", "B3", "- [ ] Phase 2: next\n")
    amend(c, "docs/plan.md", "**Status:** approved 2026-01-01", "**Status:** draft")
    state = sh(command, c).stdout.strip()
    expect("M5 feature: a re-run's draft keeps the built, tagged phase ticked and /build is next", check(c).returncode == 0 and state == "draft /build", check(c).stdout + state)
    sh("git tag -d phase-1", c)
    rejects(c, "M6 feature: a phase ticked under a draft with no phase tag is still rejected", "not approved")
    sh("git tag -f phase-1", c)
    build_phase(c, 2, "wave")
    rejects(c, "M7 feature: the built phase needs its Build-story entry", "phase 2 is ticked but has no Build-story entry")
    write(c, "docs/talk.md", (c / "docs/talk.md").read_text() + STORY.format(n=2))
    rejects(c, "M8 last phase: talk.md must cover every phase", "phases 1–2")
    amend(c, "docs/talk.md", "**Covers:** nothing built yet", "**Covers:** phases 1–2")
    rejects(c, "M9 last phase: the Likely questions must be answered", "Likely questions")
    write(c, "docs/plan.md", (c / "docs/plan.md").read_text() + "\n## 8. Likely questions\n**Covers:** phases 1–2\n\n- **Why no AI?** It only greets (`reply()`).\n")
    expect("M10 everything built, three docs in step → SPEC OK, All built", check(c).returncode == 0 and "All built" in sh(command, c).stdout, check(c).stdout)
    sh("git add -A && git commit -qm p2 && git tag -f phase-2", c)

    # scenario 3: a feature after everything is built becomes the next phase
    new_phase(c, 3, "nod", "B4", "\n## 8. Likely questions")
    amend(c, "docs/plan.md", "**Status:** approved 2026-01-03", "**Status:** draft")
    state = sh(command, c).stdout.strip()
    expect("M11 new phase after all built: plan is valid as a draft, /build is next, talk still covers what is built", check(c).returncode == 0 and state == "draft /build", check(c).stdout + state)
    amend(c, "docs/plan.md", "`reply(text: str) -> str`", "`reply(text: str, loud: bool) -> str`")
    amend(c, "docs/plan.md", '  "text": "hi"  // str · the message\n', '  "text": "hi",  // str · the message\n  "loud": true  // bool · shout it\n')
    rejects(c, "M11b a built function whose plan signature changed, with no phase saying so, is rejected", "but the code takes (text)")
    amend(c, "docs/plan.md", "- [ ] Phase 3: nod\n", "- [ ] Phase 3: nod\n  - **Builds:** changes `reply`\n")
    run = check(c)
    expect("M11c the unbuilt phase says it changes that function → a warning until the phase is built", run.returncode == 0 and "WARN src/agent.py: plan.md: reply(text, loud)" in run.stdout, run.stdout)
    amend(c, "docs/plan.md", "`reply(text: str, loud: bool) -> str`", "`reply(text: str) -> str`")
    amend(c, "docs/plan.md", '  "text": "hi",  // str · the message\n  "loud": true  // bool · shout it\n', '  "text": "hi"  // str · the message\n')
    build_phase(c, 3, "nod")
    write(c, "docs/talk.md", (c / "docs/talk.md").read_text() + STORY.format(n=3))
    rejects(c, "M12 new phase built: a talk.md that still covers phases 1–2 is rejected", "phases 1–3")
    amend(c, "docs/talk.md", "**Covers:** phases 1–2", "**Covers:** phases 1–3")
    rejects(c, "M12b new phase built: Likely questions that still cover phases 1–2 are rejected", "answer them for all 3 phases")
    amend(c, "docs/plan.md", "**Covers:** phases 1–2", "**Covers:** phases 1–3")
    verify = sh(f".venv/bin/python {SPEC} verify 3", c).stdout
    out = sh(f".venv/bin/python {SPEC} changes 3", c).stdout
    expect("M13 new phase built and told → SPEC OK, VERIFY OK, 📚 names B4, Phase 3 and its entry",
           check(c).returncode == 0 and "VERIFY OK" in verify and "+ B4" in out and "+ Phase 3, + P3.R1" in out and "nothing, every phase is built" in out,
           check(c).stdout + verify + out)
    amend(c, "docs/talk.md", "Fixed by: `reply()`", "Fixed by: the greeter")
    amend(c, "docs/talk.md", "Fixed by: `reply()`", "Fixed by: the greeter")
    amend(c, "docs/talk.md", "Fixed by: `reply()`", "Fixed by: the greeter")
    amend(c, "docs/plan.md", "It only greets (`reply()`).", "It only greets.")
    run = check(c)
    expect("M14 a function the client docs never name is a warning, not a failure", run.returncode == 0 and "WARN reply() is in plan.md Functions but never named" in run.stdout, run.stdout)
    sh(f"git add -A && git commit -qm scenarios; git reset -q --hard {start}; git tag -d phase-2", c)


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
    bike_ok = "Spoke & Chain" in (c / "notes/raw.md").read_text()
    sh("git checkout -q -- notes/raw.md", c)
    other, unknown = sh(f"python3 {KIT}/bin/demo.py seed maintenance", c), sh(f"python3 {KIT}/bin/demo.py seed nope", c)
    expect(
        "T30 /demo seeds empty notes once (bike by default, or a named sample), then refuses",
        seeded.returncode == 0
        and bike_ok
        and again.returncode == 1
        and other.returncode == 0
        and "Greenleaf" in (c / "notes/raw.md").read_text()
        and "NO SUCH SAMPLE" in unknown.stdout,
        seeded.stdout + again.stdout + other.stdout + unknown.stdout,
    )
    sh("git checkout -q -- notes/raw.md && git stash pop -q", c)

    env_leak = sh("git add -f .env && git commit -q -m leak", c)
    sh("git reset -q .env", c)
    write(c, "src/leak.py", 'KEY = "' + "AIza" + "B" * 35 + '"\n')
    key_leak = sh("git add src/leak.py && git commit -q -m leak", c)
    sh("git reset -q src/leak.py && rm -f src/leak.py", c)
    clean = sh("git add docs/spec.md && git commit -q --allow-empty -m fine", c)
    expect(
        "T31 pre-commit blocks .env and API keys, allows clean commits",
        env_leak.returncode != 0 and key_leak.returncode != 0 and clean.returncode == 0,
        env_leak.stderr + key_leak.stderr + clean.stderr,
    )

    talk = (c / "docs/talk.md").read_text()
    expect(
        "T32 talk template has no fixed diagram (phase 4 copies the plan's), and no kit file is left behind",
        "```mermaid" not in talk and not (KIT / "templates/render_docs.py").exists()
        and not list(KIT.parent.glob("discovery/templates/architecture*.md")) and not (KIT / "vendor").exists(),
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
        "T34 React templates complete + pinned, /rehearse gone",
        all((react / n).exists() for n in need)
        and not any(v[:1] in "^~" for v in versions.values())
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
    changes(c)
    mid_build(c)
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
