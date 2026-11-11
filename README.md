# claude-kickoff

A Claude Code kit for **2-hour build interviews**: interview → plan → build a working demo (an AI agent or a plain app)
in 4 visible steps → present it. The app comes first: every scenario starts ⬜ and turns ✅ one step at a time, and every
step is built from a written spec that traces each line to your interview notes, is tested, and is proven by a script.

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
browser (check each step in `docs/specs/phase-N/verify.md`, which shows the rendered screen), and for live AI steps set
the environment variable `GEMINI_API_KEY` in the cloud environment settings and allow `generativelanguage.googleapis.com`.

## The flow
| Time | Command | What happens |
|---|---|---|
| 0:00 | `/kickoff` | sets up the folder and prints a short, fixed welcome (`/kickoff` again = "where am I") |
| learn | `/demo` | fills in a sample interview (bike repair shop), plans it, builds phase 1, explains each step |
| 0:00–0:10 | you | interview with GUIDES (Goal · Users · Inputs · Danger · Edges · Scale) → `notes/raw.md` |
| 0:10 | `/discovery` | notes → `docs/plan.md`: 3 demo scenarios, rules traced to your notes, 4 phases with "Try it" lines |
| 0:15–1:30 | `/build` ×4 | per phase: spec → tests → code → verify → the app updates → commit + tag → your "Try it" list |
| 1:40 | `/rehearse` | code freeze, run the scenarios, practice the talk, mock interview questions |

## What a practice folder looks like
```
notes/raw.md   your interview notes (Claude reads, never edits)
data/          the interviewer's files
docs/          plan.md · talk.md · specs/phase-N/{spec.md, verify.md}
src/           the product: agent.py or core.py, tools.py (gated), guards.py, data.py, llm.py
ui/            the screen only: Streamlit app.py (or React: api.py + web/)
evals/ tests/ scripts/   scenarios + board, tests, spec checker + demo
```

## Safety
- `.env` (your Gemini key) is git-ignored, and a pre-commit hook blocks `.env` files and anything that looks like an
  API key, in every practice folder and in this repo.
- The LLM only extracts fields; every rule is plain Python, and tools re-check their gates.

## Working on the kit
`./install.sh --link` symlinks the skills so edits here are live. Self-test: `python3 .claude/skills/kickoff/tests/selftest.py`
(also runs in CI on every push). Optional React UI mode and Impeccable (pinned, opt-in, no hook): see `CHEATSHEET.md`
inside a practice folder.
