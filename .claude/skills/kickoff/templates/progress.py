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
CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
SIGNATURE = re.compile(r"^`([A-Za-z_][\w.]*)\((.*?)\)(?:\s*->\s*([^`]+))?`")  # a `#### `signature`` heading in "Functions"


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
    """The body of the plan section whose heading names it, e.g. section('Files') for `## 3. Files` ('' if missing)."""
    pattern = rf"^## (?:\d+[a-z]?\.\s*)?{re.escape(title)}\b[^\n]*\n(.*?)(?=^## |\Z)"
    found = re.search(pattern, plan_text(), re.M | re.S)
    return found[1] if found else ""


def interfaces() -> dict[str, list[dict]]:
    """Plan "Functions": file -> its functions, each {'name', 'params', 'summary', 'in', 'out'} (summary = docstring line 1)."""
    files: dict[str, list[dict]] = {}
    for block in re.split(r"^### ", section("Functions"), flags=re.M)[1:]:
        path = re.match(r"`([^`]+)`", block)
        if not path:
            continue
        files[path[1]] = [entry for entry in map(function_entry, re.split(r"^#### ", block, flags=re.M)[1:]) if entry]
    return files


def function_entry(block: str) -> dict | None:
    """One `#### `signature`` block: name, parameter types, return type, summary line, In and Out (None if malformed)."""
    found = SIGNATURE.match(block)
    if not found:
        return None
    lines = [line.strip() for line in block.splitlines()[1:] if line.strip()]
    summary = re.split(r"\s*\*Why:\*", lines[0])[0] if lines else ""
    types = params_typed(found[2])
    return {
        "name": found[1],
        "params": list(types),
        "types": types,
        "returns": (found[3] or "").strip(),
        "summary": summary,
        **in_and_out(block),
    }


def in_and_out(block: str) -> dict:
    """The blocks under **In** and **Out**: parsed values, the comment on each In key, and the type on the Out label."""
    found: dict = {"in": "", "out": "", "in_notes": {}, "out_type": ""}
    for label in ("In", "Out"):
        code = re.search(rf"\*\*{label}\*\*([^\n]*)\n```(jsonc|json|text)\n(.*?)\n```", block, re.S)
        if not code:
            continue
        if label == "Out":
            typed = re.search(r"`([^`]+)`", code[1])
            found["out_type"] = typed[1] if typed else ""
        if code[2] == "text":
            found[label.lower()] = code[3]
            continue
        clean, notes = without_comments(code[3])
        found[label.lower()] = json.loads(clean)
        if label == "In":
            found["in_notes"] = notes
    return found


def without_comments(block: str) -> tuple[str, dict[str, str]]:
    """A ```jsonc block without its `  // …` line comments, and each top-level key's comment (key -> comment)."""
    lines, notes = [], {}
    for line in block.splitlines():
        code, _, comment = line.partition("  //")
        lines.append(code.rstrip())
        key = re.match(r'^  "([^"]+)":', code)
        if key and comment:
            notes[key[1]] = comment.strip()
    return "\n".join(lines), notes


def matches(actual: object, shown: object) -> bool:
    """True when the real object agrees with what the plan shows; a "…" value or key stands for parts left out."""
    if shown == "…":
        return True
    if isinstance(shown, dict):
        return isinstance(actual, dict) and all(
            key == "…" or (key in actual and matches(actual[key], value)) for key, value in shown.items()
        )
    if isinstance(shown, list):
        listed = [item for item in shown if item != "…"]
        return isinstance(actual, list) and all(matches(a, b) for a, b in zip(actual, listed)) and len(actual) >= len(listed)
    return actual == shown


def file_table() -> dict[str, int]:
    """Plan "Files": the table of every file the build writes: path (a folder ends in '/') -> the phase that writes it."""
    return {path: int(phase) for path, phase in re.findall(r"^\|\s*`([^`]+)`\s*\|\s*(\d)\s*\|", section("Files"), re.M)}


def params_typed(signature: str) -> dict[str, str]:
    """Parameter name -> its type from a signature's inside, e.g. 'text: str, n: int = 2' -> {'text': 'str', 'n': 'int'}."""
    found = {}
    for part in re.split(r",(?![^\[]*\])", signature):
        name, _, rest = part.partition(":")
        name = name.split("=")[0].strip().lstrip("*")
        if name and name not in ("self", "/"):
            found[name] = rest.split("=")[0].strip()
    return found


def params_of(signature: str) -> list[str]:
    """Parameter names from a signature's inside, e.g. 'text: str, n: int = 2' -> ['text', 'n'] (self dropped)."""
    return list(params_typed(signature))


def flow() -> list[dict]:
    """Plan "Flow": each `### <n> · <title>` step as {'n', 'call', 'in', 'out'}, its In and Out blocks parsed."""
    steps = []
    for n, step in re.findall(r"^### (\d+) · (.*?)(?=^### \d+ · |\Z)", section("Flow"), re.M | re.S):
        call = re.search(r"`([A-Za-z_][\w.]*\([^`]*\))`", step)
        if call:
            steps.append({"n": int(n), "call": call[1], **in_and_out(step)})
    return steps


def flow_arrows() -> list[int]:
    """The step numbers (①, ②, …) on the arrows of the Flow diagram, in the order they're drawn."""
    diagrams = re.findall(r"```mermaid\n(.*?)```", section("Flow"), re.S)
    return [CIRCLED.index(mark) + 1 for mark in re.findall(r'-- "([①-⑳])', diagrams[0] if diagrams else "")]


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
