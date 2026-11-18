---
name: build
description: Build the next unticked phase of an APPROVED docs/plan.md in a /kickoff classroom - refuses a draft plan; reads the phase's requirements (P<n>.R<k>, each traced, quoted, with a named test) and the files, functions and records from plan.md, writes the tests first, then the code (following CLAUDE.md's Coding standards), then verifies (pytest + the kit's spec.py verify N renders the real screen, spec.py check enforces plan + standards). UI first (React via ui/api.py + ui/web/ on localhost; phase 1 = full app shell, board all ⬜, honest 🚧 stubs), each phase visibly turns features ✅. Keeps the app running, adds a Build-story entry, commits + tags locally (never pushes), hands over a "Try it" checklist and every changed file, stops. One phase per call. Use when the user types /build.
---

# /build: approved plan → tests → code → verify → the user tries it

Two goals, in order: **(1) a working build**, **(2) the user understands it and can present it**. The user learns by
**using the product**. The whole screen exists from phase 1, everything starts ⬜ / 🚧, and each phase turns something ✅.

**No intuition.** Everything you build is a requirement in `docs/plan.md` (traced to `docs/spec.md`, `raw.md` or
`data/`). If you need something no source says, **ask the user** (AskUserQuestion) and write the answer down first
(spec.md decision + a plan requirement). The plan comes before the code; the proof is printed by a script.

**Paths:** `KIT` = `../kickoff/templates` next to this skill's base directory. Kit tools run from there, in the project
folder, and are never copied into it: `.venv/bin/python $KIT/spec.py check | verify N`. `progress` imports through the
venv's `classroom.pth`. Product layout and rules: the project's `CLAUDE.md` (this skill doesn't restate its Coding standards).

## 0. Check
- `docs/plan.md` must exist with phase checkboxes. If not, say "run /discovery first" and stop.
- **Approval gate:** if its `**Status:**` line isn't `approved <date>`, say "plan.md is still a draft: re-run /discovery
  to approve it" and stop. Never approve it yourself.
- Take the **first unticked phase** (`- [ ] Phase N: …`). If all are ticked, say "All built. Before you present:
  `.venv/bin/python scripts/demo.py`, then read docs/talk.md top to bottom with the app open." and stop.
- Say in one line which phase you're building, quoting its `On screen (before → after)` line.
- Open questions in spec.md that this phase depends on → ask them now, record the answers, then continue.

## 1. Read the phase, change the plan only on purpose
- The phase's **Requirements** (P<n>.R<k>) are the spec: each has `Traces to`, `Acceptance` (exact "quoted" value) and `Test`.
- The code must match plan.md: **§2 Files**, every `####` function block in **§4 Functions** and **§6 Evals** (signature,
  docstring line 1, **Does**, In, Out) and **§5 Records**. Each function's **Does** steps are its logic, in order: build
  exactly those paths, no more.
- Need a signature, file or record the plan doesn't have, or a different one? **Edit plan.md first** (§2 Files, a §4 function block, §5 Records, plus a
  requirement if behavior changes), keep it minimal, and list it in the handover as `📐 Plan changed: …`.
- A scope change the user asks for → a new requirement with `Traces to: user <date>: "<their words>"` (no re-approval).
- Run `.venv/bin/python $KIT/spec.py check` before coding: the only failures allowed now are this phase's missing tests.

## 2. Tests from the requirements, then code
- Write each requirement's test first, with the name it gives and a docstring citing it (`"""plan.md P2.R3: …"""`).
  Assert the **quoted** value exactly. **Tests stay true in later phases:** read the plan's ticks instead of hard-coding
  "still broken" (e.g. "panel shows ⬜ iff its phase isn't ticked", "a 🚧 reply names an unticked phase").
- Then the code: only what the requirements ask for, in the files plan.md §2 names, following CLAUDE.md **Coding standards**
  (file docstring with its place in the system, a docstring on every function, line 1 = its plan.md function block's line).
- **Phase 1 = the app shell, nothing else:**
  - Tab 1 = the user's door. Tab 2 = **📊 Owner dashboard** (KPIs, domain view, queue, audit, eval score), read-only.
    Panels not live yet show `⬜ <panel>: arrives in phase N`.
  - **Scenario board** with **3 states** (⬜ not built: every reply is a 🚧 stub and sub-checks are not evaluated ·
    ❌ fail · ✅ pass), computed offline by `evals/scenarios.py` `run_all(extractor) -> list[Result]`
    (`Result.state`, `Result.checks: [(label, bool | None)]`), cached on file mtimes. A "did *not* happen" check is
    vacuously true on a stub, so it is only evaluated after a real reply.
  - A stub `src/agent.py` (app: `src/core.py`) with its final interface from plan.md; every reply is `🚧 <feature> arrives in
    phase N.` and never claims success or shows data. No `llm.py` / `data.py` yet.
  - Required tests: `test_stub_replies_never_show_green` and `tests/test_screen.py::test_screen_matches_plan_and_board`.
  - **The screen** (the kit's React template):
    `cp $KIT/react/api_template.py ui/api.py; mkdir -p ui/web; cp -R $KIT/react/{package.json,vite.config.js,index.html,src} ui/web/; cp $KIT/react/test_screen_api.py tests/test_screen.py`,
    then `uv pip install --python .venv/bin/python fastapi==0.115.6 uvicorn==0.32.1 httpx==0.28.1` and
    `(cd ui/web && npm install --no-audit --no-fund && npm run build)`. Fill `ui/api.py`'s TITLE, TABS, PANELS, WIDE
    and SHOWS (spec.md §3 table). The guide sidebar comes with the template: don't rewrite it. `npm test` must pass.
- **Later phases** replace stubs and turn placeholders live. **Never remove a panel or a board row.** An owner action
  calls a gated function in `src/tools.py` and is audited. From phase 2, keep `scripts/demo.py` running.
- One short ★ Insight per file: *why*, not what.

## 3. Verify (nothing goes back to the user until all of this is green)
1. `.venv/bin/python -m pytest -q tests`: green.
2. From phase 2: `.venv/bin/python scripts/demo.py` (live Gemini if the plan uses it; key missing or Gemini down → say so, continue).
3. **Tick the phase** in plan.md (`- [x] Phase N: …`): the screen checks must see the after-tick state.
4. `.venv/bin/python $KIT/spec.py verify N`: runs the phase's requirement tests and its Try-it screen claims against
   the rendered screen, prints them, and must end `VERIFY OK`. A ❌ claim means the plan, the screen and the guide
   disagree: fix the code (or, if the plan line is wrong, fix the plan and say so), then repeat from step 1.
5. `.venv/bin/python $KIT/spec.py check` → `SPEC OK` (the Stop hook enforces it too). Read its `WARN` lines: a file over
   ~150 lines or a function over ~30 is a hint to split or simplify, per the Coding standards.
6. The app is running. **React:** rebuild if `ui/web/` changed (`cd ui/web && npm run build`). If `.app.pid` is alive,
   restart it (uvicorn doesn't reload Python). Else take the first free port from 8501 to 8510 (`lsof -ti tcp:$P` empty),
   run `.venv/bin/uvicorn api:app --app-dir ui --port $P > out/app.log 2>&1 &`, save `echo $! > .app.pid; echo $P > .app.port`,
   check `curl -s localhost:$P/api/screen` returns JSON, `open http://localhost:$P`.

## 4. Talk entry, then commit (local only)
- Append to `docs/talk.md` §7 Build story: `**Phase N · <name>** · Was broken: … · Fixed by: `function()` … · Why it
  matters: … · Say it: "…"`. Name functions, never `file:line` (`spec.py check` rejects it: line numbers go stale).
- A new product file this phase needs is added to plan.md §2 Files **and** to the §3 diagram first, with its §4 function blocks (`📐 Plan changed`):
  `spec.py check` fails when a product file has no box.
- **Phase 4 only**, from what was actually built:
  - `docs/talk.md` §1–§6, for the client: the problem in their words (spec.md), the 3 scenarios as "type X →
    it does Y", how it works (plan.md §3's diagram copied as is, "LLM understands, Python decides", a pointer to plan.md
    §4 for each function), 3–5 decisions
    citing B<n>/D<n>, safety & known limits naming the function that enforces each, eval score + production metrics +
    next week. §7 gets a 1-minute version at the top.
  - plan.md **§8 Likely questions**: 8–10 questions a client or interviewer will ask about **this** build, each
    answered in 1–2 lines naming its function (cover the list in the template: why an LLM, prompt injection, a case the
    guard misses, offline board vs live evals, concurrency/scale, cost + model, the next fix).
- One commit per phase, its body listing every changed file, then the tag:
  `git add -A && { echo "phase N: <name>"; echo; git diff --cached --name-status; } | git commit -q -F - && git tag -f phase-N`.
  **Never push**: commits stay local so every phase can be diffed (`git diff <plan | phase-(N-1)> phase-N`).

## 5. Hand over, then **STOP**
```
✅ Phase N built · tests X passed · P<N>.R1–R<k> verified · committed as phase-N (local, not pushed)
⚠️ Not working yet: <each ⬜ scenario + the phase that makes it work; "nothing" when all ✅>
🖥  App: http://localhost:<port>  (refresh the tab)
📁 Files: <n> in src/, each explained in plan.md §4 · every function documented
📐 Plan changed: <each file, function, record or requirement change, or "nothing">
📄 Changed files (git diff --name-status <plan | phase-(N-1)> phase-N), every one, A = added · M = changed · D = deleted:
   A src/tools.py
   M docs/plan.md
   …  (ui/web/ template files as one line: "A ui/web/ (15 files, kit React template)")
   See any file's change: git diff <plan | phase-(N-1)> phase-N -- <file> · or VS Code Source Control → Graph

👀 What changed on screen:  <the plan's "before → after" line>
📊 Scenario board:          S1 ⬜→✅ · S2 ⬜ · S3 ⬜ · bonus ⬜      (real results)

Try it (in the app):
1. `<exact input>` → you should see "<exact text>"
2. …
3. 🚧 `<exact input>` → still: "<stub text>" → fixed in phase N+1     (phases 2–3 only)

🎤 Say it: "<the Build-story sentence>"

Looks right? → `/build` for Phase N+1: <name>
   (phase 4: Before you present: `.venv/bin/python scripts/demo.py`, then read docs/talk.md top to bottom with the app open.)
Something off? → tell me what you saw. I add it as a requirement, fix it as "phase N fix" and re-tag.
```
- Try it items come from plan.md. Item 1 is always S1. From phase 3 on, at least one is a refusal or handoff.
- All numbers are real (the last pytest run, the verify output, the real changed-file list from git). If anything is red, line 1 is
  `❌ …: <what>`, and the phase is not ticked or tagged.
- **The user reports a mismatch:** add a requirement (`Traces to: user <date>: "<their report>"`) and its test, then
  fix, re-verify, `git add -A && git commit -q -m "phase N fix: <what>" && git tag -f phase-N` (local, never pushed), and
  list that fix's changed files the same way.
