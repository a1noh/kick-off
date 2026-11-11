// Smoke test: the UI shows every string the API sends (it renders, it never decides). Run: npm test
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import App from "./App.jsx";

// No API server in a unit test: the chat tab still opens a session on load, so answer it here.
vi.stubGlobal("fetch", vi.fn(async () => ({ json: async () => ({ session: "test-session", reply: "" }) })));

const SAMPLE = {
  title: "Probe app",
  tabs: ["💬 Chat", "📊 Owner dashboard"],
  sidebar: {
    progress: "✅ P1 · ⬜ P2",
    try_it_phase: 1,
    try_it: ["`hi` → \"🚧 Greeting arrives in phase 2.\""],
    board: [{ label: "⬜ S1 · Happy path", checks: ["⬜ reply matches"], not_built: true }],
    next: "/build",
  },
  panels: [{ name: "KPIs", phase: 2, live: false, text: "⬜ KPIs: arrives in phase 2" }],
};

test("renders sidebar, board and placeholders from the screen JSON", () => {
  render(<App initialScreen={SAMPLE} />);
  for (const s of ["Probe app", "✅ P1 · ⬜ P2", SAMPLE.sidebar.try_it[0], "⬜ S1 · Happy path", "/build"]) {
    expect(screen.getByText(s, { exact: false })).toBeTruthy();
  }
  fireEvent.click(screen.getByRole("tab", { name: "📊 Owner dashboard" }));
  expect(screen.getByText("⬜ KPIs: arrives in phase 2")).toBeTruthy();
});
