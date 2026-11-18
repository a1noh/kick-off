# claude-kickoff

A Claude Code kit for **2-hour build interviews**: interview → plan → build a working demo (an AI agent or a plain app)
in 4 visible steps → present it. The app comes first: every scenario starts ⬜ and turns ✅ one step at a time. You
approve a code-level plan (every function, the records, scenario 1 step by step) before any code is written; every
requirement traces to your notes, is tested, and is proven by a script. A practice repo holds only the product.

## Use it

**On a computer** (macOS / Linux, or Windows via WSL):
```bash
git clone <this repo> claude-kickoff && cd claude-kickoff && ./install.sh
mkdir ~/interview-practice && cd ~/interview-practice && claude
# then in Claude Code:  /kickoff   (and /demo to learn the flow on a sample)
```
Needs: Claude Code, git, Python 3, and [uv](https://docs.astral.sh/uv/) (`/kickoff` offers to install it).

**On your phone or claude.ai/code** (no install): on GitHub, click **Use this template** → create a repo → open it in
claude.ai/code → `/kickoff`. The skills and hooks come with the repo. Limits there: you can't click the app in a
browser (`spec.py verify N` prints the rendered screen claims instead), and for live AI steps set
the environment variable `GEMINI_API_KEY` in the cloud environment settings and allow `generativelanguage.googleapis.com`.

## The flow
| Time | Command | What happens |
|---|---|---|
| 0:00 | `/kickoff` | sets up the folder and prints a short, fixed welcome (`/kickoff` again = "where am I") |
| learn | `/demo` | fills in a sample interview (bike repair shop), plans it, builds phase 1, explains each step |
| 0:00–0:10 | you | interview with GUIDES (Goal · Users · Inputs · Danger · Edges · Scale) → `notes/raw.md` |
| 0:10 | `/discovery` | notes → `docs/requirements.md` (rules + decisions) + `docs/plan.md` (functions, records, S1 flow, 4 phases) → you approve it |
| 0:15–1:30 | `/build` ×4 | per phase: tests → code → verify → the app updates → local commit + tag → your "Try it" list + diff stat |
| 1:40 | you | code freeze: `.venv/bin/python scripts/demo.py`, then read `docs/talk.md` top to bottom with the app open |

## What a practice folder looks like
```
notes/raw.md   your interview notes (Claude reads, never edits)
data/          the interviewer's files
docs/          requirements.md (what) · plan.md (how: study it) · talk.md (for the client)
src/           the product: agent.py or core.py, tools.py (gated), guards.py, data.py, llm.py
ui/            the screen only: React (api.py + web/, default) or Streamlit app.py
evals/ tests/ scripts/demo.py   scenarios + board, tests, the terminal demo
(the kit's tools, hooks and Impeccable run from the kit: nothing of them is committed)
```

## Safety
- `.env` (your Gemini key) is git-ignored, and a pre-commit hook blocks `.env` files and anything that looks like an
  API key, in every practice folder and in this repo.
- The LLM only extracts fields; every rule is plain Python, and tools re-check their gates.

## Working on the kit
`./install.sh --link` symlinks the skills so edits here are live. Self-test: `python3 .claude/skills/kickoff/tests/selftest.py`
(also runs in CI on every push). The UI is React by default (Node ≥ 18; Streamlit otherwise), designed by the bundled
Impeccable skill (pinned, no hook, telemetry off, run from the kit) after phase 1 and in phase 4: see `.claude/skills/kickoff/CHEATSHEET.md`.
