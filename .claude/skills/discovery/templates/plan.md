<!-- TEMPLATE for docs/plan.md. HOW it's built: the study file the user approves before any code. ~350 lines.
Keep every heading. Fill every ‹slot›. Business rules live in requirements.md: cite them (B1, D1), never restate.
The parsers (kit progress.py / spec.py) read: the Status line, §5c, §5e, the phase lines, Try it and Requirements. -->
# Plan: ‹product name›

**Status:** draft

## 1. Goal
‹One paragraph: what was asked, for whom, success (cite requirements.md). Kind + shape and why, in one line.
LLM: "Gemini free tier via .env, extracts ‹fields› only" or "No AI: every step is plain Python.">

## 2. Demo scenarios (from the interviewer)
### S1 · ‹happy path›
> ‹exact conversation / input → output›

Must be true at the end: ‹a positive fact first: a record written, an exact reply in "quotes"› · ‹negative facts after›
### S2 · ‹edge case› …
### S3 · ‹stop / handoff› …
### Bonus · ‹stop trigger, if the notes name one› …

## 2b. The app: what you'll see and how to check it
**UI:** react
‹Owner + what they check daily. ASCII sketch of both tabs, panels labeled [live in PN]. Table `Panel · Shows · In phase 1 · Live in`.
One-click actions for the chat header (ACTIONS), if any. "How to check a phase" in 3 lines.›

## 3. Business rules
In docs/requirements.md (B1..Bn, decisions D1..Dn). This plan cites them; it never restates them.

## 4. Data gotchas
| # | Gotcha | How the code handles it |
|---|---|---|
| G1 | ‹e.g. duplicate rows› | ‹e.g. grouped by bike, shown once› |

## 5. Architecture
‹From templates/architecture.md (agent) or architecture_app.md (app), slots filled. §5 + §5b.›

## 5c. Code: every file it will write, and what passes between them
**Every file the build writes**, by phase (Coding standards in CLAUDE.md: fewest files, each with one job).
`spec.py check` fails on a code file that isn't in this table, and on a ticked phase whose files don't exist.
| File | Phase | Job | Takes in | Gives back |
|---|---|---|---|---|
| `src/agent.py` | 1 | ‹brain: one chat› | ‹a message (str)› | ‹the reply (str)› |
| `ui/api.py` | 1 | ‹door: the screen as JSON + the chat› | ‹HTTP: {"session", "text"}› | ‹{"reply"}; the screen JSON› |
| `ui/web/` | 1 | kit React template, copied as is | `/api/screen` JSON | the page |
| `evals/scenarios.py` | 1 | ‹the 3 scenarios + bonus as data with checks› | ‹an extractor, an Agent factory› | ‹board rows› |
| `tests/test_phase1.py` | 1 | ‹proves P1.R*› | — | — |
| `‹src/tools.py›` | 2 | ‹hands› | ‹…› | ‹…› |

Then one `###` per Python file, one entry per function the rest of the code calls. Each entry is the signature line
`` `signature -> return` · <its docstring line 1, word for word> · <why> `` and two shape lines: **`in:`** each argument
with a real example value, **`out:`** what comes back, as real JSON (name the §5d record when it is one).
### `src/agent.py` · brain: ‹one job›
- `Agent.reply(text: str) -> str` · ‹One message in, one checked reply out› · ‹guards run around the model›
  - in: `text` "‹S1 input›"
  - out: "‹the exact reply›"
### `src/tools.py` · hands: ‹one job›
- `‹name›(‹params›) -> ‹type›` · ‹docstring line 1› · ‹why›
  - in: `‹param›` ‹example value›
  - out: ‹example JSON / §5d record›

## 5d. Records
Each record as typed JSON (where it lives, every field and its type).
### ‹record› (`out/‹name›.jsonl`)
```json
{"‹field›": "str", "‹field›": "int", "at": "str (ISO time)"}
```

## 5e. Sample flow (S1)
The call chain for S1 with the real object at each step, ending in the reply text. `tests/test_flow.py` runs S1
offline and asserts each step equals this table, so it can't drift from the code.
| # | Call | Returns |
|---|---|---|
| 1 | `‹check_in("<S1 input>")›` | `‹null›` |
| 2 | `‹extract("<S1 input>")›` | `‹{"intent": "…", …}›` |
| 3 | `‹tool(…)›` | `‹{record}›` |
| 4 | `‹Agent.reply("<S1 input>")›` | "‹the exact reply›" |

## 6. Phases
Every `On screen` and `Try it` line describes the app **after** that phase is built and ticked. Expected replies are in
"quotes". A Try-it line never quotes text that only appears after a click. Requirements cite B<n>/D<n>, raw.md:L<n>,
data/<file> or `user <date>: "<words>"`; each names the test that proves it.
- [ ] Phase 1: the app shell (everything visible, nothing working yet)
  - **On screen (before → after):** ‹nothing → both tabs, every panel ⬜, board all ⬜, chat 🚧›
  - **Builds:** ‹files›
  - **Try it:**
    1. `‹S1 input›` → "‹🚧 … arrives in phase 2.›"
    2. Open the 📊 Owner dashboard tab → every panel shows "‹⬜ KPIs: arrives in phase 2›"
  - **Requirements:**
    - **P1.R1** · ‹title›
      - Traces to: ‹plan.md §2b · raw.md:L‹n››
      - Acceptance: `‹input›` → "‹exact text›"
      - Test: tests/test_phase1.py::test_r1_‹name›
- [ ] Phase 2: scenario 1 works end to end
  - … (same four parts)
- [ ] Phase 3: safety + scenarios 2–3
  - …
- [ ] Phase 4: evals + talk
  - …

## 7. Eval cases
| # | Input | Expected |
|---|---|---|
| E1 | ‹S1 input› | "‹exact reply›" |

## 9. Likely questions (filled in phase 4, from what was built)
The questions a client or interviewer will most likely ask, each answered in 1–2 lines, naming the function that
does it (never file:line). Cover: why an LLM at all · prompt injection · a case the guard word list misses · is the
board mocked (offline board vs live evals) · concurrency / scale · what it never does · cost and model · next fix.
- **‹question›** ‹answer› (`‹function()›`)
