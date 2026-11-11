// The build guide: where you are, what to type, what passes. Shown on purpose: it proves the agent built this step by step.
import * as Collapsible from "@radix-ui/react-collapsible";
import { ChevronDown, RotateCcw } from "lucide-react";
import Board from "./Board.jsx";
import CopyButton from "./CopyButton.jsx";
import TryIt from "./TryIt.jsx";

function Stepper({ phases }) {
  const current = phases.find((p) => !p.done)?.n;
  return (
    <ol className="stepper" aria-label="Build progress">
      {phases.map((p) => {
        const state = p.done ? "done" : p.n === current ? "current" : "todo";
        return (
          <li key={p.n} className={state} title={`Phase ${p.n}: ${p.name}`}>
            <span className="bar" aria-hidden />
            <span className="lbl">
              P{p.n}
              <span className="sr-only">{p.done ? " done" : p.n === current ? " next" : " not built"}</span>
            </span>
          </li>
        );
      })}
    </ol>
  );
}

export default function Sidebar({ s, title, onReset, onTry, busy }) {
  const done = s.phases.filter((p) => p.done).length;
  return (
    <Collapsible.Root className="sidebar" defaultOpen>
      <div className="brand">
        <h1>{title}</h1>
        <Collapsible.Trigger className="guide-toggle" aria-label="Show or hide the build guide">
          <span>
            Guide · {done}/{s.phases.length}
          </span>
          <ChevronDown size={16} aria-hidden />
        </Collapsible.Trigger>
      </div>
      <Collapsible.Content className="guide">
        <section className="now" aria-label="Next step">
          <Stepper phases={s.phases} />
          <div className="next">
            <code>{s.next}</code>
            <CopyButton text={s.next} label="next command" />
          </div>
          <p className="muted small">{s.next_detail}</p>
        </section>

        <section aria-label="Try it">
          <h2>Try it · phase {s.try_it_phase}</h2>
          <TryIt key={s.try_it_phase} lines={s.try_it} phase={s.try_it_phase} onTry={onTry} busy={busy} />
        </section>

        <section aria-label="Scenario board">
          <h2>Scenarios</h2>
          <Board board={s.board} />
        </section>

        <button type="button" className="ghost reset" onClick={onReset}>
          <RotateCcw size={14} aria-hidden /> Reset demo data
        </button>
      </Collapsible.Content>
    </Collapsible.Root>
  );
}
