#!/bin/bash
# Stop hook: runs every time Claude tries to finish a turn, from the kit (nothing is copied into the project).
# Tests failing, or plan.md / the code breaking a rule (scripts: spec.py check) -> exit 2 -> Claude must fix it first.
# (Hooks are ENFORCED by Claude Code; CLAUDE.md instructions are only advice.)
PROJECT="${CLAUDE_PROJECT_DIR:-$PWD}"
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$PROJECT/.venv/bin/python"
unset __PYVENV_LAUNCHER__   # macOS python3 leaks this; it breaks the venv python

# Avoid an endless loop: if Claude is already continuing because of this hook, let it stop.
INPUT=$(cat)
if echo "$INPUT" | "$PY" -c "import json,sys; sys.exit(0 if json.load(sys.stdin).get('stop_hook_active') else 1)" 2>/dev/null; then
  exit 0
fi

cd "$PROJECT" || exit 0

if ls tests/test_*.py >/dev/null 2>&1; then
  OUT=$("$PY" -m pytest -q tests 2>&1)
  if [ $? -ne 0 ]; then
    echo "Tests are failing - fix them before finishing:" >&2
    echo "$OUT" | tail -25 >&2
    exit 2
  fi
fi

OUT=$("$PY" "$KIT/spec.py" check 2>&1)
if [ $? -ne 0 ]; then
  echo "plan.md or the code breaks a kit rule - fix it before finishing (CLAUDE.md: Plan-driven, Coding standards):" >&2
  echo "$OUT" | tail -25 >&2
  exit 2
fi
exit 0
