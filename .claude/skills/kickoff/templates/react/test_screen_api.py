"""React mode screen contract (copy to tests/test_screen.py). Same rules as the Streamlit AppTest version, read live
from plan.md + run_all, so it stays true in every phase. Offline: no network, no browser."""

from fastapi.testclient import TestClient

import api
import progress
from evals.scenarios import run_all

client = TestClient(api.app)


class StubAgent:
    """A 🚧 stub: proves a stub can never turn the board green."""

    def __init__(self, extract=None, out_dir=None):
        pass

    def reply(self, text: str) -> str:
        return "🚧 Something arrives in phase 9."


def test_screen_matches_plan_and_board():
    s = client.get("/api/screen").json()
    sb = s["sidebar"]
    for n, (done, _) in progress.phases().items():
        assert f"{'✅' if done else '⬜'} P{n}" in sb["progress"]
    assert sb["try_it"] == progress.try_it(progress.last_ticked() or 1)
    assert [b["label"] for b in sb["board"]] == [f"{api.ICON[r.state]} {r.id} · {r.title}" for r in run_all()]
    assert sb["next"] == progress.next_command()
    for p in s["panels"]:
        assert p["live"] == progress.ticked(p["phase"]), p["name"]
        assert ("text" in p) == (not progress.ticked(p["phase"])), p["name"]


def test_stub_replies_never_show_green():
    api.config["board_agent"] = StubAgent
    try:
        board = client.get("/api/screen").json()["sidebar"]["board"]
    finally:
        api.config["board_agent"] = None
    assert board and all(b["not_built"] and b["label"].startswith("⬜") for b in board)
    assert not any(c.startswith("✅") for b in board for c in b["checks"])


def test_chat_sessions_are_separate():
    api.config["agent_factory"] = StubAgent
    try:
        a, b = (client.post("/api/new").json()["session"] for _ in range(2))
        assert a != b
        assert client.post("/api/chat", json={"session": a, "text": "hi"}).json()["reply"].startswith("🚧")
    finally:
        api.config["agent_factory"] = api.Agent
