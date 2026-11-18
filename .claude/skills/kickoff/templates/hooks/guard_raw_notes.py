"""PreToolUse hook (Edit | Write | MultiEdit): notes/raw.md belongs to the user.

Claude may read it but never change it. Exit 2 blocks the edit and tells Claude why.
Runs from the kit; the project is $CLAUDE_PROJECT_DIR (or the current folder).
"""

import json
import os
import sys
from pathlib import Path


def main() -> int:
    """Return 2 (block) when the edit targets notes/raw.md, else 0."""
    try:
        path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
    except json.JSONDecodeError:
        return 0
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()
    if path and Path(path).resolve() == project / "notes" / "raw.md":
        print(
            "notes/raw.md is the user's raw notes and is read-only. Put structure in docs/requirements.md or docs/plan.md.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
