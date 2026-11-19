---
name: demo
description: Learn the kickoff process on a built-in sample interview (bike repair chat by default; `/demo maintenance` for a property-maintenance triage batch; `/demo laptops` for an IT laptop-request workflow, no AI; `/demo handbook` for an HR handbook Q&A agent; `/demo providers` for a healthcare provider-search API; `python3 <kit>/bin/demo.py briefs` lists them). Run it right after /kickoff in an empty folder - it writes the sample into notes/raw.md, runs /discovery (answering its open questions with the recommended option) to produce docs/spec.md and docs/plan.md, and STOPS at the plan approval question so the user reads and approves the plan. It builds nothing: /build takes it from there. Shows a short fixed "what just happened" box after each step. Needs no Gemini key. Use when the user types /demo.
---

# /demo: watch discovery once, on a sample, up to the approved plan

**KIT_HOME** = `../kickoff` next to this skill's base directory (`export KIT_HOME="<that path>"` in each command).
The user is here to *learn the flow*. Your own commentary between steps: **one line at most**. The boxes are the
explanation, and they come from `$KIT_HOME/bin/demo.py`, printed exactly. The demo ends at the approved plan: it builds
nothing (that's `/build`).

## 1. Pick the sample and seed it
- The sample is the argument (`/demo maintenance`), or `bike` when there is none. `python3 "$KIT_HOME/bin/demo.py" briefs`
  lists them; if the user asked for "a new / different use case" without naming one, pick one that isn't `bike`.
- `python3 "$KIT_HOME/bin/demo.py" seed <name>`. If it prints `NOT A CLASSROOM`, `NO SUCH SAMPLE` or `NOTES NOT EMPTY`,
  show that line and stop. (Writing the notes this way is the documented exception: the notes guard protects the
  *user's* notes from Claude's edits; `seed` only fills the still-empty template with the kit's sample.)
- `python3 "$KIT_HOME/bin/demo.py" box 1` → show it exactly, in a ```text block.

## 2. Discovery: follow `/discovery`, with one demo override
Read `../discovery/SKILL.md` and follow it fully (§0–§5), from these notes alone (never copy a plan from another folder):
- Its **open questions**: pick the **recommended** answer yourself and record it as a decision
  `D<n> … · decided with user <today> (demo run: recommended answer)`.
- **The approval question is NOT overridden.** Show `python3 "$KIT_HOME/bin/demo.py" box 2` exactly, then ask
  "Approve plan.md (the files, the diagram and every function)?" as `/discovery` §5 says, and wait for the user's answer.
  - **Approve** → Status → approved, commit (body = the changed files) + tag `plan`, local, never pushed.
  - **Change something** → change it, keep the draft, ask again.

## 3. Close
After Approve: `python3 "$KIT_HOME/bin/demo.py" box 3` → show it exactly, then `git show --name-status --oneline plan`.
**Stop.** The user continues with `/build` (phase 1).
