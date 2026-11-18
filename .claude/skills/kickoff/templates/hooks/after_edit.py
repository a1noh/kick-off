"""PostToolUse hook (Edit | Write | MultiEdit): ruff formats and fixes every Python file Claude edits.

Runs from the kit (the project's .claude/settings.json finds it), so no hook code lands in the project.
It never blocks Claude (always exits 0). Git history is the build log, so nothing else is written.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Read the edited file's path from the hook input and run ruff format + ruff check --fix on it."""
    try:
        path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
    except json.JSONDecodeError:
        return
    ruff = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()) / ".venv" / "bin" / "ruff"
    if path.endswith(".py") and ruff.exists():
        subprocess.run([str(ruff), "format", "-q", path], check=False)
        subprocess.run([str(ruff), "check", "--fix", "-q", path], capture_output=True, check=False)


if __name__ == "__main__":
    main()
