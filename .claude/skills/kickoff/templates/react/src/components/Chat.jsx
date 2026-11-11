// Tab 1, the user's door (chat shape). Shows exactly what the agent replies. Other shapes (upload, Q&A, form)
// replace this file with the same pattern: send the input to an /api endpoint, show exactly what comes back.
import { ArrowUp, MessageSquarePlus } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { allInputs } from "../lib/tryit.js";

export default function Chat({ chat, onSend, onNew, suggestions = [] }) {
  const [text, setText] = useState("");
  const input = useRef(null);
  const end = useRef(null);
  const chips = allInputs(suggestions).slice(0, 4);

  // Block body on purpose: an effect must return nothing or a cleanup function. Current Chrome returns a
  // non-function from scrollIntoView, and returning it crashed React (blank page).
  useEffect(() => {
    end.current?.scrollIntoView?.({ block: "end" });
  }, [chat.history.length, chat.sending]);

  const submit = async (e) => {
    e.preventDefault();
    const msg = text;
    setText("");
    await onSend(msg);
    input.current?.focus();
  };

  return (
    <section className="chat" aria-label="Chat">
      <div className="chat-head">
        <button type="button" className="ghost" onClick={onNew}>
          <MessageSquarePlus size={15} aria-hidden /> New chat
        </button>
      </div>

      {chat.history.length === 0 && !chat.sending && chips.length > 0 && (
        <div className="empty">
          <p>Start with a demo input:</p>
          <div className="suggestions">
            {chips.map((c) => (
              <button key={c} type="button" className="suggestion" onClick={() => onSend(c)} disabled={!chat.session}>
                {c}
              </button>
            ))}
          </div>
        </div>
      )}

      <ul className="messages" aria-live="polite">
        {chat.history.map(([role, t], i) => (
          <li key={i} className={role}>
            {t}
          </li>
        ))}
        {chat.sending && (
          <li className="assistant pending" aria-label="Waiting for the reply">
            <span className="dots" aria-hidden>
              <i />
              <i />
              <i />
            </span>
          </li>
        )}
        <li ref={end} className="anchor" aria-hidden />
      </ul>

      {chat.error && (
        <p className="error" role="alert">
          {chat.error}
        </p>
      )}

      <form className="composer" onSubmit={submit}>
        <input
          ref={input}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type your message…"
          aria-label="Message"
          disabled={!chat.session}
        />
        <button type="submit" className="send" disabled={!text.trim() || !chat.session || chat.sending} aria-label="Send">
          <ArrowUp size={18} aria-hidden />
        </button>
      </form>
    </section>
  );
}
