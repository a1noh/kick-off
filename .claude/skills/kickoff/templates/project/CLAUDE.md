# Project rules for Claude (2-hour build)

We have **2 hours** to build a working, demoable POC (an AI agent or a plain app; see "Kinds and shapes"), and the user
must be able to present it. Goal 1: **it works.** Goal 2: **the user understands it and can present it.** So: **UI first**.
Phase 1 builds the whole screen with nothing working (every scenario ⬜, honest 🚧 replies, ⬜ panels), and each later
phase visibly turns something ✅. After each phase the user **tries it in the app**, without reading a diff.

## Commands (the workflow)
| Command | When | Does |
|---|---|---|
| `/discovery` | 0:10–0:15, after the interview; re-run after new notes | notes + data → `docs/spec.md` + `docs/plan.md` (**Status: draft**) → the user approves it |
| `/build` | 0:15–1:30, once per phase (×4) | next unticked phase of the approved plan → tests → code → `spec.py verify N` → app running → commit + tag → **Try it** list → stop |
Before presenting (1:40, code freeze): `.venv/bin/python scripts/demo.py`, then read `docs/talk.md` top to bottom with the app open.

## Docs: each has one job (nothing else is written)
| File | Job | Written by |
|---|---|---|
| `notes/raw.md` | the user's raw interview notes. **Never edit it** (a hook blocks it) | the user |
| `docs/spec.md` | **the whole discovery in plain English (what + why)**: problem + success, the demo scenarios S1–S3, what the app shows, business rules B1..Bn (each traced to `raw.md:L<n>` or "decided with user <date>"), decisions D1..Dn, messy data G1..Gn, eval cases E1..En, out of scope. No code | `/discovery` (+ scope changes) |
| `docs/plan.md` | **the technical file (how), the one to study**: Status, overview, architecture, §3 Files (every file the build writes), §4 Functions (each with its in/out shapes), §5 Records, §6 Flow (S1 step by step), §7 Phases with requirements P<n>.R<k>, §8 Likely questions. Cites spec.md, never restates it | `/discovery`; `/build` ticks phases |
| `docs/talk.md` | **for the client and viewers**: the problem, the demo, how it works, decisions, safety, results, the build story. Cites functions by name (never `file:line`) | `/build` (§7 every phase, the rest in phase 4) |
`docs/talk.html` (browser view, git-ignored) comes from the kit's `render_docs.py` on demand. Git history is the build log.

## Product layout (Coding standards below decide what exists: every file is named in plan.md Functions)
`src/` = the product (Python decides) · `ui/` = the screen only · `tests/` · `evals/` · `data/` · `scripts/demo.py`.
Imports stay flat (`from agent import Agent`): the venv's `classroom.pth` puts `src/`, `ui/`, the root and the kit's
`templates/` (for `progress`) on the path. In `src/` and `ui/` use `ROOT = Path(__file__).resolve().parents[1]`.
Typical files: `src/data.py` (memory), `src/guards.py` (check in + check out), `src/agent.py` (agent kind: the loop) or
`src/core.py` (app kind: one request end to end), `src/llm.py` (Gemini REST, the only network file; app kind only with the
optional AI helper), `src/tools.py` (hands, gated in code), `ui/api.py` + `ui/web/` (React, default) or `ui/app.py`
(Streamlit), `evals/scenarios.py` (the 3 scenarios + bonus: drives the Scenario board) and `evals/run.py`.

## Kit tools run from the kit, never copied into the project
`KIT` = `.claude/skills/kickoff/templates` if it exists, else `~/.claude/skills/kickoff/templates`. Run them from the project folder:
- `.venv/bin/python $KIT/spec.py check`: plan + code obey the rules below (the Stop hook runs it with the tests).
- `.venv/bin/python $KIT/spec.py verify N`: runs phase N's tests and its Try-it screen claims, prints the result.
- `.venv/bin/python $KIT/check_llm.py` (Gemini key) · `.venv/bin/python $KIT/render_docs.py` (talk.html) · `progress` (imported by the UI).
Hooks (in `.claude/settings.json`, found at run time): ruff on every edit, the raw-notes guard, tests + `spec.py check` on stop.

## The app (React `ui/api.py` + `ui/web/` by default; Streamlit `ui/app.py` only without Node ≥ 18)
- **Must match the sketch in spec.md §3.** Everything exists from phase 1: panels not live yet show `⬜ <panel>: arrives
  in phase N`; unbuilt behavior replies `🚧 <feature> arrives in phase N` and never claims success. Never remove a panel.
- **Tab 1, the user's door** (the shape): chat (input + history + "New chat"), batch (upload / "use sample" → results),
  Q&A (question → answer + source), tool (form → result + updated view), dashboard (filters → KPIs, chart, table),
  workflow (records → pick one → allowed actions → new state). One-click actions sit in the chat header (`ACTIONS`).
- **Tab 2, 📊 Owner dashboard**: KPIs, the domain view of what the system did, the handoff/blocked queue, the audit log,
  the eval score. At most one owner action, only if the notes name a human step, through a gated tool, audited.
- **Sidebar = the build guide** (from the kit template): progress stepper + next command, the **Scenario board**
  (⬜ not built / ❌ / ✅ from `evals/scenarios.py`, offline; a check that something did *not* happen is only evaluated
  after a real reply, so a stub never shows green), then the last phase's **Try it** lines (closed once all are built).
- No logic in `ui/`: it only displays. Same entry point (`agent.py` / `core.py`) as `scripts/demo.py` and the tests.
- Runs in the background on the first free port from 8501; pid/port in `.app.pid` / `.app.port` (Streamlit: `.streamlit.*`).

