---
name: demo
description: Learn the kickoff process on a built-in sample interview (a bike repair shop). Run it right after /kickoff in an empty folder - it writes the sample brief into notes/raw.md, runs /discovery on its own (answering its open questions with the recommended option), STOPS at the plan approval question so the user reads and approves the code-level plan, then builds phase 1, showing a short fixed "what just happened" box after each step. Needs no Gemini key, so it also works on the phone. Use when the user types /demo.
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

## 2. Plan: follow `/discovery`, with one demo override
Read `../discovery/SKILL.md` and follow it fully (§0–§5), with this override:
- Its **open questions**: pick the **recommended** answer yourself and record it as a decision
  `D<n> … · decided with user <today> (demo run: recommended answer)`. The UI mode is the default (React with Node ≥ 18).
- **The approval question is NOT overridden.** Show `python3 "$KIT_HOME/bin/demo.py" box 2` exactly, then ask
  "Approve plan.md (function list + S1 flow)?" as `/discovery` §5 says, and wait for the user's answer. Only on
  Approve: Status → approved, commit + tag `plan`. On "Change something": change it, then ask again.

## 3. Phase 1: follow `/build`, with demo overrides
Read `../build/SKILL.md` and follow it for **phase 1 only**: tests → code → (React: Impeccable polish, §3b) → verify
(`VERIFY OK`, `SPEC OK`) → app running → Build-story entry → commit + tag `phase-1` (local, never pushed). Any question →
the recommended answer, recorded as above. Skip the long §5 handover, but show its `📁 Files` and `🔀 Diff` lines.

## 4. Close
Print the app URL (`/build` §3 step 6; none in a cloud session → say "run `.venv/bin/python $KIT/spec.py verify 1` to
see the screen as text"), then `python3 "$KIT_HOME/bin/demo.py" box 3` → show it exactly. Stop. The user continues
with `/build` (phase 2).
