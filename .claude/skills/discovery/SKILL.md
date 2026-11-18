---
name: discovery
description: Turn the user's raw interview notes (notes/raw.md) and data/ into docs/requirements.md (business rules + decisions) and a code-level docs/plan.md (Status: draft; functions §5c, records §5d, S1 flow §5e, requirements per phase) that the user approves before any code, for a 2-hour build of an AI agent (chat / batch / Q&A) or a plain app (tool / dashboard / workflow, optional AI helper) - picks the kind and shape, copes with thin notes (sample data, exact questions to ask), 3 demo scenarios from the interviewer, rules traced to the notes, data gotchas, architecture + agent-loop diagrams, 4 phases (phase 1 = the full app shell with every scenario ❌ on a Scenario board, then each phase turns features ✅; each with an "On screen (before → after)" line and a "Try it" checklist incl. one 🚧 still-broken item), eval cases, likely questions. Ends by asking the user to approve the plan. Works for any use case. Re-runnable after each new round of notes. Use when the user types /discovery inside a /kickoff classroom.
---

# /discovery: raw notes → requirements + a code-level plan → the user approves it

## 0. Check the room
This must be a /kickoff classroom: `CLAUDE.md` and `notes/raw.md` exist. If not, say so and suggest running `/kickoff`
in the folder first. Plan mode isn't needed: the plan file itself is the draft, and §6 asks for approval.
`KIT` = `../kickoff/templates` next to this skill's base directory (spec.py, progress.py run from there).

## 1. Read (never edit `notes/raw.md`; it's the user's)
- Read `notes/raw.md` fully. Number its lines in your head; you'll cite them as `raw.md:L12`.
- **Data pasted into the notes** (CSV/JSON/text blocks under a file name such as `orders.csv`): if that file is not in
  `data/` yet, write it to `data/<name>` **exactly as pasted** (no cleaning: the gotchas must stay for the code to handle).
  Mention it in the plan's gotchas table.
- Read every file in `data/` and **profile it for gotchas**: duplicates, missing values, inconsistent formats or casing,
  records in the past or outside allowed windows, conflicting rows, inactive/frozen/on-leave entities, capacity already
  full, the same value under two owners, flags stored as strings, values the rules need that the data lacks.
- If `docs/plan.md` already exists, this is a **re-run**: you'll update it, set `**Status:** draft` again, and report what changed.

