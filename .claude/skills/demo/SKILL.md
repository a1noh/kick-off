---
name: demo
description: Learn the kickoff process on a built-in sample interview (a bike repair shop). Run it right after /kickoff in an empty folder - it writes the sample brief into notes/raw.md, runs /discovery on its own (answering its own questions with the recommended option), then builds phase 1, showing a short fixed "what just happened" box after each step. Needs no Gemini key, so it also works on the phone. Use when the user types /demo.
---

# /demo: watch the process once, on a sample, up to phase 1

**KIT_HOME** = `../kickoff` next to this skill's base directory (`export KIT_HOME="<that path>"` in each command).
The user is here to *learn the flow*. Your own commentary between steps: **one line at most**. The boxes are the
explanation, and they come from `$KIT_HOME/bin/demo.py`, printed exactly.

## 1. Check and seed
- `python3 "$KIT_HOME/bin/demo.py" seed`. If it prints `NOT A CLASSROOM` or `NOTES NOT EMPTY`, show that line and stop.
  (Writing the notes this way is the documented exception: the notes guard protects the *user's* notes from Claude's edits;
  `seed` only fills the still-empty template with the kit's sample and refuses otherwise.)
- `python3 "$KIT_HOME/bin/demo.py" box 1` → show it exactly, in a ```text block.

## 2. Plan: follow `/discovery`, with demo overrides
Read `../discovery/SKILL.md` and follow it fully (§0–§6), with these overrides:
- No plan mode, no waiting for approval.
- Wherever it would ask the user (AskUserQuestion), pick the **recommended** option yourself and record it as
  `Assumption: … · confirmed by demo run <today>`. The UI mode is `streamlit`.
- Commit and tag as the skill says (`discovery: plan + data`, tag `plan`).
Then `python3 "$KIT_HOME/bin/demo.py" box 2` → show it exactly.

## 3. Phase 1: follow `/build`, with demo overrides
Read `../build/SKILL.md` and follow it for **phase 1 only**: spec → tests → code → verify (`VERIFY OK`) → app running →
Build-story entry → commit + tag `phase-1`. Same override: any question → the recommended answer, recorded
`confirmed by demo run <today>`. Skip the long §5 handover.

## 4. Close
Print the app URL (`/build` §3 step 7; none in a cloud session → say "open docs/specs/phase-1/verify.md to see the screen"),
then `python3 "$KIT_HOME/bin/demo.py" box 3` → show it exactly. Stop. The user continues with `/build` (phase 2).
