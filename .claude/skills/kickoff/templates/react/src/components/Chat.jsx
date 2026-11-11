// Tab 1 for the chat shape. Other shapes (batch upload, Q&A, form) replace this file with the same pattern:
// send the input to an /api endpoint, show exactly what comes back.
import { useEffect, useState } from "react";
import { api } from "../App.jsx";

export default function Chat({ onChange }) {
  const [session, setSession] = useState(null);
  const [history, setHistory] = useState([]);
  const [text, setText] = useState("");

  const start = () => {
    setHistory([]);
    return api("new", {}).then((r) => setSession(r.session));
  };
  useEffect(() => {
    start();
  }, []);

  const send = async (e) => {
    e.preventDefault();
    const msg = text.trim();
    if (!msg || !session) return;
    setText("");
    setHistory((h) => [...h, ["user", msg]]);
    const r = await api("chat", { session, text: msg });
    setHistory((h) => [...h, ["assistant", r.reply]]);
    onChange();
  };

  return (
    <section className="chat">
      <button className="secondary" onClick={start}>
        New chat
      </button>
      <ul className="messages">
        {history.map(([role, t], i) => (
          <li key={i} className={role}>
            {t}
          </li>
        ))}
      </ul>
      <form onSubmit={send}>
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Type your message…" />
        <button type="submit">Send</button>
      </form>
    </section>
  );
}
