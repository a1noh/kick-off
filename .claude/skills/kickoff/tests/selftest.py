"""Kit self-test: proves /kickoff builds a working, spec-enforcing classroom. ~1 minute, no network except uv's cache.

  python3 ~/.claude/skills/kickoff/tests/selftest.py          (add --keep to leave the temp classroom for a look)

It extracts the REAL setup + verify blocks from ../SKILL.md (so it tests what /kickoff runs), runs them in a temp
folder, then plants good and broken specs and checks that scripts/spec.py and the Stop hook react correctly.
"""

from __future__ import annotations

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
results: list[tuple[str, bool, str]] = []


def block(title: str, fence: str) -> str:
    m = re.search(rf"^## {re.escape(title)}\b.*?\n{fence}bash\n(.*?)\n{fence}\n", SKILL, re.M | re.S)
    assert m, f"no '{title}' block in SKILL.md"
    return m[1]


def sh(cmd: str, cwd: Path, stdin: str = "") -> subprocess.CompletedProcess:
    env = {
        **{k: v for k, v in os.environ.items() if k != "__PYVENV_LAUNCHER__"},
        "CLAUDE_PROJECT_DIR": str(cwd),
        "DEST": str(cwd),
        "KIT_HOME": str(KIT),
    }
    return subprocess.run(["bash", "-c", cmd], cwd=cwd, input=stdin, capture_output=True, text=True, env=env)


def expect(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"{'✅' if ok else '❌'} {name}" + (f"  · {detail[:300]}" if detail and not ok else ""))


def spec_check(c: Path) -> subprocess.CompletedProcess:
    return sh(".venv/bin/python scripts/spec.py check", c)


def write(c: Path, rel: str, text: str) -> None:
    (c / rel).parent.mkdir(parents=True, exist_ok=True)
    (c / rel).write_text(text)


