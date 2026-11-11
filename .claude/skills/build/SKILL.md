---
name: build
description: Build the next unchecked phase of docs/plan.md in a /kickoff classroom, SPEC-DRIVEN - first write docs/specs/phase-N/spec.md (every requirement traced to plan.md / raw.md / data, exact quoted acceptance, named test; untraceable → ask the user), then tests from the spec, then code, then verify (pytest + scripts/spec.py verify N renders the real screen) before handing back. UI first (Streamlit, or React via api.py + web/ when the plan says UI: react; phase 1 = full app shell, board all ⬜ not built, honest 🚧 stubs), each phase visibly turns features ✅. Keeps the app running, adds a Build-story entry, commits + tags, hands over a "Try it" checklist, stops. One phase per call. Use when the user types /build.
---

# /build: spec → tests → code → verify → the user tries it

Two goals, in order: **(1) a working build**, **(2) the user understands it and can present it**. The user learns by
**using the product**. The whole screen exists from phase 1, everything starts ⬜ / 🚧, and each phase turns something
✅ / real / live.

**No intuition.** Every behavior you build comes from a source: `docs/plan.md`, `notes/raw.md:L<n>` or `data/<file>`.
If you need something no source says, **ask the user** (AskUserQuestion) and write the answer into the spec. Never guess
silently. The spec comes before the code, and the evidence (`verify.md`) is written by a script, never by you.

**Paths:** `KIT` = `../kickoff/templates` next to this skill's base directory (works in `~/.claude/skills` and in a repo's
`.claude/skills`). Classroom layout: product code in `src/` (agent.py or core.py, tools.py, guards.py, data.py, llm.py),
screen in `ui/` (app.py, dashboard.py, progress.py; React: api.py + web/), `scripts/demo.py`. Imports stay flat (`from agent
import Agent`) thanks to the venv's `classroom.pth`. Older classrooms with files in the root: keep their layout.

## 0. Check
- `docs/plan.md` must exist with phase checkboxes. If not, say "run /discovery first" and stop.
- Take the **first unchecked phase** (`- [ ] Phase N: …`). If all are checked, say "All built → `/rehearse`" and stop.
- Say in one line which phase you're building, quoting its `On screen (before → after)` line.
- Classroom from an older kit (no `scripts/spec.py` or `docs/specs/_template/spec.md`)? Say so and ask the user
  to re-run `/kickoff` in this folder (it upgrades in place), then continue.
- **Open assumptions:** if plan.md has `Assumption:` lines that this phase depends on and that aren't marked
  `confirmed`, ask them now (AskUserQuestion, yes/no, max 4 per call). Write the answers into plan.md and the spec.

## 1. Spec first: `docs/specs/phase-N/spec.md`
Copy `docs/specs/_template/spec.md` and fill it **from the sources only**:
- **Scope:** the phase line and its `On screen` line, verbatim, plus what stays 🚧 / ⬜ and which phase fixes it.
- **Interfaces:** exact signatures and record schemas this phase adds. Keep the earlier phases' interfaces unchanged.
- **Requirements R1..Rn**, one for each of: every `Try it` line · every "Must be true" check of each scenario this phase
  turns ✅ · every rule (plan §3) and gotcha (§4) this phase implements · the **screen contract** (what the
  sidebar/panels show **after this phase is ticked**). Each R has exactly 3 one-line fields:
  - `Traces to:` the source (`plan.md §…`, `raw.md:L…`, `data/…`);
  - `Acceptance:` exact input → the exact expected value in **"quotes"**;
  - `Test:` `tests/test_phaseN.py::test_rK_…`.
- **Assumptions:** `none`, or each one `confirmed by user <date>`. An unconfirmed line blocks the build.
- Run `.venv/bin/python scripts/spec.py check`. Fix the spec until the only failures are "test … does not exist".

