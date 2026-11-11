"""Spec tooling for a /kickoff classroom. One folder per phase: docs/specs/phase-N/{spec.md, verify.md}.

  .venv/bin/python scripts/spec.py check       every spec is grounded + tested (the Stop hook runs this)
  .venv/bin/python scripts/spec.py verify N    run phase N's tests + render the app -> phase-N/verify.md + README.md

`check` fails when: a ticked phase has no spec.md, or no verify.md newer than its spec with every R passing;
an R block's `Traces to:` cites no source (plan.md / raw.md:L<n> / data/<file>), its `Acceptance:` has no exact
value in "quotes", or its `Test:` names a test that doesn't exist; or an Assumption isn't confirmed.
verify.md is always written by this script, never by hand: it is the evidence.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / "docs" / "specs"
PLAN = ROOT / "docs" / "plan.md"
SOURCE = re.compile(r"plan\.md|raw\.md:L\d+|data/[\w.\-]+")
QUOTED = re.compile(r'"[^"]+"')
VENV_PY = ROOT / ".venv" / "bin" / "python"
PY = str(VENV_PY) if VENV_PY.exists() else sys.executable
ENV = {k: v for k, v in os.environ.items() if k != "__PYVENV_LAUNCHER__"}  # macOS python3 leaks this into children


def phases() -> dict[int, tuple[bool, str]]:
    """Phase number -> (ticked?, name), read from docs/plan.md."""
    text = PLAN.read_text() if PLAN.exists() else ""
    return {int(n): (x == "x", name) for x, n, name in re.findall(r"^- \[( |x)\] Phase (\d+): (.*)$", text, re.M)}


def section(text: str, title: str) -> str:
    """Body of the `## <title>` section ('' if missing)."""
    m = re.search(rf"^## {re.escape(title)}\b[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m[1] if m else ""


def requirements(text: str) -> list[dict]:
    """Every `### R<n> · title` block with its Traces to / Acceptance / Test fields."""
    reqs = []
    for m in re.finditer(r"^### (R\d+)\b[^\n]*\n(.*?)(?=^### |^## |\Z)", text, re.M | re.S):
        body = m[2]

        def field(name: str, body: str = body) -> str:
            f = re.search(rf"^- {name}:(.*)$", body, re.M)
            return f[1].strip() if f else ""

        t = re.search(r"([\w/.\-]+\.py)::(\w+)", field("Test"))
        reqs.append(
            {
                "id": m[1],
                "traces": field("Traces to"),
                "acceptance": field("Acceptance"),
                "test": t.groups() if t else None,
            }
        )
    return reqs


def check_spec(n: int, path: Path) -> list[str]:
    """Problems in one spec.md (grounding, acceptance, tests, assumptions)."""
    text, problems = path.read_text(), []
    reqs = requirements(text)
    if not reqs:
        problems.append("no requirements (### R1 · …)")
    for r in reqs:
        if not SOURCE.search(r["traces"]):
            problems.append(f"{r['id']}: 'Traces to:' must cite plan.md, raw.md:L<n> or data/<file>")
        if not QUOTED.search(r["acceptance"]):
            problems.append(f"{r['id']}: 'Acceptance:' needs the exact expected value in \"quotes\"")
        if not r["test"]:
            problems.append(f"{r['id']}: 'Test:' must name tests/<file>.py::<test_name>")
        else:
            f = ROOT / r["test"][0]
            if not f.exists() or not re.search(rf"^def {r['test'][1]}\(", f.read_text(), re.M):
                problems.append(f"{r['id']}: test {r['test'][0]}::{r['test'][1]} does not exist")
    for line in section(text, "Assumptions").splitlines():
        s = line.strip()
        if s.startswith("- ") and not re.search(r"confirmed|^- none", s, re.I):
            problems.append(f"open assumption (ask the user, then write 'confirmed by user'): {s[2:70]}")
    return [f"phase-{n}/spec.md: {p}" for p in problems]


def check_verify(n: int, reqs: list[dict]) -> list[str]:
    """A ticked phase needs a fresh verify.md with every requirement passing."""
    spec, verify = SPECS / f"phase-{n}" / "spec.md", SPECS / f"phase-{n}" / "verify.md"
    if not verify.exists():
        return [f"phase-{n} is ticked but has no verify.md: run scripts/spec.py verify {n}"]
    if verify.stat().st_mtime < spec.stat().st_mtime:
        return [f"phase-{n}/verify.md is older than spec.md: re-run scripts/spec.py verify {n}"]
    text = verify.read_text()
    return [
        f"phase-{n}/verify.md: {r['id']} is not passing (fix it, then re-run verify {n})"
        for r in reqs
        if not re.search(rf"^\| {r['id']} \|.*\| ✅ pass \|$", text, re.M)
    ]


def cmd_check() -> int:
    problems = []
    for n, (done, _) in sorted(phases().items()):
        spec = SPECS / f"phase-{n}" / "spec.md"
        if not spec.exists():
            if done:
                problems.append(f"phase {n} is ticked in plan.md but docs/specs/phase-{n}/spec.md is missing")
            continue
        problems += check_spec(n, spec)
        if done:
            problems += check_verify(n, requirements(spec.read_text()))
    for p in problems:
        print("FAIL", p)
    print("SPEC OK" if not problems else f"{len(problems)} spec problem(s)")
    return 1 if problems else 0


def run_tests(reqs: list[dict]) -> dict[str, bool]:
    """Run the spec's tests with pytest; test name -> passed."""
    ids = sorted({f"{r['test'][0]}::{r['test'][1]}" for r in reqs if r["test"]})
    with tempfile.TemporaryDirectory() as tmp:
        xml = Path(tmp) / "r.xml"
        r = subprocess.run(
            [PY, "-m", "pytest", "-q", f"--junitxml={xml}", *ids], cwd=ROOT, capture_output=True, text=True, env=ENV
        )
        if not xml.exists():
            print(f"FAIL pytest did not run:\n{(r.stdout + r.stderr)[-800:]}")
            return {}
        return {
            c.get("name"): not any(x.tag in ("failure", "error", "skipped") for x in c)
            for c in ET.parse(xml).iter("testcase")
        }


