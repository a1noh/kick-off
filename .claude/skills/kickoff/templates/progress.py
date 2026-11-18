"""Read docs/plan.md: the one parser of the plan, shared by the UI sidebar, spec.py, guide.py and the project's tests.

Runs from the kit (the venv's classroom.pth puts this folder on the path) and reads the plan of the project in the
current folder. Nothing here decides anything for the product: it only reports what the plan says.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

PHASE = re.compile(r"^- \[( |x)\] Phase (\d+): (.*)$", re.M)
REQUIREMENT = re.compile(r"^\s+- \*\*P(\d+)\.R(\d+)\*\*[^\n]*\n((?:\s{6,}- [^\n]*\n?)*)", re.M)
SIGNATURE = re.compile(r"^- `([A-Za-z_][\w.]*)\((.*?)\)[^`]*`\s*·\s*([^·]+?)\s*(?:·.*)?$", re.M)


def plan_text() -> str:
    """The text of docs/plan.md in the current project ('' when there is no plan yet)."""
    path = Path.cwd() / "docs" / "plan.md"
    return path.read_text() if path.exists() else ""


def status() -> str:
    """The plan's approval state: 'draft', 'approved <date>', or '' when the Status line is missing."""
    found = re.search(r"^\*\*Status:\*\*\s*(draft|approved \d{4}-\d{2}-\d{2})\s*$", plan_text(), re.M)
    return found[1] if found else ""


def phases() -> dict[int, tuple[bool, str]]:
    """Phase number -> (ticked?, name), from the plan's `- [ ] Phase N: name` lines."""
    return {int(n): (mark == "x", name) for mark, n, name in PHASE.findall(plan_text())}


def ticked(n: int) -> bool:
    """True when phase n is ticked in the plan."""
    return phases().get(n, (False, ""))[0]


def last_ticked() -> int:
    """The highest ticked phase, 0 if none."""
    return max((n for n, (done, _) in phases().items() if done), default=0)


def phase_block(n: int) -> str:
    """The plan text under phase n, up to the next phase or section."""
    text = plan_text()
    start = re.search(rf"^- \[[ x]\] Phase {n}:", text, re.M)
    if not start:
        return ""
    rest = text[start.end() :]
    end = re.search(r"^- \[[ x]\] Phase \d+:|^## ", rest, re.M)
    return rest[: end.start()] if end else rest


def try_it(n: int) -> list[str]:
    """The numbered Try it lines under phase n, without their numbers."""
    after = phase_block(n).split("**Try it:**", 1)
    if len(after) < 2:
        return []
    return re.findall(r"^\s+\d+\. (.+)$", after[1].split("**Requirements:**", 1)[0], re.M)


def requirements(n: int) -> list[dict]:
    """Phase n's requirements: id ('P2.R1'), traces, acceptance and test ('tests/x.py', 'test_name') or None."""
    found = []
    for phase, k, body in REQUIREMENT.findall(phase_block(n)):

        def field(name: str, body: str = body) -> str:
            """One `- Name: value` field of this requirement ('' if missing)."""
            line = re.search(rf"^\s+- {name}:(.*)$", body, re.M)
            return line[1].strip() if line else ""

        test = re.search(r"([\w/.\-]+\.py)::(\w+)", field("Test"))
        found.append(
            {
                "id": f"P{phase}.R{k}",
                "traces": field("Traces to"),
                "acceptance": field("Acceptance"),
                "test": test.groups() if test else None,
            }
        )
    return found


def section(title: str) -> str:
    """The body of the plan's `## <title>` section, e.g. section('5c') ('' if missing)."""
    found = re.search(rf"^## {re.escape(title)}\b[^\n]*\n(.*?)(?=^## |\Z)", plan_text(), re.M | re.S)
    return found[1] if found else ""


def interfaces() -> dict[str, list[dict]]:
    """Plan §5c: file -> its public functions, each {'name', 'params', 'summary'} (summary = docstring line 1)."""
    files: dict[str, list[dict]] = {}
    for block in re.split(r"^### ", section("5c"), flags=re.M)[1:]:
        path = re.match(r"`([^`]+)`", block)
        if not path:
            continue
        files[path[1]] = [
            {"name": name, "params": params_of(params), "summary": summary}
            for name, params, summary in SIGNATURE.findall(block)
        ]
    return files


def params_of(signature: str) -> list[str]:
    """Parameter names from a signature's inside, e.g. 'text: str, n: int = 2' -> ['text', 'n'] (self dropped)."""
    names = [re.split(r"[:=]", part)[0].strip().lstrip("*") for part in re.split(r",(?![^\[]*\])", signature)]
    return [name for name in names if name and name not in ("self", "/")]


def flow() -> list[tuple[str, object]]:
    """Plan §5e: the S1 flow as (call, expected object), JSON in backticks parsed, "quoted" text kept as a string."""
    steps = []
    for call, returns in re.findall(r"^\|\s*\d+\s*\|\s*`(.+?)`\s*\|\s*(.+?)\s*\|\s*$", section("5e"), re.M):
        code = re.fullmatch(r"`(.*)`", returns)
        steps.append((call, json.loads(code[1]) if code else returns.strip('"')))
    return steps


def scenario_phases() -> dict[str, int]:
    """Scenario id -> the phase that makes it work, from each phase's On screen line ("Board S2, S3 ⬜→✅")."""
    found: dict[str, int] = {}
    for n in phases():
        line = re.search(r"On screen[^\n]*", phase_block(n))
        for group in re.findall(r"Board ([^·]*?)⬜→✅", line[0] if line else ""):
            for sid in re.findall(r"\b(S\d+|[Bb]onus)\b", group):
                found.setdefault(sid[0].upper() + sid[1:], n)
    return found


def built() -> str:
    """'Phase N: name' of the last ticked phase ('' if none)."""
    n = last_ticked()
    return f"Phase {n}: {phases()[n][1]}" if n else ""


def next_command() -> str:
    """`/build` while a phase is unticked, then `All built`."""
    every = phases()
    return "All built" if every and all(done for done, _ in every.values()) else "/build"
