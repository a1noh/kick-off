---
name: discovery
description: Turn the user's raw interview notes (notes/raw.md) and data/ into docs/spec.md (the whole discovery in plain English: scenarios, the app, business rules, decisions, messy data, eval cases) and a technical docs/plan.md, the implementation spec (Status: draft; every file, one diagram, every function with what it does in order and its In/Out, records, evals, requirements per phase) that the user approves before any code, for a 2-hour build of an AI agent (chat / batch / Q&A) or a plain app (tool / dashboard / workflow, optional AI helper) - picks the kind and shape, copes with thin notes (sample data, exact questions to ask), 3 demo scenarios from the interviewer, rules traced to the notes, data gotchas, architecture + agent-loop diagrams, 4 phases (phase 1 = the full app shell with every scenario ❌ on a Scenario board, then each phase turns features ✅; each with an "On screen (before → after)" line and a "Try it" checklist incl. one 🚧 still-broken item), eval cases, likely questions. Ends by asking the user to approve the plan. Works for any use case. Re-runnable after each new round of notes. Use when the user types /discovery inside a /kickoff classroom.
---

# /discovery: raw notes → spec.md (plain English) + plan.md (technical) → the user approves the plan

## 0. Check the room
This must be a /kickoff classroom: `CLAUDE.md` and `notes/raw.md` exist. If not, say so and suggest running `/kickoff`
in the folder first. Plan mode isn't needed: the plan file itself is the draft, and §6 asks for approval.
`KIT` = `../kickoff/templates` next to this skill's base directory (spec.py, progress.py run from there).