## 2. Tests from the spec, then code
- Write each R's test first, using the name the spec gives it. Assert the **quoted** value exactly.
  **Tests must stay true in later phases:** read the plan's ticks instead of hard-coding "this is still broken",
  e.g. "panel shows ⬜ iff its phase isn't ticked", or "a 🚧 reply names an unticked phase".
- Then the code. Use only what the spec says, the fixed layout in CLAUDE.md, and files under ~150 lines.
- **Phase 1 = the app shell, nothing else:**
  - `ui/app.py` with the **full** §2b layout. Tab 1 = the user's door. Tab 2 = **📊 Owner dashboard** (KPIs, domain view,
    queue, audit, eval score), read-only displays of `out/`. Not-live panels show `⬜ <panel>: arrives in phase N`.
  - **Scenario board** (sidebar), with **3 states**:
    - ⬜ not built: every reply is a `🚧` stub, and the sub-checks are **not evaluated** (shown ⬜);
    - ❌ fail;
    - ✅ pass.

    A check that something did *not* happen ("no fee", "nothing changed", "model not called") is vacuously true on a
    stub, so it is only evaluated after a real reply. Computed offline by `evals/scenarios.py`
    `run_all(extractor) -> list[Result]` (`Result.state`, `Result.checks: [(label, bool | None)]`), cached on file mtimes.
  - A stub `src/agent.py` (app: `src/core.py`) with the final interface. Every reply is `🚧 <feature> arrives in phase N.`,
    and it never claims success or shows data.
  - Sidebar: Progress (✅/⬜ from plan.md), the **last ticked** phase's Try it lines, the board, and the next command.
  - Required tests: `test_stub_replies_never_show_green` (force a stub agent → every scenario is `not_built`, and no
    sub-check is True) and `tests/test_screen.py::test_screen_matches_plan_and_board` (AppTest, or TestClient in UI react: Progress, Try it,
    Next and the board rows match plan.md + `run_all`, read live so the test holds in every phase).
  - No `llm.py` / `data.py` yet.
  - **`**UI:** react` in plan §2b** (otherwise skip this bullet): instead of `ui/app.py`, set up from
    `K=<KIT>` (see Paths):
    `cp $K/react/api_template.py ui/api.py; mkdir -p ui/web; cp -R $K/react/{package.json,vite.config.js,index.html,src} ui/web/; cp $K/react/test_screen_api.py tests/test_screen.py`,
    then `uv pip install --python .venv/bin/python fastapi==0.115.6 uvicorn==0.32.1 httpx==0.28.1` and
    `(cd ui/web && npm install --no-audit --no-fund && npm run build)`. Fill `ui/api.py`'s TITLE, TABS, PANELS, WIDE and
    SHOWS (the §2b panel table: phase, full-width panels, the "Shows" column). The guide sidebar (stepper + next command
    with Copy, Try-it rows with Copy/Try and a ✓/✗ reply check, the scenario accordion) comes with the template: don't
    rewrite it; adapt `ui/web/src/components/Chat.jsx` if the shape isn't chat. `ui/api.py` and `ui/web/` stay display only:
    the UI renders `/api/screen` strings and never decides. The required tests are the `TestClient` versions in
    `tests/test_screen.py` (same names). Later phases fill `LIVE` (panel → `{"kind": "metrics"|"table"|"lines", …}`)
    and `RESET` in `ui/api.py`. `npm test` (vitest, in `ui/web`) must pass too. Node < 18 → stop and tell the user (see CHEATSHEET).
    **Then design it with Impeccable** (§3b, "phase 1 pass": `polish`) before the verify step, so the first screen the
    user opens already looks finished.
- **Later phases** replace stubs and turn placeholders live. **Never remove a panel or a board row.** An owner action
  calls a gated function in `src/tools.py` and is audited. `ui/` never changes a record itself. From phase 2, keep `scripts/demo.py` running.
- One short ★ Insight per file: *why*, not what.

