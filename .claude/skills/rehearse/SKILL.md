---
name: rehearse
description: Code freeze and presentation rehearsal for a /kickoff classroom - run the 3 demo scenarios, walk docs/talk.md section by section with the user, then ask 5 likely interviewer questions one at a time and critique each answer. Use when the user types /rehearse.
---

# /rehearse: code freeze, then practice presenting

**Code freeze:** don't change any code in this command. Only `docs/talk.md` may be touched: fill §1–§6 first if they still
hold only the template's _italic_ placeholders (time ran out before the last phase; follow `/build` §5; §7 Build story
already has entries from each phase), otherwise only if the user asks.

## 1. Run the 3 demo scenarios
Run `.venv/bin/python scripts/demo.py` (or the scenario tests if there's none; older classrooms: `demo.py` in the root). Show each scenario's outcome in one line:
✅ works / ❌ broken. If one is broken, say so plainly: the user should either skip it in the demo or mention it as a known gap.
Don't fix it. Make sure the app is running (start it as `/build` §3 step 7 does; URL in `.streamlit.port`, or `.app.port` for UI react): the user presents from the app, not the terminal.
Point the user at the **Scenario board**: all ✅ is the opening shot of the demo. The board checks the logic offline (fixed
AI answers); `scripts/demo.py` above uses live Gemini. If they disagree (board ✅, demo ❌), the logic is fine and the live model
misread the input: say that plainly; it's a good "known gap" line for the talk.

## 2. Walk `docs/talk.md` with the user, section by section
For each of the 6 sections, then **§7 Build story** (the user tells it as "it started all ❌, then phase by phase…": the
strongest way to explain the build to a crowd):
- Ask the user to say it in their own words (2–4 sentences), as they would to the interviewer.
- Then give 2 lines of feedback: what was strong, and the one thing to add or cut (point at talk.md content they missed).
- Go to the next section only when they're ready. They can say "skip".

## 3. Mock interview: 5 questions, one at a time
Ask the 5 questions an interviewer would most likely ask about **this** build. Mix them:
- how a specific part works ("Walk me through what happens when…")
- a design choice ("Why X instead of Y?")
- safety/hallucination ("What stops it from making up a…?")
- a failure/gap ("What happens if…? What would you fix next?")
- measurement/production ("How would you know it's working with real users?")

After each answer: **critique in 2 lines** (what landed · what to add, citing the file or talk.md section). Then the next question.

## 4. Close
3 bullets: the strongest part of their pitch · the weakest spot to fix in the talk · the one sentence to open with.
