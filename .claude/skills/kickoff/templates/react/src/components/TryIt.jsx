// "Try it" as a checklist you can act on: copy an input, or Try it (sent to the chat) and see if the reply matches.
import { Check, CircleCheck, CircleX, Play } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { parseTryIt } from "../lib/tryit.js";
import CopyButton from "./CopyButton.jsx";

const KEY = (phase) => `kickoff:tryit:${phase}`;
const load = (phase) => {
  try {
    return JSON.parse(localStorage.getItem(KEY(phase)) || "{}");
  } catch {
    return {};
  }
};
const save = (phase, v) => {
  try {
    localStorage.setItem(KEY(phase), JSON.stringify(v));
  } catch {
    /* private mode: ticks just aren't remembered */
  }
};

export default function TryIt({ lines, phase, onTry, busy }) {
  const [state, setState] = useState(() => load(phase)); // "i" -> true (ticked) · "i.j" -> "match" | "differs"
  const set = (k, v) =>
    setState((s) => {
      const next = { ...s, [k]: v };
      save(phase, next);
      return next;
    });

  const run = async (i, j, step) => {
    const reply = await onTry(step.input);
    if (reply === null || reply === undefined) return;
    const ok = step.expect === null || reply === step.expect;
    set(`${i}.${j}`, ok ? "match" : "differs");
    toast(ok ? "Reply matches" : "Reply differs from the plan", { description: ok ? undefined : reply });
  };

  return (
    <ol className="tryit">
      {lines.map((line, i) => {
        const { steps, summary, full } = parseTryIt(line);
        if (!steps.length) {
          const ticked = !!state[i];
          return (
            <li key={line} className="manual">
              <label title={full}>
                <input type="checkbox" checked={ticked} onChange={() => set(i, !ticked)} />
                <span>{summary}</span>
              </label>
            </li>
          );
        }
        return (
          <li key={line} title={full}>
            {steps.map((step, j) => {
              const result = state[`${i}.${j}`];
              return (
                <div key={j} className="step">
                  <div className="step-row">
                    <code className="chip">{step.input}</code>
                    <CopyButton text={step.input} label={`"${step.input}"`} />
                    <button
                      type="button"
                      className="icon-btn"
                      onClick={() => run(i, j, step)}
                      disabled={busy}
                      aria-label={`Try "${step.input}" in the chat`}
                      title="Send it to the chat"
                    >
                      <Play size={14} aria-hidden />
                    </button>
                    {result === "match" && <CircleCheck className="ok" size={16} aria-label="Reply matches" />}
                    {result === "differs" && <CircleX className="bad" size={16} aria-label="Reply differs" />}
                  </div>
                  {step.expect && (
                    <p className="expect">
                      <Check size={12} aria-hidden /> {step.expect}
                    </p>
                  )}
                </div>
              );
            })}
          </li>
        );
      })}
    </ol>
  );
}
