#!/bin/bash
# Stop hook: runs every time Claude tries to finish a turn.
# If tests fail, or a spec is ungrounded/unverified -> exit 2 -> Claude must fix it before it may stop.
# (Hooks are ENFORCED by Claude Code; CLAUDE.md instructions are only advice.)
PROJECT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
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

if [ -f scripts/spec.py ]; then
  OUT=$("$PY" scripts/spec.py check 2>&1)
  if [ $? -ne 0 ]; then
    echo "Specs are not grounded/verified - fix them before finishing (see docs/specs/_template/spec.md):" >&2
    echo "$OUT" | tail -25 >&2
    exit 2
  fi
fi
exit 0