## 3. Verify (nothing goes back to the user until all of this is green)
1. `.venv/bin/python -m pytest -q tests`: green.
2. From phase 2: `.venv/bin/python scripts/demo.py` (live Gemini if the plan uses it; key missing or Gemini down → say so in one line, continue).
3. **Tick the phase** in plan.md (`- [x] Phase N: …`). The screen check must see the after-tick state.
4. `.venv/bin/python scripts/spec.py verify N`: runs the spec's tests and **renders the app with AppTest**. It writes
   `docs/specs/phase-N/verify.md` (pass/fail per R + the screen as text) and `docs/specs/README.md`.
   It must print `VERIFY OK`.
5. Read the screen dump in `verify.md` against the phase's `On screen` line and **every** `Try it` line, character by
   character for quoted text. Its "Try-it screen claims" list must be all ✅ (verify fails on a ❌): the plan, the screen and
   the guide say the same words. Mismatch → fix the code (or, if the plan line is wrong, fix plan + spec and tell the user),
   then repeat from step 1.
6. `.venv/bin/python scripts/spec.py check` → `SPEC OK` (the Stop hook enforces it too).
7. The app is running: if `.streamlit.pid` is alive, use the port in `.streamlit.port` ("refresh the tab"). Otherwise take
   the first free port from 8501 to 8510 (`lsof -ti tcp:$P` empty) and run
   `.venv/bin/streamlit run ui/app.py --server.headless true --server.port $P --server.runOnSave true > out/streamlit.log 2>&1 &`.
   Then `echo $! > .streamlit.pid; echo $P > .streamlit.port`, check `curl -s localhost:$P/_stcore/health` says `ok`,
   and `open http://localhost:$P`.
   **UI react:** rebuild first if `ui/web/` changed (`cd ui/web && npm run build`). Pid/port live in `.app.pid` / `.app.port`;
   if alive, restart it (uvicorn doesn't reload Python changes). Run
   `.venv/bin/uvicorn api:app --app-dir ui --port $P > out/app.log 2>&1 &`, save `.app.pid` / `.app.port`, check
   `curl -s localhost:$P/api/screen` returns JSON, and `open http://localhost:$P`.

## 3b. UI react only: Impeccable (bundled, pinned, no hook)
Runs twice: **phase 1** (`polish`, after the shell's tests pass, before `verify 1`) and **phase 4** (`critique`, then
`polish`). The kit carries a pinned copy (`../kickoff/vendor/impeccable/`, see its `PINNED` + Apache-2.0 `LICENSE`).
1. Install it into the project once (skip if `.claude/skills/impeccable/SKILL.md` exists):
   `V=<this skill's base>/../kickoff/vendor/impeccable; mkdir -p .claude/skills .claude/agents .impeccable && cp -R $V/skill .claude/skills/impeccable && cp $V/agents/*.md .claude/agents/ && echo '{"telemetry": false}' > .impeccable/config.json`.
   Never `npx impeccable install` and never its hooks/settings.
2. Product context: if `PRODUCT.md` is missing, write it from `docs/plan.md` §1–§2b (users, purpose, operating
   context: "an agent builds this live in an interview; the guide sidebar shows that on purpose", constraints: quoted
   texts render exactly, the UI only displays `ui/api.py`). Mark inferred facts. Don't stop for an interview.
3. With `DO_NOT_TRACK=1`: run its launcher `sh .claude/skills/impeccable/scripts/impeccable context --target ui/web/src`
   (first run downloads its engine, verified against the bundled checksums). If that fails (offline, cloud network),
   use the skill's documented "Launcher unavailable" path instead and say its one line. Read `reference/craft-floor.md`
   before any edit; mode = **Operate**. The kit's shell (guide sidebar, board, chat, panels) is an established surface:
   extend and polish it, no new-world round inside a timed build.
4. Phase 1: follow `reference/polish.md`. Phase 4: `reference/critique.md` first (show the user the score + top 3
   issues), then `polish`. Then run its detector once on the result: `sh .claude/skills/impeccable/scripts/impeccable detect --json ui/web/src`
   and fix what it flags (or name the deliberate exception).
5. Scope: **only `ui/web/src/**`**. Every quoted text from the plan, every panel and the board stay exactly as they are
   (polish is refinement; ask before changing any copy). `git diff --stat` proves the scope.
6. Re-check: `cd ui/web && npm run build && npm test`, pytest, then `verify N` again; quoted texts must still render exactly.

## 4. Talk entry, then commit
- Append to `docs/talk.md` §7 Build story:
  `**Phase N · <name>** · Was broken: … · Fixed by: <file:line> … · Why it matters: … · Say it: "…"`.
- **Architecture diagram** (`docs/talk.md` §3, mermaid): give every file this phase built its part's class (`door`,
  `guard`, `brain`, `hands`, `store`) instead of `todo`; rename a node to the real file if it differs (e.g. `src/core.py`
  for app kind, `ui/api.py` for UI react) and add a node + one labeled arrow for a new file in the layout (e.g.
  `ui/dashboard.py`). Only files that exist leave grey. SAFE MERMAID (CLAUDE.md): `flowchart LR`, solid labeled arrows,
  quoted labels, no HTML tags. Then `.venv/bin/python scripts/render_docs.py` → `docs/talk.html` + `docs/plan.html`
  (older classrooms without it: copy `$KIT/render_docs.py` to `scripts/` first).