## 2. Kind, shape, then the 3 demo scenarios (the heart of the plan)
**First the kind** (CLAUDE.md "Kinds and shapes"). Ask: *does the core job need to understand free text?*
- **Agent**: yes (messages, emails, documents, questions in plain language). Shapes: **chat**, **batch**, **Q&A**.
- **App**: no (forms, buttons, files with columns, numbers, dates). Shapes: **tool** (input → result: scheduler,
  booking, calculator, planner), **dashboard** (data → filters, charts, tables), **workflow** (records move through
  states: tickets, approvals, inventory). An app may have **one optional AI helper** for a single step (e.g. "type your
  request in words → booking fields"), never for a rule.
- **Default: agent.** Only pick app when the notes clearly have no free text at the core.
- Mixed? Pick the kind whose **core** job it is, and put the rest in Out of scope or in the optional helper.
  Nothing fits? Pick the closest shape, say so in one line, and adapt the door (CLAUDE.md "The app"): the method
  (UI first, 4 phases, board, dashboard) never changes.
Say kind + shape and why in one line of the Goal.

**Then the UI mode** (only the door + Owner dashboard change; the Python core is identical in both):
- **`react`** (default): FastAPI `ui/api.py` (display only) + a Vite React (JSX) UI from the kit's `templates/react/`
  (`../kickoff/` next to this skill), designed by the bundled **Impeccable** after phase 1 and in phase 4 (see `/build`).
  Needs Node ≥ 18: check `node -v` (also try `bash -lc 'node -v'`, nvm may only be on the login shell's PATH).
- **`streamlit`**: only when Node < 18 / missing (e.g. a cloud session without Node: say so in one line) or the
  interviewer wants a Python-only app.
Write it as one line at the top of §2b: `**UI:** streamlit` or `**UI:** react`.

From the interviewer's answers in raw.md, take **exactly 3**, in their words where possible:
1. **Happy path**: their typical example
2. **Edge case**: their tricky or messy case
3. **Stop / handoff**: when the system must refuse, block or bring in a human. Agent: a human takes over. App: a rule
   blocks the action (clash, over capacity, not allowed) or it needs someone's approval. (Add a "bonus" for the
   check-in stop trigger if the notes name one: injection, abuse, a dangerous input.)
A scenario's input fits the shape: chat = a conversation; batch = an item + its expected result; Q&A = a question +
the answer and its source; tool = the form values + the result; dashboard = a filter + what the chart/table shows;
workflow = a record + the action + its new state.

**Variability: thin or messy notes.** Never stall, never invent silently:
- An answer is missing → tell the user the exact question to ask the interviewer ("What's a typical example…?" /
  "What's a tricky or messy case…?" / "When must it refuse or bring in a human?"). At most 2 other blocking questions.
- **No data given** → write a small sample to `data/sample_<name>.csv` (8–12 rows) with 3–4 realistic gotchas baked in
  (a duplicate, a bad format, a missing value, an out-of-range value), and add an open question in requirements.md
  ("No data was given: build on this sample?") so the user can tell the interviewer.
- **The interviewer names a stack**: React / a web frontend → `**UI:** react` (if Node ≥ 18). Anything else (a database,
  another framework, an API) → keep the POC as is and add a line to requirements.md Out of scope + talk §6: "In production this would be
  <their stack>; the logic in core/tools ports as is."
- **The brief changes mid-build** → the user re-runs `/discovery`; keep built phases ticked, re-plan only the unchecked ones.

## 3a. Write `docs/requirements.md` first (WHAT the client needs)
Copy `templates/requirements.md` (this skill's base directory) and fill it from the notes and data only:
problem + success in their words, **business rules B1..Bn** (one line each, each traced to `raw.md:L<n>`, `data/<file>`
or "decided with user <date>"), **decisions D1..Dn** on every ambiguous point (question · answer · why), data facts, out
of scope (+ the free-LLM-tier gap for personal, financial or health data), open questions. No code and no file names:
this is the file the client could read. Anything you had to decide that the notes don't say is an open question, asked
in §5 before approval, never decided silently.

## 3b. Write `docs/plan.md` (HOW it's built: the study file)
Copy `templates/plan.md` and keep its headings. It starts `**Status:** draft`. Title: `# Plan: <product name>`. Sections, in order:
1. **Goal**: what was asked, for whom, what success means (cite raw.md lines), and the kind + shape line. If it uses an
   LLM (agent, or an app's optional helper), name it: Gemini free tier via `.env` (CLAUDE.md), and say what it does:
   extract fields only. If not: "No AI: every step is plain Python."
2. **Demo scenarios (from the interviewer)**: the 3 above, each with the exact input and output in a quote block (a
   conversation for chat; input → result for the other shapes) and "Must be true at the end:" (state changes, records,
   queue entries, what is NOT done). **Put at least one positive fact first** (a record written, an exact reply in
   "quotes"); negative facts ("unchanged", "model not called") come after it, because on a stub they are vacuously true.
   Then **§2b The app: what you'll see and how to check it** (the user tests every phase by hand in this UI). The **whole
   screen exists from phase 1**: the user sees everything that will be built, broken first, and watches each phase fix it.
   - The app has **two tabs** (CLAUDE.md "The app"): the **user's door** (chat / batch / Q&A, the shape) and the
     **📊 Owner dashboard**, a mini back-office for whoever runs the product day to day (from the Users answers: the
     owner, the team that takes over, whoever reads the log). Name the owner and, in 2–3 bullets, what they need to see
     every day (cite raw.md). Make the dashboard fit the domain: refunds → a refund ledger (KPIs: count, $ total, pending
     approval); scheduler → a mini calendar of bookings by day; batch → the results table by route; Q&A → questions asked +
     unanswered ones; workflow → a board of records by state. If the product **is** a dashboard, tab 2 shows what's behind
     it instead: data-quality issues found, rows excluded and why, and the change log. Plus the handoff/blocked queue and the audit log. **At most one owner action** (e.g. Approve a pending
     refund, Resolve a queue item), and only if the notes name a human step; it runs through a gated tool and is audited.
   - An ASCII sketch of **both tabs** in ```text blocks (the final screen), each panel labeled `[live in PN]`. Panel
     names are this project's records (e.g. Refunds, Queue, Audit). The sidebar holds progress + Try it + the
     **Scenario board** (one row per scenario, S1, S2, S3, bonus) with **3 states**: ⬜ not built (only 🚧 replies,
     sub-checks not evaluated) · ❌ broken · ✅ works. The user watches ⬜ turn ✅.
   - A table `Panel · Shows · In phase 1 · Live in` (one row per panel). "In phase 1" says what the panel shows before it
     is live, e.g. `⬜ placeholder: "arrives in phase 3"` or `all ⬜`.
   - "How to check a phase" in 3 lines: open the app URL `/build` printed → look at the **Scenario board** and the
     panels (did the "before → after" in the phase happen?) → for each `Try it` line: start fresh (**New chat** / new
     upload / new question, to fit the shape), give the input, compare
     the reply **and** the panel to the expected result → all match? `/build` · anything off? tell Claude what you saw.
3. **Business rules**: one line pointing at requirements.md. The plan cites B<n>/D<n>; it never restates a rule.
4. **Data gotchas**: table `# · Gotcha · How the code handles it` (G1, G2, …). Fail safe: unknown values take the
   careful path.
5. **Architecture** (§5) and **who decides what** (§5b): copy the template for the kind **exactly**: agent →
   `templates/architecture.md`, app → `templates/architecture_app.md` (headings, node IDs, shapes, arrow labels,
   `classDef` colors, the ⇧⌘V line, the 4-row table) and replace every `‹slot›` (`templates/example_refill.md` shows a
   filled-in one). No extra boxes. Obey its **SAFE MERMAID** rule, including **a clear path, no dead ends**.
   - **§5c Interfaces** (follow CLAUDE.md "Coding standards": fewest files, each with one job, ~8–10 product files):
     one `### \`<file>\` · <part>: <its one job>` per file, then one line per **public** function:
     `` - `Agent.reply(text: str) -> str` · One message in, one checked reply out · guards run around the model ``.
     The middle part is the function's docstring line 1, word for word (`spec.py check` compares them once the file
     exists, and the parameter names too). Leave private helpers out. Every product file in `src/` and `ui/*.py` must
     appear here, including `ui/api.py` (`screen`, `chat`) and the stub in phase 1.
   - **§5d Records**: each record (input, decision/booking, queue row, audit line) as typed JSON, and where it lives.
   - **§5e Sample flow (S1)**: the call chain for S1 as a table `# · Call · Returns`: each call in backticks with its
     real arguments, each return as JSON in backticks (or the exact reply in "quotes" on the last row). Use only public
     functions from §5c. Phase 2's `tests/test_flow.py` asserts every row, so write the real values.
6. **Phases** as checkboxes, **exactly 4**. **UI first, then features:** phase 1 builds the whole screen with nothing
   working yet, and every later phase visibly turns something from broken (❌ / 🚧 / ⬜) into working (✅ / live). The user
   should never have to read a diff to know what a phase changed.
   - `- [ ] Phase 1: the app shell (everything visible, nothing working yet)`: **`ui/app.py`** (UI react: **`ui/api.py`** +
     **`ui/web/`** from the kit's React templates, same screen) with the full §2b layout,
     both tabs (every panel; not-yet-live ones show `⬜ <panel>: arrives in phase N`), the **Scenario board**, a stub `src/agent.py`
     whose replies are honest fixed texts (`🚧 <feature> arrives in phase N`; never a fake success), and
     `evals/scenarios.py` (S1–S3 + bonus as data: inputs + the "Must be true at the end" checks, run offline: with a
     fixed extractor for an agent, directly through `core.py` for an app; the board shows their results). App kind:
     the stub is `src/core.py` instead of `src/agent.py`. No LLM, no data code yet. Tests: app imports, the board has one row per
     scenario, all ⬜ while stubbed, no sub-check ever green on a stub, and the screen matches plan.md (tests read the
     plan's ticks, so they stay true in later phases).
   - `- [ ] Phase 2: scenario 1 works end to end`: `data/*` (if needed), `src/data.py`, `src/tools.py` (gated), and
     - **agent:** `llm.py` (Gemini REST via `requests`, key + model from `.env`, returns JSON of the fields; 1 retry on
       429/503, then a polite "try again" reply) + the real `agent.py` loop (takes the extractor as a parameter so tests
       never hit the network);
     - **app:** the real `core.py` (one request end to end; rules in plain Python), plus `llm.py` only if the plan has
       the optional helper (same rules as above, and the app still works when the helper is off);
     `scripts/demo.py` running S1, `tests/test_flow.py` (asserts every §5e row), tests. S1's record goes live on the Owner dashboard (e.g. the refund ledger + KPIs); board S1 ⬜→✅.
   - `- [ ] Phase 3: safety + scenarios 2–3`: `guards.py` in/out (agent: stop triggers + output checks; app: input
     validation + "result matches the records"), queue with reasons, audit log JSONL; the dashboard's
     queue + audit panels go live (+ the owner action, if the plan has one); board S2, S3, bonus ⬜→✅.
   - `- [ ] Phase 4: evals + talk`: `evals/` runner (agent: against live Gemini; app: every case end to end through
     `core.py`, plus live Gemini for the helper cases if there is one), scorecard, Eval score panel live on the dashboard, polish,
     `docs/talk.md` (for the client) filled in full, plan §9 Likely questions answered. UI react: phase 1 `Builds:` ends with "Impeccable polish on `ui/web/src`", phase 4 with "Impeccable critique + polish on `ui/web/src`".
   - Put this line right under the `## 6. Phases` heading: "Every `On screen` and `Try it` line describes the app
     **after** that phase is built and ticked. Expected replies are in \"quotes\".
     Requirements cite B<n>/D<n>, raw.md:L<n>, data/<file> or `user <date>: \"<words>\"`; each names the test that
     proves it." (write them so a machine can check them).
   - Under **each** phase, in this order:
     - **`On screen (before → after):`** one line naming exactly what changes in the app, e.g.
       `Board S1 ⬜→✅ · Refund requests ⬜→live · S1 reply 🚧→real`.
     - **`Builds:`** the file list above, in this project's words.
     - **`Try it:`** 2–4 lines: `` `<exact input>` → "<exact text the user should see>" ``, with the expected reply or
       panel text **in quotes, character for character** (including emoji and the final period). Use the scenarios' exact inputs
       (an "input" is whatever the shape takes: a chat line, a sample file to upload, a question).
       - **Phase 1** (nothing works yet, so it's a tour): line 1 = S1's input → its exact 🚧 stub reply, e.g.
         `"🚧 Rescheduling arrives in phase 2."`; then "open the 📊 Owner dashboard tab → every panel shows
         \"⬜ <panel>: arrives in phase N\""; then "Scenario board → all ⬜ (every check ⬜, \"not built yet (🚧 stub
         reply)\") · Progress \"✅ P1\", \"⬜ P2\"–\"⬜ P4\"". Remember, this describes the screen *after* phase 1 is ticked.
       - **Phases 2–4:** line 1 = S1 (the regression check). The rest are what this phase fixed; from phase 3 on at least
         one shows a refusal or handoff. **Phases 2–3 end with exactly one 🚧 line**: an input that is *still broken* and
         the phase that fixes it (e.g. `` `can I talk to a person` `` → 🚧 "handoff arrives in phase 3"). Phase 4 has none.
       - Expected results must be visible in the app (reply, panel or board), not only in code. **Never quote text
         that only appears after a click** (an action button, an upload, a Try): `spec.py verify` renders the
         screen as loaded (every tab and panel) but can't click.
     - **`Requirements:`** one per Try-it line, per "Must be true" check of each scenario the phase turns ✅, per rule
       (B<n>) and gotcha it implements, and the screen contract. Exact format (the kit parses it):
       ```
         - **Requirements:**
           - **P2.R1** · S1 ready bike
             - Traces to: B1 · raw.md:L34
             - Acceptance: `is my bike ready? T-100 Nguyen` → "Your blue Trek is ready. …"
             - Test: tests/test_phase2.py::test_r1_ready_bike
       ```
       Each test's docstring cites it (`"""plan.md P2.R1: …"""`). Tests stay true in later phases (they read the ticks).
7. **Eval cases** (8–15) as a table `# · Input · Expected`, **grown from the 3 scenarios**: exact scenarios, variations,
   wrong inputs, and one case per data gotcha.
8. **Out of scope** lives in requirements.md.
9. **Likely questions**: the heading and its guide line only; `/build` phase 4 fills the answers from what was built.

## 4. Check it
Run `.venv/bin/python $KIT/spec.py check`. Every requirement must be grounded and quoted (tests may not exist yet: they
are only checked once a phase is ticked), every B<n> cited must exist, every diagram must have no dead ends. Fix the plan
until it prints `SPEC OK`.

## 5. Finish: the approval gate
- Tell the user: view the diagrams with **⇧⌘V** on `docs/plan.md`.
- **Open questions first:** ask them with AskUserQuestion (max 4 per call; recommended answer first). Write each answer
  into requirements.md as a decision (`D<n> … · decided with user <date>`) and update the rules and plan that use it.
- On a re-run: list in 3–5 bullets what changed in requirements.md and plan.md, and why (which new raw.md lines).
- Show the road ahead as 4 one-liners (board state after each + `Try it` count), and the §5c file list with its function
  count ("📁 8 files, 17 functions"), so the user knows what they are approving.
- Then ask with AskUserQuestion: **"Approve plan.md (function list + S1 flow)?"** with options "Approve" (recommended)
  and "Change something".
  - **Approve** → replace the Status line with `**Status:** approved <today>`, then
    `git add -A && git commit -q -m "discovery: plan + data" && git tag -f plan` (re-run: message
    `discovery: re-run (<what changed>)`; the tag moves). Show `git show --stat --oneline HEAD`. Commits stay local: never push.
    Next step: `/build`.
  - **Change something** → make the change in requirements.md / plan.md, keep `**Status:** draft`, run §4 again and ask again.
- **Stop.** `/build` refuses to start while the plan is a draft.
