#!/usr/bin/env python3
"""The /demo tool: a built-in sample interview + the fixed explanation boxes shown between steps.

  python3 demo.py seed      put the sample brief into notes/raw.md (only while it is still the empty template)
  python3 demo.py box N     print explanation box N (1 = notes, 2 = plan, 3 = phase 1)

Why `seed` may write notes/raw.md: the notes guard stops *Claude's edits* to the user's notes. In demo mode the notes are
the kit's own sample, and seed refuses as soon as the file holds anything the user wrote.
"""

from __future__ import annotations

import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
BRIEF = KIT / "demo" / "brief.md"

BOXES = {
    "1": """\
🎓 Demo 1/3 · The interview (GUIDES)
What happened: a sample interview is now in notes/raw.md. Dev runs a bike repair shop and wants a chat bot that
answers "is my bike ready?" and books a pickup time; price questions go to Dev.
In a real interview YOU write this file while asking the 6 GUIDES questions. Claude reads it but never edits it.
Look at: notes/raw.md → the Goal, the Danger line ("never tell someone another person's bike status") and the
pasted repairs.csv with its messy rows.
Next (automatic): /discovery turns these notes into a plan.""",
    "2": """\
🎓 Demo 2/3 · The plan (/discovery)
What happened: docs/requirements.md holds Dev's business rules (B1…, each traced to a notes line) and the
decisions on what the notes left open (D1…). docs/plan.md (Status: draft) is the code-level plan: §5c names every
function before it's written, §5e shows scenario 1 step by step, and each phase lists its requirements + tests.
The demo answered the open questions with the recommended option: search requirements.md for "demo run".
Look at: requirements.md, then plan.md §5c + §5e (⇧⌘V shows the diagrams).
Your turn: approve the plan (the question below). Nothing is built until you do.""",
    "3": """\
🎓 Demo 3/3 · The app shell (/build phase 1)
What happened: /build wrote phase 1's tests from its requirements in plan.md, then the code in src/ and ui/ (every
file named in §5c, every function documented), and proved it: the kit's spec.py verify 1 rendered the real screen.
git diff plan phase-1 --stat shows exactly what phase 1 added (committed locally, never pushed).
Look at: the app (URL above). Both tabs, every panel ⬜, the Scenario board all ⬜, the chat answers 🚧. That honest
"nothing works yet" screen is the starting point every real build has too.
Your turn: /build → phase 2 makes scenario 1 work (paste your Gemini key into .env first). Then 3 and 4.
A real one: make an empty folder → claude → /kickoff.""",
}


def seed(root: Path) -> int:
    """Fill the still-empty notes/raw.md with the sample brief; exit code 1 when it isn't an empty classroom."""
    notes = root / "notes" / "raw.md"
    if not (root / ".claude" / "settings.json").exists() or not notes.exists():
        print("NOT A CLASSROOM: run /kickoff first (in an empty folder), then /demo.")
        return 1
    text = notes.read_text()
    head, sep, body = text.partition("\n---\n")
    if not sep or body.strip():
        print("NOTES NOT EMPTY: notes/raw.md already has notes. /demo needs a fresh classroom (empty folder → /kickoff).")
        return 1
    brief = BRIEF.read_text()
    notes.write_text(head + sep + "\n" + brief)
    print(f"SEEDED: notes/raw.md now holds the sample interview ({len(brief.splitlines())} lines, bike repair shop).")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["seed"]:
        sys.exit(seed(Path.cwd()))
    if args[:1] == ["box"] and len(args) == 2 and args[1] in BOXES:
        print(BOXES[args[1]])
        sys.exit(0)
    sys.exit(__doc__)
