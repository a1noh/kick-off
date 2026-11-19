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
  to approve it" and stop. Never approve it yourself (the only approval `/build` records is the user's yes to a new phase, §0b).
- **The user said what they want with the command** (`/build also show the phone number`, or a message asking for a
  change): that is a change request, see **0b** first.
- Take the **first unticked phase** (`- [ ] Phase N: …`). If all are ticked and nothing was asked for, say "All built.
  Before you present: `.venv/bin/python scripts/demo.py`, then read docs/talk.md top to bottom with the app open. To add
  or change something: `/build <what you want>`." and stop.
- Say in one line which phase you're building, quoting its `On screen (before → after)` line.
- Open questions in spec.md that this phase depends on → ask them now, record the answers, then continue.

## 0b. A change the user asks for in words (the only door for changes: the user never edits the notes or re-runs /discovery)
The docs change **first**, in this order, then the code. The user's words are the source: quote them.
1. **spec.md**: what the product must now do, in plain English: new rules `B<n> … · decided with user <date>: "<their
   words>"`, a scenario or eval case when a reply changes, the §3 panel or endpoint table, decisions for anything
   ambiguous (ask with AskUserQuestion only when the answer changes what you build; otherwise take the careful option
   and record it). New ids continue the numbering; never renumber or delete one. A rule the change alters keeps its id.
2. **plan.md**, everywhere it touches: §1, §2 Files, the §3 diagram, each new or changed §4 function block (Does, In,
   Out), §5 Records, §6 Evals, and the requirements with `Traces to: B<n> · user <date>: "<their words>"`. If the change
   makes an already-built line false (a count, a list, a reply's text), make it true everywhere it is quoted: the
   requirement's Acceptance (add ` · updated in phase N` at the end of that line), the Try-it lines of earlier
   phases, spec.md's scenarios and eval rows, and the §4/§6 examples. The docs never keep a line that is no longer
   true. The old **tests and eval expectations** change later, as the first step of building the phase (tests first:
   they go red, then the code turns them green), so the docs commit stays green.
3. **Where it lands:**
   - phases still unbuilt → fold it into them (say which);
   - everything built → it becomes the next phase, **Phase 5** (6, …), with the same four parts (On screen, Builds,
     Try it, Requirements). Its Builds line names each built function it alters as "changes `name`" (until the phase
     is built, `spec.py check` only warns that plan and code differ there). A new board row is written
     `Board S4 new→✅`, a new panel `Most asked new→live`.
4. Run `spec.py check` → `SPEC OK`, then show the user what was added: the 📚 lines of `spec.py changes <the new phase's number>`
   (it compares with the last built phase) plus two or three plain sentences. **A new phase needs their yes:** set `**Status:** draft`, ask
   "Build Phase N: <name>?" (Approve / Change something), and on Approve set `**Status:** approved <today>` and commit
   `plan: phase N added (<their words, short>)`. A change folded into unbuilt phases needs no question.
5. Then build as usual from §1 below. The last phase always ends with the client docs rewritten (§4).

## 1. Read the phase, change the plan only on purpose
- The phase's **Requirements** (P<n>.R<k>) are the spec: each has `Traces to`, `Acceptance` (exact "quoted" value) and `Test`.
- The code must match plan.md: **§2 Files**, every `####` function block in **§4 Functions** and **§6 Evals** (signature,
  docstring line 1, **Does**, In, Out) and **§5 Records**. Each function's **Does** steps are its logic, in order: build
  exactly those paths, no more.
- Need a signature, file or record the plan doesn't have, or a different one? **Edit plan.md first** (§2 Files, a §4 function block, §5 Records, plus a
  requirement if behavior changes), keep it minimal, and list it in the handover as `📐 Plan changed: …`.