def render_screen() -> str:
    """The app as the user sees it right now (api.screen_text or AppTest), in a clean subprocess with the classroom's venv."""
    r = subprocess.run([PY, __file__, "_render"], cwd=ROOT, capture_output=True, text=True, env=ENV)
    out = r.stdout.split("<<<SCREEN>>>\n", 1)
    return (
        out[1].rstrip() if len(out) == 2 else f"APP EXCEPTION: could not render the app\n{(r.stdout + r.stderr)[-800:]}"
    )


def _render() -> str:
    """Runs inside the venv: tabs, sidebar text, board rows, panels.
    React mode (ui/api.py exists): api.screen_text(), the same JSON the UI renders. Streamlit: AppTest of ui/app.py.
    Older classrooms keep api.py / app.py in the root; both layouts work."""
    os.chdir(ROOT)
    sys.path[:0] = [str(ROOT / "src"), str(ROOT / "ui"), str(ROOT)]
    pick = lambda name: next((p for p in (ROOT / "ui" / name, ROOT / name) if p.exists()), None)  # noqa: E731
    api_py, app_py = pick("api.py"), pick("app.py")
    if api_py:
        try:
            import api

            return api.screen_text()
        except Exception as e:  # noqa: BLE001  (any crash is shown as the proof's failure)
            return f"APP EXCEPTION: {type(e).__name__}: {e}"
    if not app_py:
        return "APP EXCEPTION: no ui/app.py (or ui/api.py)"
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(app_py), default_timeout=60).run()
    if at.exception:
        return f"APP EXCEPTION: {at.exception[0].value}"
    lines = ["[tabs] " + " | ".join(t.label for t in at.tabs), "[sidebar]"]
    lines += [m.value for m in at.sidebar.markdown] + [f"[row] {e.label}" for e in at.sidebar.expander]
    lines += (
        ["[main]"] + [f"[info] {i.value}" for i in at.main.info] + [f"[warning] {w.value}" for w in at.main.warning]
    )
    return "\n".join(lines)


def write_index() -> None:
    rows = ["| Phase | Name | Spec | Requirements | Verified |", "|---|---|---|---|---|"]
    for n, (done, name) in sorted(phases().items()):
        spec, verify = SPECS / f"phase-{n}" / "spec.md", SPECS / f"phase-{n}" / "verify.md"
        reqs = len(requirements(spec.read_text())) if spec.exists() else 0
        ok = verify.exists() and "❌" not in verify.read_text()
        link = f"[spec](phase-{n}/spec.md)" if spec.exists() else "—"
        state = ("✅" if ok else "❌") if verify.exists() else ("⬜ not yet" if not done else "❌ missing")
        rows.append(f"| {n} | {name} | {link} | {reqs} | {state} |")
    head = "# Specs\n\nOne folder per phase: `spec.md` (what will be built, grounded) + `verify.md` (evidence, written by `scripts/spec.py verify N`).\n\n"
    (SPECS / "README.md").write_text(head + "\n".join(rows) + "\n")


def cmd_verify(n: int) -> int:
    spec = SPECS / f"phase-{n}" / "spec.md"
    if not spec.exists():
        print(f"FAIL no {spec.relative_to(ROOT)}")
        return 1
    reqs = requirements(spec.read_text())
    results = run_tests(reqs)
    rows = ["| R | Test | Result |", "|---|---|---|"]
    for r in reqs:
        name = r["test"][1] if r["test"] else "—"
        ok = results.get(name, False)
        rows.append(
            f"| {r['id']} | `{r['test'][0] if r['test'] else '—'}::{name}` | {'✅ pass' if ok else '❌ fail'} |"
        )
    screen = render_screen()
    stamp = f"{datetime.now():%Y-%m-%d %H:%M}"
    body = (
        f"# Phase {n} · verification\n\nAuto-written by `scripts/spec.py verify {n}` at {stamp}. Do not edit by hand.\n\n"
        "## Requirements\n" + "\n".join(rows) + "\n\n## Screen (rendered, as the user sees it now)\n```text\n"
        f"{screen}\n```\n"
    )
    (SPECS / f"phase-{n}" / "verify.md").write_text(body)
    write_index()
    print(body)
    failed = [r["id"] for r in reqs if not results.get(r["test"][1] if r["test"] else "", False)]
    print("VERIFY OK" if not failed and "APP EXCEPTION" not in screen else f"VERIFY FAIL: {failed or 'app exception'}")
    return 1 if failed or "APP EXCEPTION" in screen else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["check"]:
        sys.exit(cmd_check())
    if args[:1] == ["_render"]:
        print("<<<SCREEN>>>\n" + _render())
        sys.exit(0)
    if args[:1] == ["verify"] and len(args) == 2 and args[1].isdigit():
        sys.exit(cmd_verify(int(args[1])))
    sys.exit(__doc__)