## 1. Read (never edit `notes/raw.md`; it's the user's)
- Read `notes/raw.md` fully. Number its lines in your head; you'll cite them as `raw.md:L12`.
- **Data pasted into the notes** (CSV/JSON/text blocks under a file name such as `orders.csv`): if that file is not in
  `data/` yet, write it to `data/<name>` **exactly as pasted** (no cleaning: the gotchas must stay for the code to handle).
  Mention it in spec.md §7 (messy data).
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
- **API** (either kind): the notes ask for an API, endpoints or a service other programs call ("build an API from this
  dataset"). The product is its HTTP routes; see **The API shape** below. Agent kind when a route takes free text
  (a search box, a question), app kind when every parameter is a field.
- **Default: agent.** Only pick app when the notes clearly have no free text at the core.
- Mixed? Pick the kind whose **core** job it is, and put the rest in Out of scope or in the optional helper.
  Nothing fits? Pick the closest shape, say so in one line, and adapt the door (CLAUDE.md "The app"): the method
  (UI first, 4 phases, board, dashboard) never changes.
Say kind + shape and why in one line of the Goal.

**The screen** is always the kit's React template on localhost (FastAPI `ui/api.py`, display only, + `ui/web/`); only
the door and the Owner dashboard change per project. It needs Node ≥ 18 (`node -v`, or `bash -lc 'node -v'` for nvm):
if it's missing, tell the user to install it before `/build`.

**The API shape** (the method never changes; only the door does):
- **The door is the request.** Tab 1 is a **🔌 API console**: the user types a request line (`GET /v1/providers/search?q=heart
  doctor in austin`, or `POST /v1/… {json}`) and sees the status code and the JSON. Scenarios, Try-it lines and eval
  inputs are request lines; an expected value is **one plain piece** of the reply in quotes, with no quote marks inside
  it: a message text ("2 active providers match.") or a value ("1003"), never a key-value pair. The screen and the
  checker pass a console line when the reply contains that piece.
- **Files:** `src/service.py` is the product's HTTP door: a FastAPI `APIRouter` under `/v1` with one thin route per
  endpoint (typed parameters, calls one `src/core.py` function, returns its dict and status) and a `Console` class whose
  `reply(line)` runs a request line against those routes in-process. The router comes from
  `make_router(extract, out_dir)`, so the board, the tests and the evals can pass an offline extractor and a temporary
  folder. `ui/api.py` includes the router (so `/docs` lists the real endpoints) and uses `Console` where a chat build
  uses `Agent`. Every rule stays in `src/`: `src/core.py` (one function per endpoint) arrives in phase 2; in phase 1
  the routes themselves answer `501`.
- **Parameters arrive as text and `src/core.py` checks them**, so every bad value gets the spec's own `400` and
  fix-it message (a typed `page: int` would answer with the framework's `422` instead). A line the console can't read
  is a `400` too, with an example request line.
- **spec.md §3** adds an endpoint table `| Method + path | Parameters | Returns | Errors | Works from phase |`.
  Every error is a rule with exact JSON: a bad parameter is `400` with a fix-it message, an unknown id `404`, an
  unbuilt route `501` with `🚧 <feature> arrives in phase N`.
- **plan.md §5 Records** shows each endpoint's request and response as JSON, next to the stored records.
- **Search or ranking?** Then quality is measured, not eyeballed: spec.md §8 gets a second table, the **labelled
  queries** `| # | Query | Relevant ids (best first) |` (Q1..Qn, 8–12, written from the data, covering synonyms,
  typos, filters and one query with no good answer), and plan.md §6 says how `evals/run.py` scores them: precision@k
  and recall@k per query and on average, the target the notes give (else ask), and how ranking ties are broken (a
  rule in spec.md). A requirement in phase 4 quotes the target ("precision@3 ≥ 0.8"). **spec.md §4 explains the
  metrics in plain words**, so the reader never has to hunt for them: one sentence each for what precision@k and
  recall@k ask ("of what we showed, how much was right?" · "of what was right, how much did we show?"), then **one
  worked example from this project's own labelled queries** (the query, the ids returned, the relevant ids, the two
  numbers and the arithmetic), then why both are needed (one alone can be gamed).
- **Scale** (spec.md §4 gets a `**Scale:**` paragraph, and plan.md §8 a question on it): the data size today and the size the
  notes name (ask if they don't), what the POC does per request (e.g. "scans all 30 rows in memory"), what breaks
  first as it grows, and the change that fixes it (an index, a search engine, pagination, a cache, a queue), with the
  latency or throughput number it is aiming at. Pagination and a result limit are rules, built in the POC. **Mark
  every number as measured or estimated**; `/build` phase 4 replaces estimates it can measure (time per request with
  and without the model) with the measured ones.
- **The model has to earn its place.** If a keyword reader in code could read the query too, the labelled queries
  include at least two that only the model gets right (a paraphrase no synonym list has), and the eval prints both
  readers' scores side by side. A fallback from the model to the keyword reader records why (the error) in the
  request log.
- **The board mid-build:** a scenario whose route already works but whose rule arrives later shows ❌, not ⬜, so its
  phase line says `Board S3 ❌→✅`.

From the interviewer's answers in raw.md, take **exactly 3**, in their words where possible:
1. **Happy path**: their typical example
2. **Edge case**: their tricky or messy case
3. **Stop / handoff**: when the system must refuse, block or bring in a human. Agent: a human takes over. App: a rule
   blocks the action (clash, over capacity, not allowed) or it needs someone's approval. (Add a "bonus" for the
   check-in stop trigger if the notes name one: injection, abuse, a dangerous input.)
A scenario's input fits the shape: chat = a conversation; batch = an item + its expected result; Q&A = a question +
the answer and its source; API = a request line + the status and JSON; tool = the form values + the result; dashboard = a filter + what the chart/table shows;
workflow = a record + the action + its new state.

**Variability: thin or messy notes.** Never stall, never invent silently:
- An answer is missing → tell the user the exact question to ask the interviewer ("What's a typical example…?" /
  "What's a tricky or messy case…?" / "When must it refuse or bring in a human?"). At most 2 other blocking questions.
- **No data given** → write a small sample to `data/sample_<name>.csv` (8–12 rows) with 3–4 realistic gotchas baked in
  (a duplicate, a bad format, a missing value, an out-of-range value), and add an open question in spec.md
  ("No data was given: build on this sample?") so the user can tell the interviewer.
- **The interviewer names a stack**: React / a web frontend → `**UI:** react` (if Node ≥ 18). Anything else (a database,
  another framework, an API) → keep the POC as is and add a line to spec.md Out of scope + talk §6: "In production this would be
  <their stack>; the logic in core/tools ports as is."
- **Checks to make on your own plan before §4** (each one broke a real build):
  - The offline extractor in `evals/scenarios.py` (the fixed stand-in for the model) must give the right fields for
    **every** input a requirement, scenario or eval case uses offline: walk each input through its keyword list.
  - A function the kit's screen calls with no arguments (`Agent()`, `run_all()`) shows its defaults in its signature.
  - A function in a phase-1 file may only call what phase 1 builds; if it needs a later file, say what it does until then.
  - Each **Does** list is in the order the code runs (an error path sits at the step where it can happen).
  - Every panel and every value on screen has a function in §4 that produces it (the eval score included), in `src/`.
  - `evals/run.py` (when the plan uses a model) never counts a busy model as a wrong answer: live, a case whose reply
    is the model-unavailable line (or, where a fallback reader answers instead, a reply the fallback produced) is asked again after a pause (3 tries), then listed as **not scored**, apart from the
    fails; the scorecard and the Eval score panel say so. It has a requirement and an offline test (an extractor that
    raises). Its cases are spec.md §8 row for row, each with its E id.
  - The model prompt states rules (what each field means), never example inputs taken from the eval cases.
  - The demo data can be reset: `src/data.py` has the reset the screen's Reset button calls, built in phase 2.
  - In the §3 diagram, only the numbered request path starts a label with a number; write "all 19 rows", not "19 rows".
  - In a **Try it** line, backticks mark only what the user types into the door (the screen turns each one into a
    Try button). A terminal command or a file name in a Try-it line is written without backticks.
- **A change after the plan is approved** is not this skill's job any more: the user says it to `/build` in their own
  words (`/build` §0b updates spec.md and plan.md first, then builds; after the last phase it adds Phase 5, 6, …). Re-run
  `/discovery` only when the user brings a whole new round of interview notes: then update both docs everywhere the
  notes touch, never renumber or delete an id, keep built phases ticked, put new work in the unbuilt phases or a new
  phase, set `**Status:** draft`, list what changed and ask for approval.

## 3a. Write `docs/spec.md` first: the whole discovery in plain English
Copy `templates/spec.md` (this skill's base directory) and keep its headings. It is the WHAT and WHY: no code, no file
names, no function names, so the client or a new teammate can read it top to bottom. Every rule and decision is traced
(`raw.md:L<n>`, `data/<file>`, or "decided with user <date>"). Sections, in order:
1. **Problem and success** in their words (cite raw.md lines), and what we're building in one line.
2. **The demo scenarios** (S1, S2, S3, bonus): the 3 above, each with the exact input and output in a quote block (a
   conversation for chat; input → result for the other shapes) and "Must be true at the end:" (state changes, records,
   queue entries, what is NOT done). **Put at least one positive fact first** (a record written, an exact reply in
   "quotes"); negative facts ("unchanged", "model not called") come after it, because on a stub they are vacuously true.
3. **What the app shows** (the user tests every phase by hand in this UI). The **whole
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
4. **The design** (the most important section for the person presenting it): how the product works as **logical
   steps**, before any file exists. One mermaid diagram (SAFE MERMAID, no dead ends, **no file or function names**):
   what comes in → each check or decision in order → every way out (the answer, the stop, the handoff). Then the **who
   decides each step** table (the AI model only reads; every rule is plain code, and why), **design choices** (3–5
   lines: chose X over Y because Z, citing B/D ids), and **how we know it works** in plain words (scenarios, eval cases,
   what passing means; for search or ranking, each metric in one sentence plus one worked example from the labelled
   queries). For an API, the **Scale** paragraph sits here too. `spec.py check` fails without the diagram.
5. **Business rules B1..Bn**: one line each, each traced to `raw.md:L<n>`, `data/<file>` or "decided with user <date>".
6. **Decisions D1..Dn** on every ambiguous point (question · answer · why). Anything the notes don't say is an open
   question, asked in the approval gate below before approval, never decided silently.
7. **Messy data and what we do about it**: table `# · What's messy · What the product does` (G1, G2, …), in plain words. Fail safe: unknown values take the
   careful path.
8. **What "good" looks like** (eval cases, 8–15) as a table `# · Input · Expected`, **grown from the 3 scenarios**: exact scenarios, variations,
   wrong inputs, and one case per data gotcha.
9. **Out of scope** (+ the free-LLM-tier gap for personal, financial or health data).
10. **Open questions**.

## 3b. Write `docs/plan.md`: the implementation spec (HOW it's built, the study file)
Copy `templates/plan.md` and keep its headings (the kit parses **Files**, **How it works**, **Functions**, **Evals**
and the phases by name). It starts `**Status:** draft`. It cites spec.md (S1, B<n>, D<n>, G<n>, E<n>) and never
restates it. The LLM that runs `/build` writes the code **from this file**, so every function must be specified
completely; a person must also be able to read it once and understand the code.
1. **Overview**: kind + shape and why in one line; if it uses an LLM, name it (Gemini free tier via `.env`) and say it
   extracts fields only, else "No AI: every step is plain Python"; one line on the path a request takes.
2. **Files** (follow CLAUDE.md "Coding standards": fewest files, each with one job, ~8–10 product files): a table
   `| File | Phase | Job | Takes in | Gives back |` listing **every** file the build will write (each Python file in
   `src/`, `ui/`, `evals/`, `scripts/` and `tests/`, data files, `ui/web/` as one row). Split `src/` by kind of work:
   the model call (`llm.py`, the only network file), the orchestration (`agent.py` or `core.py`: reads the input,
   calls the others, builds the reply, decides nothing itself), the decisions (`rules.py` / guards: pure functions),
   the reads and writes (`data.py` / `tools.py`). `spec.py check` fails on a code file that isn't in the table, and on
   a ticked phase whose files don't exist. Under it, "How it's checked" in 3 bullets: tests, the board, the evals.
3. **How it works**: **one simple diagram** drawn for this project, never from a fixed template: one box per product
   file (`src/…`, `ui/api.py`) labeled with its job, the data stores it reads or writes, the user at each end, and
   arrows that say what they carry. The arrows one request follows (the S1 path) start with `1 `, `2 `, `3 `, … in the
   order they happen, once each; background arrows (loading data, saving, the owner's view) stay unnumbered. A guard, a queue or a stop box only when a spec.md rule needs one (CLAUDE.md
   "Architecture"). SAFE MERMAID (CLAUDE.md), no dead ends. It is spec.md §4's design mapped to files: each step there lands in one box here (who decides lives in spec.md). `spec.py check`
   fails when a product file has no box or a box names a file §2 doesn't list.
4. **Functions**, the implementation spec, grouped by `src/` file: one `### \`<file>\` — <its one job>` per file, then
   one block per function the rest of the code calls, exactly as the template shows (the kit parses it):
   `#### \`<name>\` — <a short title or question>` (e.g. `why_not_approve` — can this manager approve it?), then one
   visible sentence, its docstring line 1 word for word. **At first glance** a block is its heading and one plain sentence, so a reader
   skimming §4 sees what every function does and what goes in and out: **In** and **Out** stay visible, and how it
   does it sits after them inside `<details><summary>How it does it: signature, why, steps</summary>` … `</details>`
   (blank lines around the markdown inside). Inside, in order:
   - the full signature alone on a line, `` `name(param: type, …) -> return` `` (`spec.py check` compares it, and the
     visible sentence, with the code once the file exists), then `**Why** <why it works this way, citing its rule>`;
   - **Does**: numbered steps in plain words, in order: every path (each check, what it returns, its rule; what it
     saves; what it calls). This is what the code is built from, and what the tests check. No Python in the plan;
   - `**In** · the arguments, by name` and a ```jsonc block: keys are exactly the parameters, each with a comment
     `  // <type from the signature> · <what it is>`; the nested fields it uses commented with why they matter and
     their rule; fields it doesn't use become `"…": "<what was left out>"`, but **identifier fields always stay**
     (`id`, names, keys like the team) so the reader can tell which record it is;
   - `**Out** · \`<the return type>\`` and a ```jsonc block with one real example, important fields commented
     (```text for plain text); the other results are already in **Does**.
   Everywhere: values real and pretty-printed (2-space indent, comments after two spaces), every value data a person
   can read (an object shown by what it holds, never code like `Store("out")`, no escaped `\"`), placeholders in prose
   in backticks or markdown hides `<name>`. `ui/api.py` and tests are not explained: their §2 line is enough.
5. **Records**: each record (input, decision/booking, queue row, audit line) as typed JSON, and where it lives.
6. **Evals**, so a newcomer learns how the checks work: one `### \`evals/<file>\`` per evals file. Open each with
   what one item is, shown as commented JSON with real values (a scenario from spec S1–S3 + bonus: its commands, the
   lines the user must see, its checks; an eval case from spec §8: its input and the one line that must come back),
   then "how one runs" in a few steps, then its function blocks as in §4. Say in one sentence why the board (always
   offline) and the evals (the real model, in an AI project) are separate.
7. **Phases** as checkboxes, **exactly 4** on the first run (a later feature adds Phase 5, 6, …). **UI first, then features:** phase 1 builds the whole screen with nothing
   working yet, and every later phase visibly turns something from broken (❌ / 🚧 / ⬜) into working (✅ / live). The user
   should never have to read a diff to know what a phase changed.
   - `- [ ] Phase 1: the app shell (everything visible, nothing working yet)`: **`ui/api.py`** +
     **`ui/web/`** from the kit's React templates, same screen) with the full layout from spec.md §3,
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
     `scripts/demo.py` running S1, tests. S1's record goes live on the Owner dashboard (e.g. the refund ledger + KPIs); board S1 ⬜→✅.
   - `- [ ] Phase 3: safety + scenarios 2–3`: `guards.py` in/out (agent: stop triggers + output checks; app: input
     validation + "result matches the records"), queue with reasons, audit log JSONL; the dashboard's
     queue + audit panels go live (+ the owner action, if the plan has one); board S2, S3, bonus ⬜→✅.
   - `- [ ] Phase 4: evals + talk`: `evals/` runner (agent: against live Gemini; app: every case end to end through
     `core.py`, plus live Gemini for the helper cases if there is one), scorecard, Eval score panel live on the dashboard, polish,
     `docs/talk.md` (for the client) filled in full, plan §8 Likely questions answered.
   - Put this line right under the `## 6. Phases` heading: "Every `On screen` and `Try it` line describes the app
     **after** that phase is built and ticked. Expected replies are in \"quotes\".
     Requirements cite B<n>/D<n>, raw.md:L<n>, data/<file> or `user <date>: \"<words>\"`; each names the test that
     proves it." (write them so a machine can check them).
   - Under **each** phase, in this order:
     - **`On screen (before → after):`** one line naming exactly what changes in the app, e.g.
       `Board S1 ⬜→✅ · Refund requests ⬜→live · S1 reply 🚧→real`.
     - **`Builds:`** the file list above, in this project's words.
     - **`Try it:`** 2–5 lines: `` `<exact input>` → "<exact text the user should see>" ``, with the expected reply or
       panel text **in quotes, character for character** (including emoji and the final period); a reply of several lines
       quotes **one whole line** of it (the screen's Try button passes when the reply has that line). Use the scenarios' exact inputs
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
8. **Likely questions**: the heading and its guide line only; `/build` fills the answers in the last phase, from what was built.

## 4. Check it
Run `.venv/bin/python $KIT/spec.py check`. Every requirement must be grounded and quoted (tests may not exist yet: they
are only checked once a phase is ticked), every B<n> cited must exist and every B<n> in spec.md must be cited by a requirement, every diagram must have no dead ends. Fix the plan
until it prints `SPEC OK`.

## 5. Finish: the approval gate
- Tell the user: view the diagrams with **⇧⌘V** on `docs/plan.md`.
- **Open questions first:** ask them with AskUserQuestion (max 4 per call; recommended answer first). Write each answer
  into spec.md as a decision (`D<n> … · decided with user <date>`) and update the rules and plan that use it.
- On a re-run: list in 3–5 bullets what changed in spec.md and plan.md, and why (which new raw.md lines).
- Show the road ahead as 4 one-liners (board state after each + `Try it` count), and §2 Files with the number of functions §3 explains, with its function
  count ("📁 14 files, 17 functions, each with its in/out shapes"), so the user knows what they are approving.
- Then ask with AskUserQuestion: **"Approve plan.md (the files, the diagram and every function)?"** with options "Approve" (recommended)
  and "Change something".
  - **Approve** → replace the Status line with `**Status:** approved <today>`, then
    `git add -A && { echo "discovery: plan + data"; echo; git diff --cached --name-status; } | git commit -q -F - && git tag -f plan`
    (re-run: subject `discovery: re-run (<what changed>)`; the tag moves). Show `git show --name-status --oneline HEAD`. Commits stay local: never push.
    Next step: `/build`.
  - **Change something** → make the change in spec.md / plan.md, keep `**Status:** draft`, run §4 again and ask again.
- **Stop.** `/build` refuses to start while the plan is a draft.
