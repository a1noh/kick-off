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
What happened: docs/plan.md now holds the 3 demo scenarios in Dev's words, every rule traced to a notes line
(raw.md:L…), the data gotchas, 2 diagrams and 4 phases with exact "Try it" lines.
In a real interview: run it in plan mode, read §2 (scenarios) and §2b (the app sketch), answer its questions, approve.
The demo answered its own questions with the recommended option: search the plan for "confirmed by demo run".
Look at: docs/plan.md (⇧⌘V shows the diagrams) · git log shows the "plan" tag.
Next (automatic): /build phase 1, the whole screen with nothing working yet.""",
    "3": """\
🎓 Demo 3/3 · The app shell (/build phase 1)
What happened: /build wrote docs/specs/phase-1/spec.md first, then tests, then the code in src/ and ui/, and proved
it: docs/specs/phase-1/verify.md is the real screen, written by a script, never by hand.
Look at: the app (URL above). Both tabs, every panel ⬜, the Scenario board all ⬜, the chat answers 🚧. That honest
"nothing works yet" screen is the starting point every real build has too.
Your turn: /build → phase 2 makes scenario 1 work (paste your Gemini key into .env first). Then 3, 4 and /rehearse.
A real one: make an empty folder → claude → /kickoff.""",
}


def seed(root: Path) -> int:
    notes = root / "notes" / "raw.md"
    if not (root / ".claude" / "hooks" / "guard_raw_notes.py").exists() or not notes.exists():
        print("NOT A CLASSROOM: run /kickoff first (in an empty folder), then /demo.")
        return 1
    text = notes.read_text()
    head, sep, body = text.partition("\n---\n")
    if not sep or body.strip():
        print("NOTES NOT EMPTY: notes/raw.md already has notes. /demo needs a fresh classroom (empty folder → /kickoff).")
        return 1
    brief = BRIEF.read_text()
    notes.write_text(head + sep + "\n" + brief)
    (root / ".kickoff-demo").write_text("This classroom runs the built-in /demo (sample brief: kickoff/demo/brief.md).\n")
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
