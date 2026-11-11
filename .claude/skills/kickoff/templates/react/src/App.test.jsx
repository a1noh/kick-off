// UI test: the screen renders exactly what the API sends, and the guide's controls work (no server needed).
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import App from "./App.jsx";
import { parseTryIt } from "./lib/tryit.js";

const STUB = "🚧 Greeting arrives in phase 2.";
const SAMPLE = {
  title: "Probe app",
  tabs: ["💬 Chat", "📊 Owner dashboard"],
  sidebar: {
    progress: "✅ P1 · ⬜ P2",
    phases: [
      { n: 1, name: "the app shell", done: true },
      { n: 2, name: "scenario 1 works", done: false },
    ],
    built_detail: "Phase 1: the app shell",
    next_detail: "Phase 2: scenario 1 works",
    try_it_phase: 1,
    try_it: [`\`hi\` → "${STUB}"`, 'Open the 📊 Owner dashboard tab → every panel shows "⬜ KPIs: arrives in phase 2"'],
    board: [
      { id: "S1", title: "Happy path", state: "not_built", label: "⬜ S1 · Happy path", checks: ["⬜ reply matches"], done: 0, total: 1, not_built: true, note: "not built yet (🚧 stub reply)", works_in: 2 },
      { id: "S2", title: "Handoff", state: "not_built", label: "⬜ S2 · Handoff", checks: ["⬜ queue row written"], done: 0, total: 1, not_built: true, note: "not built yet (🚧 stub reply)", works_in: 3 },
    ],
    next: "/build",
  },
  panels: [{ name: "KPIs", phase: 2, live: false, wide: true, shows: "counts", text: "⬜ KPIs: arrives in phase 2" }],
};

afterEach(cleanup);

beforeEach(() => {
  // No API server in a unit test: answer the chat endpoints here (the stub reply equals the plan's expected text).
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url) => ({ json: async () => (String(url).endsWith("/chat") ? { reply: STUB } : { session: "s1" }) })),
  );
  vi.stubGlobal("matchMedia", (q) => ({ matches: false, media: q, addEventListener() {}, removeEventListener() {} }));
  Object.assign(navigator, { clipboard: { writeText: vi.fn(async () => {}) } });
  // Like current Chrome: scrollIntoView returns a value. An effect that returned it crashed React (blank page).
  Element.prototype.scrollIntoView = () => Promise.resolve();
});

test("parses try-it lines into input → expected steps", () => {
  expect(parseTryIt('`a` → "A." → `b` → "B." · panel').steps).toEqual([
    { input: "a", expect: "A." },
    { input: "b", expect: "B." },
  ]);
  expect(parseTryIt('Open the tab → shows "x"').steps).toEqual([]);
});

test("shows the guide: stepper, next command, try-it chips, scenarios", () => {
  render(<App initialScreen={SAMPLE} />);
  expect(screen.getByRole("heading", { name: "Probe app" })).toBeTruthy();
  expect(screen.getByLabelText("Build progress")).toBeTruthy();
  expect(screen.getByText("Phase 2: scenario 1 works")).toBeTruthy();
  expect(screen.getAllByText("hi").length).toBeGreaterThan(0);
  expect(screen.getByText(STUB)).toBeTruthy();
  // the plan's exact words: Try-it lines quote these, so the screen must show them verbatim
  for (const s of ["⬜ S1 · Happy path", "✅ Phase 1: the app shell", "works in P2", "works in P3", "Scenarios · 0/2 working"]) {
    expect(screen.getByText(s, { exact: false })).toBeTruthy();
  }
  expect(screen.getByLabelText("Build progress").textContent).toContain("✅ P1");
  expect(screen.getByRole("button", { name: "Copy next command" })).toBeTruthy();
});

test("copy buttons copy the exact text", async () => {
  render(<App initialScreen={SAMPLE} />);
  await act(async () => fireEvent.click(screen.getByRole("button", { name: 'Copy "hi"' })));
  expect(navigator.clipboard.writeText).toHaveBeenCalledWith("hi");
  await act(async () => fireEvent.click(screen.getByRole("button", { name: "Copy next command" })));
  expect(navigator.clipboard.writeText).toHaveBeenCalledWith("/build");
});

test("Try sends the input to the chat and marks the reply as matching", async () => {
  render(<App initialScreen={SAMPLE} />);
  const tryBtn = screen.getByRole("button", { name: 'Try "hi" in the chat' });
  await waitFor(() => expect(tryBtn.disabled).toBe(false));
  await act(async () => fireEvent.click(tryBtn));
  await waitFor(() => expect(screen.getByLabelText("Reply matches")).toBeTruthy());
  expect(screen.getAllByText(STUB).length).toBeGreaterThan(1); // the expected line + the real reply in the chat
});

test("board: rows open independently, every click toggles, Next and Reset stay on screen", async () => {
  localStorage.clear();
  render(<App initialScreen={SAMPLE} />);
  const s1 = screen.getByRole("button", { name: /S1 · Happy path/ });
  const s2 = screen.getByRole("button", { name: /S2 · Handoff/ });
  for (const expected of ["true", "false", "true"]) {
    await act(async () => fireEvent.click(s1));
    expect(s1.getAttribute("aria-expanded")).toBe(expected);
  }
  expect(screen.getByText("⬜ reply matches")).toBeTruthy();
  expect(screen.getAllByText("not built yet (🚧 stub reply)").length).toBeGreaterThan(0);
  await act(async () => fireEvent.click(s2));
  expect(s1.getAttribute("aria-expanded")).toBe("true"); // opening S2 never closes (or moves) S1
  expect(s2.getAttribute("aria-expanded")).toBe("true");
  expect(screen.getByRole("button", { name: /Reset demo data/ })).toBeTruthy();
  expect(screen.getByRole("button", { name: "Copy next command" })).toBeTruthy();
});

test("dashboard tab shows the honest placeholder and what will show", async () => {
  render(<App initialScreen={SAMPLE} />);
  fireEvent.click(screen.getByRole("tab", { name: "📊 Owner dashboard" }));
  expect(screen.getByText("⬜ KPIs: arrives in phase 2")).toBeTruthy();
  expect(screen.getByText("Will show: counts")).toBeTruthy();
});
