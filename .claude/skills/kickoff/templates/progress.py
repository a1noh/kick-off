"""Where are we? Phase ticks, Try it lines and the next command, read live from docs/plan.md."""

import re
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1] / "docs" / "plan.md"  # this file lives in ui/
PHASE = re.compile(r"^- \[( |x)\] Phase (\d+): (.*)$", re.M)


def _text() -> str:
    return PLAN.read_text() if PLAN.exists() else ""


def phases() -> dict[int, tuple[bool, str]]:
    """Phase number -> (ticked?, name)."""
    return {int(n): (x == "x", name) for x, n, name in PHASE.findall(_text())}


def ticked(n: int) -> bool:
    """True when phase n is ticked in the plan."""
    return phases().get(n, (False, ""))[0]


def last_ticked() -> int:
    """Highest ticked phase, 0 if none."""
    return max((n for n, (done, _) in phases().items() if done), default=0)


def try_it(n: int) -> list[str]:
    """The numbered Try it lines under phase n, without their numbers."""
    text = _text()
    start = re.search(rf"^- \[[ x]\] Phase {n}:", text, re.M)
    if not start:
        return []
    block = text[start.end() :]
    end = re.search(r"^- \[[ x]\] Phase \d+:|^## ", block, re.M)
    block = block[: end.start()] if end else block
    after = block.split("**Try it:**", 1)
    return re.findall(r"^\s+\d+\. (.+)$", after[1], re.M) if len(after) == 2 else []


def next_command() -> str:
    """`/build` while a phase is unticked, then `/rehearse`."""
    p = phases()
    return "/rehearse" if p and all(done for done, _ in p.values()) else "/build"
