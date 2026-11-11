#!/usr/bin/env python3
"""What /kickoff shows, printed by code so it is the same every time (Claude shows it verbatim).

  python3 guide.py setup     the short welcome after a fresh setup (fixed text)
  python3 guide.py status    "where you are" in the current classroom (computed, read-only)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

SETUP = """\
✅ Kickoff ready · a 2-hour build in 4 visible steps

You interview → plan → build → present. The app comes first: every scenario starts ⬜ and turns ✅ step by step.

  1  Key    paste your Gemini key into .env → check: .venv/bin/python scripts/check_llm.py
  2  0:00   interview with GUIDES → write it in notes/raw.md (Goal · Users · Inputs · Happy path · Danger · Edges · Scale)
  3  0:10   /discovery (plan mode) → docs/plan.md → read it, approve it
  4  0:15   /build ×4 → after each step do its "Try it" list in the app, then /build again
  5  1:40   code freeze → /rehearse

New here? /demo fills in a sample interview and runs steps 2–4 up to phase 1, explaining each one.
Lost? /kickoff shows where you are. Everything else: CHEATSHEET.md"""

CLOCK = {"discovery": "0:10–0:15", 1: "0:15–0:25", 2: "0:25–0:50", 3: "0:50–1:15", 4: "1:15–1:30", "rehearse": "1:40–1:55"}
PHASE = re.compile(r"^- \[( |x)\] Phase (\d+): (.*)$", re.M)


def notes_written(root: Path) -> int:
    """Lines the user added below the template's '---' in notes/raw.md (0 = still empty)."""
    p = root / "notes" / "raw.md"
    if not p.exists():
        return 0
    body = p.read_text().split("\n---\n", 1)
    return len([x for x in (body[1] if len(body) == 2 else "").splitlines() if x.strip()])


def try_it(plan: str, n: int) -> list[str]:
    m = re.search(rf"^- \[[ x]\] Phase {n}:", plan, re.M)
    if not m:
        return []
    block = plan[m.end() :]
    end = re.search(r"^- \[[ x]\] Phase \d+:|^## ", block, re.M)
    block = block[: end.start()] if end else block
    parts = block.split("**Try it:**", 1)
    return re.findall(r"^\s+\d+\. (.+)$", parts[1], re.M) if len(parts) == 2 else []


def venv_run(root: Path, code: list[str]) -> str:
    py = root / ".venv" / "bin" / "python"
    if not py.exists():
        return ""
    env = {k: v for k, v in os.environ.items() if k != "__PYVENV_LAUNCHER__"}
    r = subprocess.run([str(py), *code], cwd=root, capture_output=True, text=True, env=env, timeout=120)
    return (r.stdout or r.stderr).strip()


def board(root: Path) -> str:
    if not (root / "evals" / "scenarios.py").exists():
        return "⬜ not built yet (phase 1 creates it)"
    code = "from evals.scenarios import run_all\nI={'not_built':'⬜','fail':'❌','pass':'✅'}\n"
    code += "print(' · '.join(f'{I[r.state]} {r.id}' for r in run_all()))"
    out = venv_run(root, ["-c", code]).splitlines()
    if not out:
        return "could not run evals/scenarios.py"
    works = works_in(root)  # say when each unbuilt scenario starts working, so "P1 ✅" never reads as "S1 works"
    return " · ".join(
        f"{c} (works in P{works[c.split()[1]]})" if c.startswith("⬜") and c.split()[1] in works else c for c in out[-1].split(" · ")
    )


def works_in(root: Path) -> dict[str, int]:
    """Scenario id -> phase that makes it work, from the plan's On screen lines ("Board S2, S3 ⬜→✅")."""
    plan = (root / "docs" / "plan.md").read_text() if (root / "docs" / "plan.md").exists() else ""
    found: dict[str, int] = {}
    for n in [int(x) for _, x, _ in PHASE.findall(plan)]:
        m = re.search(rf"^- \[[ x]\] Phase {n}:(.*?)(?=^- \[[ x]\] Phase \d+:|^## |\Z)", plan, re.M | re.S)
        line = re.search(r"On screen[^\n]*", m[1]) if m else None
        for group in re.findall(r"Board ([^·]*?)⬜→✅", line.group(0) if line else ""):
            for sid in re.findall(r"\b(S\d+|[Bb]onus)\b", group):
                found.setdefault(sid[0].upper() + sid[1:], n)
    return found


def app_url(root: Path) -> str:
    for name in (".streamlit", ".app"):
        pid, port = root / f"{name}.pid", root / f"{name}.port"
        if pid.exists() and port.exists():
            try:
                os.kill(int(pid.read_text().strip()), 0)
                return f"http://localhost:{port.read_text().strip()} (running)"
            except (OSError, ValueError):
                pass
    return "not running (/build starts it)"


def status(root: Path) -> str:
    plan_p = root / "docs" / "plan.md"
    plan = plan_p.read_text() if plan_p.exists() else ""
    phases = {int(n): (x == "x", name) for x, n, name in PHASE.findall(plan)}
    notes = notes_written(root)
    if phases and all(d for d, _ in phases.values()):
        nxt, clock = "/rehearse (code freeze)", CLOCK["rehearse"]
    elif phases:  # the plan decides once it exists
        n = min(k for k, (d, _) in phases.items() if not d)
        nxt, clock = f"/build → Phase {n}: {phases[n][1]}", CLOCK.get(n, "")
    elif notes:
        nxt, clock = "/discovery (plan mode)", CLOCK["discovery"]
    else:
        nxt, clock = "interview → write notes/raw.md, then /discovery   (learning? /demo)", "0:00–0:10"
    spec = venv_run(root, ["scripts/spec.py", "check"]).splitlines() if (root / "scripts" / "spec.py").exists() else []
    lines = [
        f"📍 Where you are · {root.name}",
        f"  Notes   {'✅ ' + str(notes) + ' lines' if notes else '⬜ empty'}",
        f"  Plan    {'✅ docs/plan.md' if plan else '⬜ not yet'}",
        "  Phases  " + (" · ".join(f"{'✅' if d else '⬜'} P{k}" for k, (d, _) in phases.items()) or "⬜ none yet"),
        f"  Board   {board(root)}",
        f"  Specs   {spec[-1] if spec else '—'}",
        f"  App     {app_url(root)}",
        f"  Next    {nxt}",
        f"  Clock   {clock}",
    ]
    done = [k for k, (d, _) in phases.items() if d]
    if done:
        lines.append(f"  Try it (phase {max(done)}):")
        lines += [f"    {i}. {t}" for i, t in enumerate(try_it(plan, max(done)), 1)]
    return "\n".join(lines)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "setup"
    if cmd == "setup":
        print(SETUP)
    elif cmd == "status":
        print(status(Path.cwd()))
    else:
        sys.exit(__doc__)
