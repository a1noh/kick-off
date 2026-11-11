// The Scenario board: one row per demo scenario. A controlled accordion keyed by scenario id, so the open row
// stays open across refreshes and when a row turns ⬜ → ✅ (its label changes, its id doesn't).
import * as Accordion from "@radix-ui/react-accordion";
import { ChevronDown, CircleCheck, CircleDashed, CircleX } from "lucide-react";
import { useState } from "react";

const STATE_ICON = { pass: CircleCheck, fail: CircleX, not_built: CircleDashed };
const CHECK_ICON = { "✅": CircleCheck, "❌": CircleX, "⬜": CircleDashed };

function CheckLine({ text }) {
  const glyph = [...text][0];
  const Icon = CHECK_ICON[glyph] || CircleDashed;
  const rest = text.slice(glyph.length).trim();
  const cls = glyph === "✅" ? "ok" : glyph === "❌" ? "bad" : "todo";
  return (
    <li className={cls}>
      <Icon size={13} aria-hidden />
      <span>{rest}</span>
    </li>
  );
}

export default function Board({ board }) {
  const [open, setOpen] = useState("");
  return (
    <Accordion.Root type="single" collapsible value={open} onValueChange={setOpen} className="board">
      {board.map((b) => {
        const Icon = STATE_ICON[b.state] || CircleDashed;
        return (
          <Accordion.Item key={b.id} value={b.id} className={`row ${b.state}`}>
            <Accordion.Header asChild>
              <h3>
                <Accordion.Trigger className="row-trigger">
                  <Icon size={16} aria-hidden className="state" />
                  <span className="name">
                    {b.id} · {b.title}
                  </span>
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
                  <CheckLine key={c} text={c} />
                ))}
              </ul>
              {b.not_built && <p className="muted small">Not built yet: replies are still 🚧 stubs.</p>}
            </Accordion.Content>
          </Accordion.Item>
        );
      })}
    </Accordion.Root>
  );
}
