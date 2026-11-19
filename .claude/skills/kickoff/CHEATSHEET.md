# Cheat sheet: 2-hour build

Lives in the kit only (`<kit>/CHEATSHEET.md`); `/kickoff` prints its path.

## Pre-flight (the day before)
- [ ] Kit self-test: `python3 <kit>/tests/selftest.py` → all passed (`<kit>` = `~/.claude/skills/kickoff` after `install.sh`)
- [ ] Learn the flow once: empty folder → `claude` → `/kickoff` → `/demo` (sample interview, up to the approved plan)
- [ ] VS Code + the Claude Code extension · `claude` runs in VS Code's terminal (`/ide` connects it)
- [ ] Free Gemini key from https://aistudio.google.com/apikey works (paste it into `.env` right after `/kickoff`)
- [ ] Node ≥ 18 for the React UI on localhost (`node -v`; nvm: `nvm install 20 && nvm alias default 20`; or `brew install node@20`).
      Fill the npm cache once:
      `cp -R <kit>/templates/react /tmp/rw && cd /tmp/rw && npm install && npm run build && npm test`
- [ ] Other machine: `git clone <your kit repo> && ./install.sh`

## Minute 0
1. Empty folder → `claude` → `/kickoff` (prints the short welcome) → `/hooks` lists 3 (ruff, tests + kit rules, notes guard)
2. Shift+Tab: **default** (approve each edit) or **accept edits** (faster). `/discovery` ends by asking you to approve plan.md: read §2 Files, §3 How it works and §4 Functions first.
3. Keep on screen: `notes/raw.md` · the app (from phase 1; `/build` prints its URL) · Source Control `⌃⇧G` → Graph
   (every step commits and tags itself: `kickoff` → `plan` → `phase-1` … `phase-4`)

**See the diagrams:** open `docs/diagrams/diagrams.html` in a browser (every diagram on one page, kept up to date by the kit).

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
| 0:00–0:15 | Ask GUIDES → notes/raw.md → `/discovery` | Read spec.md, then approve plan.md: the files (§2), the diagram (§3), every function (§4), 4 phases |
| 0:15–0:25 | `/build` phase 1: the whole app shell, every scenario ⬜ | Click around both tabs: this is everything you'll build |
| 0:25–0:50 | `/build` phase 2: scenario 1 ✅ | Do the **Try it** list; watch S1 turn green + the dashboard fill |
| 0:50–1:15 | `/build` phase 3: safety + scenarios 2–3 ✅ | Do the **Try it** list; queue + audit go live |
| 1:15–1:30 | `/build` phase 4: evals + talk | Run evals; read talk.md (client) and plan.md §8 (likely questions) |
| 1:30 | Read `docs/talk.md` with the app open | Click through the 3 scenarios while reading |
| **1:40** | **CODE FREEZE** | No new features |
| 1:40–1:55 | `scripts/demo.py`, then talk.md top to bottom | Practice saying it with the app open |
| 1:55 | Done | |

## Changing or adding something (one door: say it to `/build`)
| When | You type | What happens |
|---|---|---|
| Phases still unbuilt | `/build also show the phone number` | spec.md rule → plan.md requirement + function block → test → code, inside the phases not built yet |
| Everything built | `/build add a "Most asked" panel` | the same, as **Phase 5** (6, …): you approve it, it's built, and talk.md §1–§6 + plan.md §8 are rewritten |

You never edit `notes/raw.md` again and never re-run `/discovery` for a change (only for a new round of interview notes).

`spec.py check` won't pass with a rule that has no requirement, a built phase with no Build-story entry, or a finished
build whose talk.md doesn't cover the last phase. Every handover's 📚 lines list what each doc gained (+) or reworded (~).

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
