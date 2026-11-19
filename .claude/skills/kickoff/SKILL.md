---
name: kickoff
description: Create a 2-hour build "classroom" for an AI agent or a plain app (scheduler, dashboard, workflow) in the current folder - UI first (phase 1 is the full app shell with an Owner dashboard and every scenario ⬜ on a Scenario board), then an approved code-level plan and 4 /build phases (traced + tested + verified) turn it ✅. Writes only CLAUDE.md, notes/raw.md, docs/talk.md, .claude/settings.json (hooks that run from the kit: ruff, raw-notes guard, tests + kit rules), .gitignore, pyproject.toml, a src/ + ui/ layout, a Python 3.12 env and git (+ a secrets pre-commit hook); every kit tool stays in the kit. Then prints a fixed short welcome. Inside an existing classroom it prints "where you are". Works from ~/.claude/skills or a repo's .claude/skills. Next: /demo (learn on a sample) or /discovery. Use when the user types /kickoff or asks to set up a timed build.
---

# /kickoff: set up the classroom, then say where we are (same words every time)

Arguments given: `$ARGUMENTS`

**KIT_HOME** = this skill's base directory (shown above as "Base directory for this skill"). It works the same whether
the kit sits in `~/.claude/skills/kickoff` (installed with `install.sh`) or in a repo's `.claude/skills/kickoff`. Export it in every command below: `export KIT_HOME="<that path>"`.

**Consistency rule:** what the user reads at the start comes from `$KIT_HOME/bin/guide.py`, printed **exactly**.
Don't add an intro, a summary, tips or your own version of the guide. The long playbook is the kit's `CHEATSHEET.md` (guide.py prints its path).

## Pick the mode
The classroom always lives in **the current folder**. `DEST` = current working directory. Never ask for a folder path;
any arguments are brief/data files to copy into `data/`.
- **Guide mode:** the folder is already a classroom (`.claude/settings.json` mentions `kickoff/templates/hooks`, or an
  older classroom with `.claude/hooks/`) → change nothing. Older classrooms are not migrated. Run
  `python3 "$KIT_HOME/bin/guide.py" status` and show its output exactly, in a ```text block. Nothing else.
- **Setup mode:** otherwise → the setup steps below.

## Setup steps
1. Allowed in `DEST`: data files, a `.env` (kept as is, so a pasted key survives), and kit files (`.claude/skills/`,
   `README.md`, `LICENSE`, `install.sh`, `.githooks/`, `.github/`, `.gitignore`). Anything else → ask before writing.
   If kit files are present (`install.sh` + `.claude/skills/kickoff/`), ask once: "This folder holds the kit itself.
   Set up a practice classroom here? (Yes for a repo made from the template; No for the kit's own repo.)"
2. `uv`: `command -v uv` or `~/.local/bin/uv`. Missing → ask the user, then `curl -LsSf https://astral.sh/uv/install.sh | sh`;
   if that can't connect, `python3 -m pip install --user uv`.
3. Run the **setup block** below exactly as written, with `KIT_HOME` exported. **Do not change any file contents.**
4. Run the **verify block**. All six checks must print OK. If one fails, fix the cause and re-run; never skip it.
5. If the arguments name brief/data files, copy them into `DEST/data/`.
6. Check that `discovery`, `build` and `demo` sit next to this skill (`$KIT_HOME/../<name>/SKILL.md`). If not, warn.
7. Only if the `code` command exists: if VS Code isn't open on this folder, `code "$DEST"`; then `code -r "$DEST/.env"`
   so the user can paste the Gemini key (never read `.env` yourself). If `code --list-extensions` lacks
   `bierner.markdown-mermaid`, install it.
8. Run `python3 "$KIT_HOME/bin/guide.py" setup` and show its output exactly, in a ```text block. Nothing before or
   after it, except one line if a step above failed or was skipped.

## Setup block
The project gets only its own files (copied from `templates/project/`). Hooks, `spec.py`, `progress.py` and
`check_llm.py` run from the kit: `.claude/settings.json` finds the kit at run time (the repo's
`.claude/skills/kickoff`, else `~/.claude/skills/kickoff`), and the venv's `classroom.pth` (git-ignored) adds `templates/`.
```bash
DEST="$PWD"   # current folder
set -e
if [ -z "${KIT_HOME:-}" ]; then for d in "$PWD/.claude/skills/kickoff" "$HOME/.claude/skills/kickoff"; do [ -d "$d/templates" ] && KIT_HOME="$d" && break; done; fi
KIT="${KIT_HOME:-}/templates"; P="$KIT/project"
for f in spec.py progress.py check_llm.py pre-commit hooks/stop.sh hooks/after_edit.py hooks/guard_raw_notes.py \
  project/CLAUDE.md project/talk.md project/raw.md project/settings.json project/gitignore project/pyproject.toml; do
  [ -f "$KIT/$f" ] || { echo "MISSING kit file $KIT/$f"; exit 1; }
