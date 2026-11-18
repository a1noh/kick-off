# Cheat sheet: 2-hour build

Lives in the kit only (`<kit>/CHEATSHEET.md`); `/kickoff` prints its path.

## Pre-flight (the day before)
- [ ] Kit self-test: `python3 <kit>/tests/selftest.py` → all passed (`<kit>` = `~/.claude/skills/kickoff` after `install.sh`,
      or `.claude/skills/kickoff` in a repo made from the template)
- [ ] Learn the flow once: empty folder → `claude` → `/kickoff` → `/demo` (sample interview, up to the approved plan)
- [ ] VS Code + the Claude Code extension · `claude` runs in VS Code's terminal (`/ide` connects it)
- [ ] Free Gemini key from https://aistudio.google.com/apikey works (paste it into `.env` right after `/kickoff`;
      on claude.ai/code set it as the environment variable `GEMINI_API_KEY` and allow `generativelanguage.googleapis.com`)
- [ ] Node ≥ 18 for the default React UI (`node -v`; nvm: `nvm install 20 && nvm alias default 20`; or `brew install node@20`).
      Without it `/discovery` falls back to Streamlit. Fill the npm cache once:
      `cp -R <kit>/templates/react /tmp/rw && cd /tmp/rw && npm install && npm run build && npm test`
- [ ] Impeccable (the UI designer) is bundled in the kit, pinned (`<kit>/vendor/impeccable/PINNED`), no hook, and runs
      from the kit: `/build` polishes after phase 1 and critiques + polishes in phase 4. Nothing lands in the project.
- [ ] Other machine: `git clone <your kit repo> && ./install.sh` · phone: GitHub "Use this template" → open the new repo in claude.ai/code

## Minute 0
1. Empty folder → `claude` → `/kickoff` (prints the short welcome) → `/hooks` lists 3 (ruff, tests + kit rules, notes guard)
2. Shift+Tab: **default** (approve each edit) or **accept edits** (faster). `/discovery` ends by asking you to approve plan.md: read Functions (the functions) and Flow (the S1 flow) first.
3. Keep on screen: `notes/raw.md` · the app (from phase 1; `/build` prints its URL) · Source Control `⌃⇧G` → Graph
   (every step commits and tags itself: `kickoff` → `plan` → `phase-1` … `phase-4`)

**Can't see a diagram?** `.venv/bin/python <kit>/templates/render_docs.py` writes `docs/talk.html` (git-ignored), or view
the `.md` on GitHub, which draws mermaid itself.

## Words you'll see
**the app** = 2 tabs: the user's door (chat, upload, Q&A, form) + the **📊 Owner dashboard** · **Scenario board** = the
3 demo stories in the sidebar: ⬜ not built · ❌ broken · ✅ works · **requirement** = a P<n>.R<k> line in plan.md,
traced to your notes, with an exact expected text and a test; `spec.py verify N` proves it · **🚧** = not built yet,
arrives in step N · **guards / gates** = safety checks in plain Python · **src/** = the product · **ui/** = the screen only

## GUIDES + Happy path: ask before you build (answers → notes/raw.md)
- **G**oal: what problem, and what does success look like?
- **U**sers: who uses it, who takes over, and who owns it? What does the owner need to see every day? (→ the Owner dashboard)
- **I**nputs: what data and systems does it touch? (files → `data/`)
- **Happy path**: walk me through one typical case, start to finish, in their words (→ demo scenario 1)
- **D**anger: what can it never get wrong? When does a human take over?
- **E**dges: what are the tricky or messy cases?
- **S**cale + Scope: how much volume? What's in or out for today?

## Timeline
| Time | Do | You |
|---|---|---|
| 0:00–0:15 | Ask GUIDES → notes/raw.md → `/discovery` | Read spec.md, then approve plan.md: functions (Functions), S1 flow (Flow), 4 phases |
| 0:15–0:25 | `/build` phase 1: the whole app shell, every scenario ⬜ | Click around both tabs: this is everything you'll build |
| 0:25–0:50 | `/build` phase 2: scenario 1 ✅ | Do the **Try it** list; watch S1 turn green + the dashboard fill |
| 0:50–1:15 | `/build` phase 3: safety + scenarios 2–3 ✅ | Do the **Try it** list; queue + audit go live |
| 1:15–1:30 | `/build` phase 4: evals + talk | Run evals; read talk.md (client) and plan.md §8 (likely questions) |
| 1:30 | Read `docs/talk.md` with the app open | Click through the 3 scenarios while reading |
| **1:40** | **CODE FREEZE** | No new features |
| 1:40–1:55 | `scripts/demo.py`, then talk.md top to bottom | Practice saying it with the app open |
| 1:55 | Done | |

## Fallback prompts
- **Steer:** `That's not what we want: <what's wrong>. Update docs/plan.md first, then fix it.`
- **Evals:** `Run the eval cases from docs/plan.md end to end. Show a scorecard. Fix only what fails, then re-run.`
- **Checkpoint (if not using /build):** `Run the tests, make sure the app is running, tick the phase, commit + tag, then give me 3 exact inputs to try in the app and what I should see. Stop.`
- **Practice:** `Code freeze. Ask me the questions in plan.md §8 one at a time and critique each answer in 2 lines.`

## Rules for yourself
1. Scope is decided when `docs/plan.md` is approved (**Status:** approved). New ideas go into talk.md §6 "next", not into the build.
2. Do every **Try it** item in the app before the next `/build`, including the 🚧 one (see it broken before it's fixed).
   What you click through is what you can present. The Scenario board must match what `/build` said changed.
3. If a phase goes badly: `git reset --hard phase-<N-1>` (or `plan`) and re-run `/build`. ⚠️ It erases anything not
   committed (save new notes first: `git add notes && git commit -m notes`), and records in `out/` stay: delete
   `out/*.jsonl` so the dashboard starts clean. Every step is tagged:
   `git log --oneline --decorate` shows them, `git diff phase-1 phase-2` shows exactly what a phase added. Nothing is pushed.
4. Code freeze at 1:40 is not optional.
5. Lost? Type `/kickoff` (no folder) inside the classroom: it shows where you are and the next command.