- A change the user asks for while you build → §0b. A fix to something that should already work (a bug, a layout
  fix) needs no rule: just a requirement sourced to their words, and its test.
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
  - Required tests: `test_stub_replies_never_show_green` and `tests/test_screen.py::test_screen_matches_plan_and_board`
    (the kit's file, copied below): give each the docstring citing the requirement the plan maps to it (`"""plan.md P1.R3: …"""`).
  - **The screen** (the kit's React template):
    `cp $KIT/react/api_template.py ui/api.py; mkdir -p ui/web; for f in package.json vite.config.js index.html src; do cp -R $KIT/react/$f ui/web/; done; cp $KIT/react/test_screen_api.py tests/test_screen.py`,
    then `uv pip install --python .venv/bin/python fastapi==0.115.6 uvicorn==0.32.1 httpx==0.28.1` and
    `(cd ui/web && npm install --no-audit --no-fund && npm run build)`. Fill `ui/api.py`'s TITLE, TABS, PANELS, WIDE
    and SHOWS (spec.md §3 table); from phase 2 set `RESET` to the plan's reset function (the Reset button only shows once it is set). The guide sidebar comes with the template: don't rewrite it. `npm test` must pass.
- **API shape** (plan.md §1 says `API`): phase 1 also builds `src/service.py`: `make_router(extract, out_dir)` with
  **every** endpoint answering `501` and `{"status": "not_built", "message": "🚧 <feature> arrives in phase N."}`, and
  the console (each instance owns its app, so the board and the tests pass an offline extractor and a temp folder):
  ```python
  class Console:
      """<its plan.md line>"""

      def __init__(self, extract: Callable = extract, out_dir: Path = OUT) -> None:
          """<its plan.md line>"""
          self.app = FastAPI()
          self.app.include_router(make_router(extract, out_dir))

      def reply(self, line: str) -> str:
          """<its plan.md line>"""
          method, _, rest = line.strip().partition(" ")
          path, brace, body = rest.partition(" {")
          if method.upper() not in ("GET", "POST", "PUT", "DELETE") or not path.startswith("/"):
              return '400\n{"error": "Type a request line, like GET /v1/<an endpoint>."}'
          response = TestClient(self.app).request(method.upper(), path, json=json.loads(brace.strip() + body) if brace else None)
          return f"{response.status_code}\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}"
  ```
  In `ui/api.py`: `app.include_router(make_router(...))`, `config["agent_factory"] = Console`,
  `TABS[0] = "🔌 API console"`, and `DOOR = {"name": "API console", "fresh": "Clear", "placeholder": "GET /v1/…"}`; the
  board plays its request lines through `Console` too. A reply is "not built" when it contains 🚧. Route parameters are
  `str` and `src/core.py` checks them (the spec's `400`, never the framework's `422`). From phase 2 each route calls its
  `src/core.py` function. Phase 4's `evals/run.py` prints the eval cases **and** the labelled-query scores
  (precision@k, recall@k per query and on average; with a keyword reader, both readers side by side), and you replace
  the Scale paragraph's estimates with numbers you measured (time one request with and without the model).
- **Later phases** replace stubs and turn placeholders live. **Never remove a panel or a board row.** An owner action
  calls a gated function in `src/tools.py` and is audited. From phase 2, keep `scripts/demo.py` running.
- One short ★ Insight per file: *why*, not what.

## 3. Verify (nothing goes back to the user until all of this is green)
1. **Tick the phase** in plan.md (`- [x] Phase N: …`) first: the tests and the screen checks read the ticks, so a test like
   "phase 3 unticked → 🚧 stub" is only true once the plan says what is built. If anything below stays red, untick it
   before you stop. A requirement that is proved by the docs ("talk.md is filled") needs those docs written first
   (step 5). Then `.venv/bin/python -m pytest -q tests`: green.
2. From phase 2: `.venv/bin/python scripts/demo.py` (live Gemini if the plan uses it; key missing or Gemini down → say so, continue).
   **A live run that fails is a finding, not a number to tune away.** Fix the prompt with a general rule (what the
   field means), never by pasting the failing input into it; re-run at least twice; and report every prompt change with
   the score before and after. talk.md §6 states the score as the last run in `out/evals.json` plus how it varied
   ("10/10 live; 9/10 on 2 of 7 runs before the prompt fix"), and names the failures that were the safe kind.
3. (The tick from step 1 stays.)
4. `.venv/bin/python $KIT/spec.py verify N`: runs the phase's requirement tests and its Try-it screen claims against
   the rendered screen, prints them, and must end `VERIFY OK`. A ❌ claim means the plan, the screen and the guide
   disagree: fix the code (or, if the plan line is wrong, fix the plan and say so), then repeat from step 1.
5. Write the docs for this phase (§4: the Build-story entry; in the last phase also the client sections), then
   `.venv/bin/python $KIT/spec.py check` → `SPEC OK` (the Stop hook enforces it too). It also holds the three docs
   together: every spec.md rule B<n> has a requirement, every ticked phase has its Build-story entry, and once every
   phase is ticked talk.md says `**Covers:** phases 1–<last>` and §8 is answered. Read its `WARN` lines: a file over
   ~150 lines or a function over ~30 is a hint to split or simplify; a function never named in talk.md or §8 is one
   the user can't present yet.
6. The app is running. **React:** rebuild if `ui/web/` changed (`cd ui/web && npm run build`). If `.app.pid` is alive,
   restart it (uvicorn doesn't reload Python). Else take the first free port from 8501 to 8510 (`lsof -ti tcp:$P` empty),
   run `.venv/bin/uvicorn api:app --app-dir ui --port $P > out/app.log 2>&1 &`, save `echo $! > .app.pid; echo $P > .app.port`,
   check `curl -s localhost:$P/api/screen` returns JSON, `open http://localhost:$P`.

## 4. Docs for this phase, then commit (local only)
- Append to `docs/talk.md` §7 Build story: `**Phase N · <name>** · Was broken: … · Fixed by: `function()` … · Why it
  matters: … · Say it: "…"`. Name functions, never `file:line` (`spec.py check` rejects it: line numbers go stale).
- A new product file this phase needs is added to plan.md §2 Files **and** to the §3 diagram first, with its §4 function blocks (`📐 Plan changed`):
  `spec.py check` fails when a product file has no box.
- **The last phase only** (phase 4; after a later feature, phase 5, 6, …: the same step runs again), from what was
  actually built. On a later run **rewrite, don't append**: re-read every section against spec.md and plan.md so the
  new feature shows up in the demo, the decisions, the limits and the questions. Then set talk.md's
  `**Covers:** phases 1–<last>` line:
  - `docs/talk.md` §1–§6, for the client: the problem in their words (spec.md), the 3 scenarios as "type X →
    it does Y", how it works (plan.md §3's diagram copied as is, "LLM understands, Python decides", a pointer to plan.md
    §4 for each function), 3–5 decisions
    citing B<n>/D<n>, safety & known limits naming the function that enforces each, eval score + production metrics +
    next week. §7 gets a 1-minute version at the top.
  - plan.md **§8 Likely questions**: 8–10 questions a client or interviewer will ask about **this** build, each
    answered in 1–2 lines naming its function (cover the list in the template: why an LLM, prompt injection, a case the
    guard misses, offline board vs live evals, concurrency/scale, cost + model, the next fix), with
    `**Covers:** phases 1–<last>` under the heading (`spec.py check` holds it to the last phase, like talk.md's).
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
<the output of `.venv/bin/python $KIT/spec.py changes N`, exactly (run it before the commit moves the tag's base):>
🧩 Added in phase N (code vs. <plan | phase-(N-1)>)   every function now in the code that wasn't (+) or changed (~),
   src/rules.py   + why_not_approve — can this manager approve it?        with its title from plan.md
   See the code: git diff <plan | phase-(N-1)> phase-N -- src/ ui/*.py evals/
📚 Docs since <plan | phase-(N-1)>                    what each doc gained: rules, requirements, functions, entries
   docs/spec.md   + B8, E11        (+ new · ~ reworded)
   docs/plan.md   + P2.R9, ~ dashboard
🔜 Coming in phase N+1: <name>   its On screen line, then every plan function still to write

👀 What changed on screen:  <the plan's "before → after" line>
📊 Scenario board:          S1 ⬜→✅ · S2 ⬜ · S3 ⬜ · bonus ⬜      (real results)

Try it (in the app):
1. `<exact input>` → you should see "<exact text>"
2. …
3. 🚧 `<exact input>` → still: "<stub text>" → fixed in phase N+1     (phases 2–3 only)

🎤 Say it: "<the Build-story sentence>"

Looks right? → `/build` for Phase N+1: <name>
   (last phase: Before you present: `.venv/bin/python scripts/demo.py`, then read docs/talk.md top to bottom with the app open.)
Something off? → tell me what you saw. I add it as a requirement, fix it as "phase N fix" and re-tag.
```
- Try it items come from plan.md. Item 1 is always S1. From phase 3 on, at least one is a refusal or handoff.
- All numbers are real (the last pytest run, the verify output, the real changed-file list from git). The 🧩 / 📚 / 🔜
  lines are pasted from `spec.py changes N` as printed, never written by hand. If anything is red, line 1 is
  `❌ …: <what>`, and the phase is not ticked or tagged.
- **The user reports a mismatch:** add a requirement (`Traces to: user <date>: "<their report>"`) and its test (if it
  changes what the product should do, it is a scope change: §1, spec.md rule first), then
  fix, re-verify, `git add -A && git commit -q -m "phase N fix: <what>" && git tag -f phase-N` (local, never pushed), and
  list that fix's changed files the same way.