## Plan-driven (no intuition)
- **No code before the plan is approved.** plan.md starts `**Status:** draft`; only the user's yes makes it
  `**Status:** approved <date>`. `/build` refuses a draft plan, and `spec.py check` fails on a ticked phase under one.
- Every requirement (P<n>.R<k>) has `Traces to:` (B<n>, `raw.md:L<n>`, `data/<file>` or `user <date>: "<their words>"`),
  `Acceptance:` with the exact expected value in "quotes", and `Test:` naming a test whose docstring cites `plan.md P<n>.R<k>`.
- Something no source says → **ask the user**, then record it (`decided with user <date>` in spec.md). Never guess.
- Files/Functions/Records change only by editing plan.md **first**; the handover says `📐 Plan changed: …`. A scope change the user asks
  for becomes a requirement sourced to their words (no re-approval needed).
- `On screen` / `Try it` lines describe the app **after** the phase is ticked. A Try-it line never quotes text that only
  appears after a click (verify can't click). Tests stay true in later phases (they read the plan's ticks).
- A user-reported mismatch becomes a new requirement (source = the report) with a test, then the fix.

## After every phase (`/build` does this)
1. Tests pass (`.venv/bin/python -m pytest -q tests`); `scripts/demo.py` runs (from phase 2).
2. Tick the phase, then `spec.py verify N` → `VERIFY OK` and `spec.py check` → `SPEC OK`. The app is running.
3. Append the phase's Build-story entry to `docs/talk.md` §7, then one commit for the phase (its body lists every changed
   file) and `git tag -f phase-N`. Commits stay local: **never push**. `git diff phase-<N-1> phase-N` shows the change.
4. Hand over what changed on screen, the board before → after, the **Try it** list and **every changed file**, then **STOP**.

## Kinds and shapes (picked by `/discovery`)
- **Agent** (the core job needs free text): **chat**, **batch** (a file of items, each classified/extracted, then routed) or **Q&A**.
- **App** (no free text at the core): **tool**, **dashboard** or **workflow**, with at most **one optional AI helper**
  for a single step (e.g. words → form fields); the app still works with it off.
- Every shape uses the same loop: check in → ① read the input → ② Python decides → ③ tool → ④ output → check out.

## Architecture defaults
- **The LLM understands; plain Python decides.** Every rule (identity, limits, money, eligibility, capacity, clashes,
  allowed state changes, safety) lives in code. Tools are **gated in code** and re-check their own gates.
- **Agent kind, guard in** before the LLM: stop triggers (emergency, legal threat, fraud, self-harm, prompt injection,
  off-topic) skip the model and go to a fixed reply or a human. **App kind:** validate every input, fix-it message first.
- **Guard out** after: no data before verification, no invented values, no claiming success unless a tool did it.
- The LLM is **Gemini (free tier) over REST** with `requests` (no SDK). `.env` holds `GEMINI_API_KEY` and `GEMINI_MODEL`
  (python-dotenv). Never read or print `.env`. The LLM **extracts** JSON fields; replies are Python templates filled from
  tool results. Generated text (a draft, a summary) is checked against the source and approved by a human before sending.
- Tests never call the network: the extractor is a parameter, tests pass a 1-line fixed function. An audit log (JSONL) of every decision.
- Diagrams: mermaid `flowchart LR`, quoted labels, labeled solid arrows, `classDef` colors. No HTML tags, no dotted,
  two-way or chained arrows. **A clear path, no dead ends**: every node has an arrow out, except stores and end points.

## Coding standards (the one place these rules live: plan.md Functions, `/build` and `spec.py check` all follow it)
**Minimal**
- Fewest files that do the job, each with a clear job named in plan.md Functions. Merge a file into its caller when it is small
  and used once, only re-exports, or only holds constants. A build like this needs about 8–10 product files.
- Fewest lines that do the job. Only the code a requirement asks for: nothing "for later", no unused parameters,
  options or config. No duplicate helpers, no dead or commented-out code.
- No clever indirection (mixins, registries, dynamic dispatch, metaprogramming) unless plan.md says why.

**Readable as plain English**
- Every file starts with a 3–5 line docstring: what it does, and where it sits in the S1 flow (plan.md Flow).
- Every function has a docstring, private helpers included. Line 1, plain English: what it does, what it takes and
  returns. Optional line 2: why it works this way. A public function's line 1 is word for word its plan.md Functions line.
- Inline comments explain *why* (a business rule, a gotcha like G3, a safety choice), never *what*.
- Plain names (`expense`, not `e`; loop variables excepted). Type hints on every function.
- Short functions in top-down order: public first, helpers below, one job each, early returns over nested ifs.
- One way to do each thing across the codebase (e.g. every reply comes from one place).

**Enforced by `spec.py check`** (every phase): it fails when a file in `src/` or `ui/*.py` has no top docstring, a function
or method has no docstring, a file isn't in the Functions file table, a Functions function has no `in:`/`out:` shape, a Functions signature or line 1 doesn't match the code, a doc cites `file:line`
or a function that doesn't exist, or kit scaffolding is committed. It warns past ~150 lines per file or ~30 per function.
Explain as you go: one short ★ Insight per file, on *why*.

## Commands
Tests: `.venv/bin/python -m pytest -q tests` · Rules: `.venv/bin/python $KIT/spec.py check` / `verify N` · Demo: `.venv/bin/python scripts/demo.py` ·
App: `.venv/bin/uvicorn api:app --app-dir ui` (Streamlit: `.venv/bin/streamlit run ui/app.py`)