done
cd "$DEST" && mkdir -p .claude data docs notes tests src ui evals scripts
cp "$P/settings.json" .claude/settings.json
cp "$P/gitignore" .gitignore
cp "$P/pyproject.toml" pyproject.toml
cp "$P/CLAUDE.md" CLAUDE.md
cp "$P/talk.md" docs/talk.md
[ -f notes/raw.md ] || cp "$P/raw.md" notes/raw.md
[ -f .env ] || printf '%s\n' "# Paste your free Gemini API key after the = (get one at https://aistudio.google.com/apikey). Never commit this file." \
  "GEMINI_API_KEY=" "GEMINI_MODEL=gemini-flash-lite-latest" > .env
UV="$(command -v uv || echo "$HOME/.local/bin/uv")"
"$UV" venv -q -p 3.12 .venv || "$UV" venv -q .venv   # 2nd try: the system Python
"$UV" pip install -q --python .venv/bin/python pytest==8.3.3 ruff==0.8.4 python-dotenv==1.0.1 requests==2.32.3
SITE="$(.venv/bin/python -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')"
printf '%s\n' "$DEST/src" "$DEST/ui" "$DEST" "$KIT" > "$SITE/classroom.pth"   # flat imports + the kit's progress.py
git init -q 2>/dev/null || true
cp "$KIT/pre-commit" "$(git rev-parse --git-path hooks)/pre-commit" && chmod +x "$(git rev-parse --git-path hooks)/pre-commit"
git add -A && git commit -q -m "kickoff: classroom (CLAUDE.md, raw notes, talk template, kit hooks)"
git tag -f kickoff >/dev/null
echo "SETUP OK: $DEST"
```

## Verify block
Runs each hook exactly as Claude Code will (the command from `.claude/settings.json`), so it proves the kit is found.
```bash
DEST="${DEST:-$PWD}"; cd "$DEST" && export CLAUDE_PROJECT_DIR="$PWD" && KIT="$KIT_HOME/templates"
hook() { .venv/bin/python -c "import json,sys; print(json.load(open('.claude/settings.json'))['hooks'][sys.argv[1]][0]['hooks'][0]['command'])" "$1"; }
printf 'import os\ndef probe( x ):\n  return x\n' > zz_probe.py
echo '{"tool_name":"Write","tool_input":{"file_path":"'"$PWD"'/zz_probe.py","content":"x"}}' | bash -c "$(hook PostToolUse)"
grep -q "def probe(x):" zz_probe.py && ! grep -q "import os" zz_probe.py && echo "OK 1/6 ruff hook formats code (run from the kit)" || echo "FAIL ruff hook"
echo '{"tool_name":"Edit","tool_input":{"file_path":"'"$PWD"'/notes/raw.md"}}' | bash -c "$(hook PreToolUse)" 2>/dev/null; [ $? -eq 2 ] && echo "OK 2/6 raw notes are read-only" || echo "FAIL raw notes guard"
printf 'def test_x():\n    assert False\n' > tests/test_zz_probe.py
echo '{}' | bash -c "$(hook Stop)" 2>/dev/null; [ $? -eq 2 ] && echo "OK 3/6 stop hook blocks failing tests" || echo "FAIL stop hook"
git check-ignore -q .env && grep -q "^GEMINI_API_KEY=" .env && echo "OK 4/6 .env exists and is git-ignored" || echo "FAIL .env"
T="$(mktemp -d)"; mkdir -p "$T/docs"
printf -- '**Status:** approved 2026-01-01\n## 6. Phases\n- [x] Phase 1: probe\n  - **Requirements:**\n    - **P1.R1** · probe\n      - Traces to: my gut\n      - Acceptance: works\n      - Test: tests/test_p1.py::test_r1\n' > "$T/docs/plan.md"
(cd "$T" && "$DEST/.venv/bin/python" "$KIT/spec.py" check >/dev/null); [ $? -eq 1 ] && .venv/bin/python "$KIT/spec.py" check >/dev/null && echo "OK 5/6 spec checker rejects an ungrounded requirement" || echo "FAIL spec checker"
rm -rf "$T"
! git ls-files | grep -Eq 'spec\.py|progress\.py|check_llm|\.claude/hooks|BUILD_LOG|CHEATSHEET|docs/specs' && .venv/bin/python -c "import progress" && echo "OK 6/6 no kit scaffolding in the repo; progress imports from the kit" || echo "FAIL kit scaffolding"
NODE_MAJOR="$(node -v 2>/dev/null | sed 's/^v\([0-9]*\).*/\1/')"; [ "${NODE_MAJOR:-0}" -ge 18 ] && echo "NOTE node $(node -v): React UI ready" || echo "NOTE node ${NODE_MAJOR:-missing}: the React UI needs Node >= 18: install it before /build"
rm -f zz_probe.py tests/test_zz_probe.py && rm -rf .pytest_cache .ruff_cache tests/__pycache__
```
