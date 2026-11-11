"""Door API (React mode). Copy to the classroom as ui/api.py. Display only, like app.py in Streamlit mode:
it turns progress + the Scenario board + the owner panels into ONE JSON screen, and passes chat to the agent.
Every decision stays in agent.py (app kind: core.py) and tools.py.

/build fills in: TABS (tab 1 named for the shape), PANELS (plan.md §2b panel table: panel -> phase), and LIVE
(panel -> function returning {"kind": "metrics"|"table"|"lines", ...}) as phases go live.
"""

import uuid
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import progress
from agent import Agent  # app kind: the core.py entry point instead
from evals.scenarios import run_all

UI = Path(__file__).resolve().parent  # ui/ (the product code is in src/, on the path via classroom.pth)
TITLE = "Product name"  # /build: from plan.md title
TABS = ["💬 Chat", "📊 Owner dashboard"]  # /build: tab 1 = the shape's door (plan.md §2b)
PANELS: dict[str, int] = {"KPIs": 2, "Queue": 3, "Audit log": 3, "Eval score": 4}  # /build: plan.md §2b table
WIDE: set[str] = {"KPIs", "Queue"}  # /build: panels that run full width in the §2b sketch
SHOWS: dict[str, str] = {}  # /build: panel -> what it will show (§2b table "Shows" column), for the empty state
LIVE: dict = {}  # panel -> () -> {"kind": "metrics", "items": [{"label", "value"}]} | {"kind": "table", "rows": [...]}
RESET = None  # phase 2+: e.g. lambda: Store(OUT).reset() (data.py owns the reset, never api.py)
ICON = {"not_built": "⬜", "fail": "❌", "pass": "✅"}
CHECK = {None: "⬜", True: "✅", False: "❌"}
config: dict = {"agent_factory": Agent, "board_agent": None}  # tests swap these (offline extractor, stub agent)
sessions: dict[str, object] = {}  # session id -> Agent (one per browser chat, in memory)


def panel(name: str) -> dict:
    """A dashboard panel: live once its phase is ticked, else an honest ⬜ placeholder."""
    n = PANELS[name]
    base = {"name": name, "phase": n, "wide": name in WIDE, "shows": SHOWS.get(name, "")}
    if not progress.ticked(n):
        return {**base, "live": False, "text": f"⬜ {name}: arrives in phase {n}"}
    if name in LIVE:
        return {**base, "live": True, **LIVE[name]()}
    return {**base, "live": False, "warning": f"{name}: phase {n} is ticked but this panel is not built"}


def screen() -> dict:
    """Everything the UI shows, read live from plan.md, the scenario board and the records."""
    n = progress.last_ticked() or 1
    stub = config["board_agent"]
    results = run_all() if stub is None else run_all(agent_factory=stub)
    board = [
        {
            "id": r.id,
            "title": r.title,
            "state": r.state,
            "label": f"{ICON[r.state]} {r.id} · {r.title}",
            "checks": [f"{CHECK[ok]} {label}" for label, ok in r.checks],
            "done": sum(ok is True for _, ok in r.checks),
            "total": len(r.checks),
            "not_built": r.state == "not_built",
        }
        for r in results
    ]
    phases = progress.phases()
    progress_line = " · ".join(f"{'✅' if d else '⬜'} P{k}" for k, (d, _) in phases.items())
    upcoming = [k for k, (d, _) in phases.items() if not d]
    sidebar = {
        "progress": progress_line,
        "phases": [{"n": k, "name": name, "done": d} for k, (d, name) in phases.items()],
        "next_detail": f"Phase {upcoming[0]}: {phases[upcoming[0]][1]}" if upcoming else "All phases built",
        "try_it_phase": n,
        "try_it": progress.try_it(n),
        "board": board,
        "next": progress.next_command(),
    }
    return {"title": TITLE, "tabs": TABS, "sidebar": sidebar, "panels": [panel(p) for p in PANELS]}


def screen_text() -> str:
    """The screen as text, same format as the Streamlit AppTest render (scripts/spec.py verify writes it to verify.md)."""
    s = screen()
    sb = s["sidebar"]
    lines = ["[tabs] " + " | ".join(s["tabs"]), "[sidebar]", f"### {s['title']}", f"**Progress** {sb['progress']}"]
    lines += [f"**Try it** (phase {sb['try_it_phase']})"] + [f"{i}. {t}" for i, t in enumerate(sb["try_it"], 1)]
    lines.append("**Scenario board**")
    for b in sb["board"]:
        lines += b["checks"] + (["not built yet (🚧 stub reply)"] if b["not_built"] else [])
    lines.append(f"**Next:** `{sb['next']}`")
    lines += [f"[row] {b['label']}" for b in sb["board"]] + ["[main]"]
    lines += [f"[info] {p['text']}" for p in s["panels"] if "text" in p]
    lines += [f"[warning] {p['warning']}" for p in s["panels"] if "warning" in p]
    return "\n".join(lines)


class Message(BaseModel):
    session: str
    text: str


app = FastAPI(title=TITLE)


@app.get("/api/screen")
def get_screen() -> dict:
    return screen()


@app.post("/api/new")
def new_chat() -> dict:
    """A fresh chat: a new session id and a new agent (nothing carries over, e.g. who verified)."""
    sid = uuid.uuid4().hex
    sessions[sid] = config["agent_factory"]()
    return {"session": sid}


@app.post("/api/chat")
def chat(m: Message) -> dict:
    agent = sessions.get(m.session)
    if agent is None:
        agent = sessions[m.session] = config["agent_factory"]()
    return {"reply": agent.reply(m.text)}


@app.post("/api/reset")
def reset() -> dict:
    """Rebuild the demo records from data/ and drop every chat."""
    if RESET is None:
        return {"ok": False, "message": "🚧 Reset arrives in phase 2."}
    RESET()
    sessions.clear()
    return {"ok": True, "message": "Demo data reset."}


DIST = UI / "web" / "dist"
if DIST.exists():  # the built React UI, served by the same process: one URL
    app.mount("/", StaticFiles(directory=DIST, html=True), name="web")