GOOD_SPEC = """# Phase 1 · probe · spec
## Requirements
### R1 · greeting
- Traces to: plan.md §6 Phase 1 Try it 1 · raw.md:L3
- Acceptance: input `hi` → reply "hello"
- Test: tests/test_phase1.py::test_r1_greeting
## Assumptions
- none
"""
APP = 'import streamlit as st\nst.sidebar.markdown("✅ P1: probe")\nst.tabs(["door", "📊 Owner dashboard"])\n'
TEST_OK = "def test_r1_greeting():\n    assert 'hello' == 'hello'\n"
TEST_BAD = "def test_r1_greeting():\n    assert 'hello' == 'bye'\n"


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="kickoff-selftest-"))
    c = tmp / "classroom"
    c.mkdir()
    print(f"temp classroom: {c}\n")

    # 1. setup + verify blocks, exactly as /kickoff runs them
    r = sh(block("Setup block", "````"), c)
    expect("T1 setup block runs (SETUP OK)", "SETUP OK" in r.stdout, r.stderr[-300:])
    r = sh(block("Verify block", "```"), c)
    oks = re.findall(r"^OK \d/6", r.stdout, re.M)
    expect("T2 verify block: all 6 checks OK", len(oks) == 6, r.stdout + r.stderr)
    expect(
        "T3 spec kit installed (spec.py, template, hook calls spec check)",
        (c / "scripts/spec.py").exists()
        and (c / "docs/specs/_template/spec.md").exists()
        and "spec.py check" in (c / ".claude/hooks/run_tests.sh").read_text(),
    )
    expect("T4 fresh classroom passes spec check", spec_check(c).returncode == 0, spec_check(c).stdout)

    # 2. a plan with phase 1 in progress
    write(c, "docs/plan.md", "# Plan\n## 6. Phases\n- [ ] Phase 1: probe\n- [ ] Phase 2: next\n")
    write(c, "ui/app.py", APP)
    write(c, "tests/test_phase1.py", TEST_OK)
    write(c, "docs/specs/phase-1/spec.md", GOOD_SPEC)
    expect("T5 good spec, phase not ticked yet → OK", spec_check(c).returncode == 0, spec_check(c).stdout)

    bad_cases = {
        "T6 untraced requirement rejected": (
            GOOD_SPEC.replace("plan.md §6 Phase 1 Try it 1 · raw.md:L3", "my intuition"),
            "Traces to",
        ),
        "T7 acceptance without a quoted value rejected": (GOOD_SPEC.replace('reply "hello"', "it works"), "quotes"),
        "T8 test that doesn't exist rejected": (
            GOOD_SPEC.replace("test_r1_greeting", "test_r1_missing"),
            "does not exist",
        ),
        "T9 open assumption rejected": (GOOD_SPEC.replace("- none", "- cancel needs a yes"), "open assumption"),
    }
    for name, (text, needle) in bad_cases.items():
        write(c, "docs/specs/phase-1/spec.md", text)
        r = spec_check(c)
        expect(name, r.returncode == 1 and needle in r.stdout, r.stdout)
    write(c, "docs/specs/phase-1/spec.md", GOOD_SPEC)

    # 3. ticking demands proof
    write(c, "docs/plan.md", "# Plan\n## 6. Phases\n- [x] Phase 1: probe\n- [ ] Phase 2: next\n")
    r = spec_check(c)
    expect("T10 ticked phase without verify.md rejected", r.returncode == 1 and "no verify.md" in r.stdout, r.stdout)
    write(c, "tests/test_phase1.py", TEST_BAD)
    r = sh(".venv/bin/python scripts/spec.py verify 1", c)
    r2 = spec_check(c)
    expect(
        "T11 failing test → VERIFY FAIL and check rejects",
        r.returncode == 1 and "not passing" in r2.stdout,
        r.stdout[-300:],
    )
    write(c, "tests/test_phase1.py", TEST_OK)
    r = sh(".venv/bin/python scripts/spec.py verify 1", c)
    verify = (c / "docs/specs/phase-1/verify.md").read_text() if (c / "docs/specs/phase-1/verify.md").exists() else ""
    expect(
        "T12 passing → VERIFY OK, proof has the rendered screen",
        r.returncode == 0 and "✅ P1: probe" in verify and "📊 Owner dashboard" in verify,
        r.stdout[-400:],
    )
    expect(
        "T13 proof passes spec check + README index written",
        spec_check(c).returncode == 0 and (c / "docs/specs/README.md").exists(),
        spec_check(c).stdout,
    )
    os.utime(c / "docs/specs/phase-1/spec.md")  # spec edited after the proof
    r = spec_check(c)
    expect(
        "T14 spec edited after proof → stale proof rejected", r.returncode == 1 and "older than" in r.stdout, r.stdout
    )

    # 4. the Stop hook enforces it (exit 2 = Claude may not stop)
    hook = sh(".claude/hooks/run_tests.sh", c, stdin=json.dumps({}))
    expect("T15 Stop hook blocks on an unverified spec", hook.returncode == 2 and "Specs" in hook.stderr, hook.stderr)
    sh(".venv/bin/python scripts/spec.py verify 1", c)
    hook = sh(".claude/hooks/run_tests.sh", c, stdin=json.dumps({}))
    expect("T16 Stop hook passes once verified", hook.returncode == 0, hook.stderr)

    # 5. an older classroom upgrades in place
    (c / "scripts/spec.py").unlink()
    r = sh(block("Upgrade block", "```"), c)
    expect(
        "T17 upgrade block restores the spec kit",
        "UPGRADE OK" in r.stdout and (c / "scripts/spec.py").exists(),
        r.stderr,
    )

    # 6. React mode: the proof renders api.screen_text() instead of AppTest; the Streamlit path is unchanged
    render = lambda: sh(".venv/bin/python scripts/spec.py _render", c).stdout  # noqa: E731
    write(
        c,
        "ui/api.py",
        'def screen_text():\n    return "[tabs] door | 📊 Owner dashboard\\n[sidebar]\\n✅ P1: react probe"\n',
    )
    out = render()
    expect("T18 React mode: proof renders api.screen_text()", "✅ P1: react probe" in out and "door" in out, out[-300:])
    write(c, "ui/api.py", "def screen_text():\n    raise RuntimeError('boom')\n")
    out = render()
    expect("T19 React mode: a crashing api.py shows as APP EXCEPTION", "APP EXCEPTION" in out and "boom" in out, out)
    (c / "ui/api.py").unlink()
    out = render()
    expect("T20 Streamlit mode unchanged (AppTest render)", "✅ P1: probe" in out and "react" not in out, out[-300:])
    react = KIT / "templates" / "react"
    need = ["api_template.py", "test_screen_api.py", "package.json", "vite.config.js", "index.html", "src/App.jsx"]
    need += ["src/main.jsx", "src/App.test.jsx", "src/styles.css"]
    need += [f"src/components/{n}.jsx" for n in ("Chat", "Panel", "Sidebar")]
    pkg = json.loads((react / "package.json").read_text()) if (react / "package.json").exists() else {}
    versions = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    skills = KIT.parent
    mentions = all(re.search(r"UI:\**\s*react", (skills / s / "SKILL.md").read_text()) for s in ("discovery", "build"))
    mentions = mentions and "Impeccable" in (skills / "build" / "SKILL.md").read_text()
    compiled = sh(f"python3 -m py_compile {react / 'api_template.py'}", c).returncode == 0
    missing = [n for n in need if not (react / n).exists()]
    pinned = bool(versions) and not any(v[:1] in "^~" for v in versions.values())
    expect(
        "T21 React templates complete + pinned, skills name the UI mode",
        not missing and pinned and mentions and compiled and (KIT / "templates" / "progress.py").exists()
        and all((KIT / f).exists() for f in ("bin/guide.py", "bin/demo.py", "demo/brief.md", "templates/pre-commit"))
        and (skills / "demo" / "SKILL.md").exists(),
        f"missing={missing} pinned={pinned} mentions={mentions} compiled={compiled}",
    )

    # 7. src/ + ui/ layout, the fixed start, /demo, the secrets guard, the installer
    write(c, "src/zz_mod.py", "X = 1\n")
    write(c, "ui/zz_ui.py", "Y = 2\n")
    r = sh(f"{c}/.venv/bin/python -c 'import zz_mod, zz_ui; print(zz_mod.X + zz_ui.Y)'", tmp)  # from another folder
    expect("T22 src/ + ui/ importable anywhere (classroom.pth)", r.stdout.strip() == "3" and (c / "ui/progress.py").exists(), r.stderr)
    (c / "src/zz_mod.py").unlink()
    (c / "ui/zz_ui.py").unlink()

    g1, g2 = sh(f"python3 {KIT}/bin/guide.py setup", c).stdout, sh(f"python3 {KIT}/bin/guide.py setup", tmp).stdout
    st = sh(f"python3 {KIT}/bin/guide.py status", c)
    expect(
        "T23 welcome is fixed (same text anywhere, ≤ 15 lines) + status names the next command",
        g1 == g2 and 0 < len(g1.splitlines()) <= 15 and "/demo" in g1 and st.returncode == 0 and "Next    /build" in st.stdout,
        st.stdout + st.stderr,
    )

    first = sh(f"python3 {KIT}/bin/demo.py seed", c)
    second = sh(f"python3 {KIT}/bin/demo.py seed", c)
    expect(
        "T24 /demo seeds empty notes once, then refuses",
        first.returncode == 0 and "Spoke & Chain" in (c / "notes/raw.md").read_text() and second.returncode == 1,
        first.stdout + second.stdout,
    )
    sh("git checkout -q -- notes/raw.md && rm -f .kickoff-demo", c)

    blocked_env = sh("git add -f .env && git commit -q -m leak", c)
    sh("git reset -q .env", c)
    write(c, "src/leak.py", 'KEY = "' + "AIza" + "B" * 35 + '"\n')
    blocked_key = sh("git add src/leak.py && git commit -q -m leak", c)
    sh("git reset -q src/leak.py && rm -f src/leak.py", c)
    write(c, "src/fine.py", "X = 1\n")
    clean = sh("git add src/fine.py && git commit -q -m fine", c)
    expect(
        "T25 pre-commit blocks .env and API keys, allows clean commits",
        blocked_env.returncode != 0 and "BLOCKED" in blocked_env.stderr and blocked_key.returncode != 0 and clean.returncode == 0,
        blocked_env.stderr + blocked_key.stderr + clean.stderr,
    )

    talk = (c / "docs/talk.md").read_text()
    diagram = re.search(r"```mermaid\n(.*?)```", talk, re.S)
    body = diagram[1] if diagram else ""
    files = ("ui/app.py", "src/guards.py", "src/agent.py", "src/llm.py", "src/tools.py", "src/data.py", "evals/")
    safe = body.startswith("flowchart LR") and not re.search(r"-\.|<-->|<(?!br/>)[a-z]+>|flowchart TD", body)
    page = (c / "docs/talk.html").read_text() if (c / "docs/talk.html").exists() else ""
    expect(
        "T27 talk.md has the architecture diagram (file names, safe mermaid) + talk.html renders it",
        all(f in body for f in files) and safe and "mermaid@11.12.2" in page and "marked@15.0.7" in page
        and "src/agent.py" in page and (c / "scripts/render_docs.py").exists(),
        f"files={[f for f in files if f not in body]} safe={safe} html={bool(page)}",
    )

    repo = KIT.parents[2]
    if (repo / "install.sh").exists():
        home = tmp / "home"
        names = ("kickoff", "discovery", "build", "rehearse", "demo")
        inst = sh(f"HOME={home} bash {repo}/install.sh", tmp)
        copied = all((home / ".claude/skills" / s / "SKILL.md").exists() for s in names)
        sh(f"HOME={home} bash {repo}/install.sh --link", tmp)
        linked = all((home / ".claude/skills" / s).is_symlink() for s in names)
        sh(f"HOME={home} bash {repo}/install.sh --uninstall", tmp)
        gone = not any((home / ".claude/skills" / s).exists() for s in names)
        expect("T26 install.sh copies, links and uninstalls the 5 skills", copied and linked and gone, inst.stdout + inst.stderr)
    else:
        expect("T26 install.sh (skipped: running from an installed copy, not the repo)", True)

    passed = sum(ok for _, ok, _ in results)
    print(f"\n{passed}/{len(results)} passed")
    if "--keep" in sys.argv:
        print(f"kept: {c}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
