// The Scenario board: one row per demo scenario, in the plan's exact words ("⬜ S1 · Ready bike", "⬜ reply matches").
// Rows open independently (a click never moves the row you clicked) and are keyed by scenario id, so an open row stays
// open across refreshes and when it turns ⬜ → ✅. Not-built rows say which phase makes them work (from the plan).
import * as Accordion from "@radix-ui/react-accordion";
import { ChevronDown } from "lucide-react";
import { useState } from "react";

const KEY = "kickoff:board-open";
const load = () => {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "[]");
  } catch {
    return [];
  }
};

export default function Board({ board }) {
  const [open, setOpen] = useState(load);
  const change = (ids) => {
    setOpen(ids);
    try {
      localStorage.setItem(KEY, JSON.stringify(ids));
    } catch {
      /* private mode: open rows just aren't remembered */
    }
  };
  return (
    <Accordion.Root type="multiple" value={open} onValueChange={change} className="board">
      {board.map((b) => (
        <Accordion.Item key={b.id} value={b.id} className={`row ${b.state}`}>
          <Accordion.Header asChild>
            <h3>
              <Accordion.Trigger className="row-trigger">
                <span className="name">{b.label}</span>
                {b.state !== "pass" && b.works_in && <span className="works-in">works in P{b.works_in}</span>}
                <span className="count" aria-label={`${b.done} of ${b.total} checks pass`}>
                  {b.done}/{b.total}
                </span>
                <ChevronDown size={14} aria-hidden className="chev" />
              </Accordion.Trigger>
            </h3>
          </Accordion.Header>
          <Accordion.Content className="row-content">
            <ul className="checks">
              {b.checks.map((c) => (
                <li key={c} className={c.startsWith("✅") ? "ok" : c.startsWith("❌") ? "bad" : "todo"}>
                  {c}
                </li>
              ))}
            </ul>
            {b.note && <p className="muted small">{b.note}</p>}
          </Accordion.Content>
        </Accordion.Item>
      ))}
    </Accordion.Root>
  );
}