- Last phase only: fill §1–§6 too (see §6 below).
- `git add -A && git commit -q -m "phase N: <name>" && git tag -f phase-N`. The spec and verify.md go in the same commit.

## 5. Hand over, then **STOP**
```
✅ Phase N built · tests X passed · spec R1–Rk verified · committed as phase-N
⚠️ Not working yet: <each ⬜ scenario + the phase that makes it work, e.g. "S1 → phase 2 · S2, S3 → phase 3"; "nothing" when all ✅>
🖥  App: http://localhost:<port>  (refresh the tab)
📄 Spec: docs/specs/phase-N/spec.md · proof: docs/specs/phase-N/verify.md

👀 What changed on screen:  <the plan's "before → after" line>
📊 Scenario board:          S1 ⬜→✅ · S2 ⬜ · S3 ⬜ · bonus ⬜      (from verify.md, real results)

Try it (in the app):
1. `<exact input>` → you should see "<exact text>"
2. …
3. 🚧 `<exact input>` → still: "<stub text>" → fixed in phase N+1     (phases 2–3 only)

🎤 Say it: "<the Build-story sentence>"

Looks right? → `/build` for Phase N+1: <name>      (last phase: → `/rehearse`)
Something off? → tell me what you saw. I add it to the spec as a new R, fix it as "phase N fix" and re-tag.
🔍 Code worth a look (optional): `file.py:LINE` <the one decision>
```
- Try it items come from plan.md. Item 1 is always S1. From phase 3 on, at least one item is a refusal or handoff.
- All numbers are real: "tests X passed" is the last pytest run, and the board comes from verify.md. If anything is red,
  line 1 is `❌ …: <what>`, and the phase is not ticked or tagged.
- **The user reports a mismatch:** first add it to the spec as a new R (with its source = the user's report and today's date)
  and its test, then fix, re-verify, `git commit -am "phase N fix: <what>" && git tag -f phase-N`.

## 6. `docs/talk.md` §1–§6 (last phase, from what was actually built)
- §1 What this is: asked / built / for whom / out of scope, success in the interviewer's words.
- §2 The 3 scenarios as "type X → it does Y", in demo order.
- §3 the architecture diagram (every node a real file, none grey), file map, the S1 trace, **exactly 3 snippets** with `file:line` (the loop, one gated tool, one guard).
  "LLM understands, Python decides."
- §4 Key decisions: 3-5 lines "Chose X over Y because Z". Include "spec-driven: every requirement traced and tested".
- §5 Safety & known gaps. §6 Eval score, production metrics, next week. §7 Tighten into a 1-minute broken → fixed story.
