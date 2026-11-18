#!/usr/bin/env python3
"""What /kickoff shows, printed by code so it is the same every time (Claude shows it verbatim).

  python3 guide.py setup     the short welcome after a fresh setup (fixed text)
  python3 guide.py status    "where you are" in the current classroom (computed, read-only)
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT / "templates"))
import progress  # noqa: E402  (the kit's one plan parser)

SETUP = f"""\
✅ Kickoff ready · a 2-hour build in 4 visible steps

You interview → plan → build → present. The app comes first: every scenario starts ⬜ and turns ✅ step by step.

  1  Key    paste your Gemini key into .env → check: .venv/bin/python {KIT}/templates/check_llm.py
  2  0:00   interview with GUIDES → write it in notes/raw.md (Goal · Users · Inputs · Happy path · Danger · Edges · Scale)
  3  0:10   /discovery → docs/spec.md + docs/plan.md → read the files, diagram + functions, approve it
  4  0:15   /build ×4 → after each step do its "Try it" list in the app, then /build again
  5  1:40   code freeze → scripts/demo.py, then read docs/talk.md with the app open

New here? /demo fills in a sample interview and runs discovery up to the approved plan, explaining each step.
Lost? /kickoff shows where you are. Everything else: {KIT}/CHEATSHEET.md"""

CLOCK = {"discovery": "0:10–0:15", 1: "0:15–0:25", 2: "0:25–0:50", 3: "0:50–1:15", 4: "1:15–1:30", "present": "1:40–1:55"}


def notes_written(root: Path) -> int:
    """Lines the user added below the template's '---' in notes/raw.md (0 = still empty)."""
    path = root / "notes" / "raw.md"
    if not path.exists():
        return 0
    body = path.read_text().split("\n---\n", 1)
    return len([x for x in (body[1] if len(body) == 2 else "").splitlines() if x.strip()])


def venv_run(root: Path, code: list[str]) -> str:
    """Run python code with the project's venv in the project folder; its output, or '' without a venv."""
    py = root / ".venv" / "bin" / "python"
    if not py.exists():
        return ""
    env = {k: v for k, v in os.environ.items() if k != "__PYVENV_LAUNCHER__"}
    r = subprocess.run([str(py), *code], cwd=root, capture_output=True, text=True, env=env, timeout=120)
    return (r.stdout or r.stderr).strip()


def board(root: Path) -> str:
    """The Scenario board as one line, e.g. '✅ S1 · ⬜ S2 (works in P3)'."""
    if not (root / "evals" / "scenarios.py").exists():
        return "⬜ not built yet (phase 1 creates it)"
    code = "from evals.scenarios import run_all\nI={'not_built':'⬜','fail':'❌','pass':'✅'}\n"
    code += "print(' · '.join(f'{I[r.state]} {r.id}' for r in run_all()))"
    out = venv_run(root, ["-c", code]).splitlines()
    if not out:
        return "could not run evals/scenarios.py"
    works = progress.scenario_phases()  # say when each unbuilt scenario starts working, so "P1 ✅" never reads as "S1 works"
    return " · ".join(
        f"{c} (works in P{works[c.split()[1]]})" if c.startswith("⬜") and c.split()[1] in works else c for c in out[-1].split(" · ")
    )


def app_url(root: Path) -> str:
    """The running app's URL from the .app.pid / .app.port files, or how to start it."""
    for name in (".app",):
        pid, port = root / f"{name}.pid", root / f"{name}.port"
        if pid.exists() and port.exists():
            try:
                os.kill(int(pid.read_text().strip()), 0)
                return f"http://localhost:{port.read_text().strip()} (running)"
            except (OSError, ValueError):
                pass
    return "not running (/build starts it)"


def status(root: Path) -> str:
    """'Where you are' in the classroom in the current folder: notes, plan, phases, board, rules, app, next step."""
    phases, notes, state = progress.phases(), notes_written(root), progress.status()
    if phases and all(done for done, _ in phases.values()):
        nxt, clock = "code freeze: .venv/bin/python scripts/demo.py, then read docs/talk.md", CLOCK["present"]
    elif phases and state == "draft":
        nxt, clock = "approve docs/plan.md (re-run /discovery to see its question)", CLOCK["discovery"]
    elif phases:
        n = min(k for k, (done, _) in phases.items() if not done)
        nxt, clock = f"/build → Phase {n}: {phases[n][1]}", CLOCK.get(n, "")
    elif notes:
        nxt, clock = "/discovery", CLOCK["discovery"]
    else:
        nxt, clock = "interview → write notes/raw.md, then /discovery   (learning? /demo)", "0:00–0:10"
    own = root / "scripts" / "spec.py"  # an older classroom keeps its own checker
    rules = venv_run(root, [str(own if own.exists() else KIT / "templates" / "spec.py"), "check"]).splitlines()
    lines = [
        f"📍 Where you are · {root.name}",
        f"  Notes   {'✅ ' + str(notes) + ' lines' if notes else '⬜ empty'}",
        f"  Plan    {'✅ docs/plan.md · ' + (state or 'no Status line') if progress.plan_text() else '⬜ not yet'}",
        "  Phases  " + (" · ".join(f"{'✅' if d else '⬜'} P{k}" for k, (d, _) in phases.items()) or "⬜ none yet"),
        f"  Board   {board(root)}",
        f"  Rules   {rules[-1] if rules else '—'}",
        f"  App     {app_url(root)}",
        f"  Next    {nxt}",
        f"  Clock   {clock}",
    ]
    if progress.last_ticked():
        lines.append(f"  Try it (phase {progress.last_ticked()}):")
        lines += [f"    {i}. {line}" for i, line in enumerate(progress.try_it(progress.last_ticked()), 1)]
    return "\n".join(lines)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "setup"
    if cmd == "setup":
        print(SETUP)
    elif cmd == "status":
        print(status(Path.cwd()))
    else:
        sys.exit(__doc__)
