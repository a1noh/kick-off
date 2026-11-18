#!/usr/bin/env python3
"""The /demo tool: built-in sample interviews + the fixed explanation boxes shown between steps.

  python3 demo.py briefs         list the sample interviews (demo/briefs/*.md)
  python3 demo.py seed [NAME]    put sample NAME (default: bike) into notes/raw.md, only while it is the empty template
  python3 demo.py box N          print explanation box N (1 = notes, 2 = plan, 3 = plan approved)

/demo stops at the approved plan: it shows discovery, the part people most need to learn; /build takes it from there.
Why `seed` may write notes/raw.md: the notes guard stops *Claude's edits* to the user's notes. In demo mode the notes are
the kit's own sample, and seed refuses as soon as the file holds anything the user wrote.
"""

from __future__ import annotations

import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
BRIEFS = KIT / "demo" / "briefs"

BOXES = {
    "1": """\
🎓 Demo 1/3 · The interview (GUIDES)
What happened: a sample interview is now in notes/raw.md: the client's brief, their answers to the 6 GUIDES
questions, and the data they pasted (with its messy rows).
In a real interview YOU write this file while asking the GUIDES questions. Claude reads it but never edits it.
Look at: notes/raw.md → the Goal, the Danger line (what it must never get wrong) and the pasted data.
Next (automatic): /discovery turns these notes into docs/spec.md and docs/plan.md.""",
    "2": """\
🎓 Demo 2/3 · The discovery (/discovery)
What happened: docs/spec.md is the whole discovery in plain English: the 3 scenarios, what the app shows, the
business rules (B1…, each traced to a notes line), the decisions on what the notes left open (D1…), the messy data and
what "good" looks like. docs/plan.md (Status: draft) is the implementation spec: every file the build will write,
one diagram, and every function with what goes in and what comes out (how it does it is one click away).
The demo answered the open questions with the recommended option: search spec.md for "demo run".
Your turn: read plan.md §2 Files, §3 How it works and §4 Functions (⇧⌘V), then answer the approval question below.""",
    "3": """\
🎓 Demo 3/3 · The plan is approved
What happened: plan.md now says **Status:** approved, and it's committed locally with the tag `plan`
(git show --name-status plan lists its files). Nothing is built yet, and nothing is pushed.
That's the end of the demo: you've seen the part that decides everything, notes → spec → an approved plan.
Your turn: /build builds phase 1 (the whole screen, nothing working yet), then /build again for phases 2–4.
A real one: make an empty folder → claude → /kickoff → write your notes → /discovery.""",
}


def names() -> list[str]:
    """The sample interviews' names, from demo/briefs/<name>.md."""
    return sorted(path.stem for path in BRIEFS.glob("*.md"))


def seed(root: Path, name: str = "bike") -> int:
    """Fill the still-empty notes/raw.md with sample `name`; exit code 1 when it isn't an empty classroom."""
    notes = root / "notes" / "raw.md"
    if not (root / ".claude" / "settings.json").exists() or not notes.exists():
        print("NOT A CLASSROOM: run /kickoff first (in an empty folder), then /demo.")
        return 1
    if name not in names():
        print(f"NO SUCH SAMPLE: {name}. Samples: {', '.join(names())}")
        return 1
    head, sep, body = notes.read_text().partition("\n---\n")
    if not sep or body.strip():
        print(
            "NOTES NOT EMPTY: notes/raw.md already has notes. /demo needs a fresh classroom (empty folder → /kickoff)."
        )
        return 1
    brief = (BRIEFS / f"{name}.md").read_text()
    notes.write_text(head + sep + "\n" + brief)
    title = brief.splitlines()[0].replace("## Interview: ", "", 1).split(" (")[0] if brief else name
    print(f"SEEDED: notes/raw.md now holds the sample interview '{name}' ({len(brief.splitlines())} lines, {title}).")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["briefs"]:
        print("\n".join(names()))
        sys.exit(0)
    if args[:1] == ["seed"] and len(args) <= 2:
        sys.exit(seed(Path.cwd(), *args[1:]))
    if args[:1] == ["box"] and len(args) == 2 and args[1] in BOXES:
        print(BOXES[args[1]])
        sys.exit(0)
    sys.exit(__doc__)
