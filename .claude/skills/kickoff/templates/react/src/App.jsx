// The whole screen = a pure render of GET /api/screen. No rules here: every decision lives in the Python core.
// The chat lives here (not in Chat.jsx) so the guide's "Try" buttons can send an input and read the real reply.
import { useCallback, useEffect, useState } from "react";
import { Toaster } from "sonner";
import Chat from "./components/Chat.jsx";
import Panel from "./components/Panel.jsx";
import Sidebar from "./components/Sidebar.jsx";

export async function api(path, body) {
  const opts =
    body === undefined
      ? {}
      : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
  const r = await fetch(`/api/${path}`, opts);
  return r.json();
}

export default function App({ initialScreen = null }) {
  const [screen, setScreen] = useState(initialScreen);
  const [tab, setTab] = useState(0);
  const [chat, setChat] = useState({ session: null, history: [], sending: false, error: "" });
  const refresh = useCallback(() => api("screen").then(setScreen), []);

  const newChat = useCallback(() => {
    setChat({ session: null, history: [], sending: false, error: "" });
    return api("new", {})
      .then((r) => setChat((c) => ({ ...c, session: r.session })))
      .catch(() => setChat((c) => ({ ...c, error: "Couldn't reach the app server. Start it, then reload this page." })));
  }, []);

  useEffect(() => {
    if (!initialScreen) refresh();
    newChat();
  }, [initialScreen, refresh, newChat]);

  // Send one message in the current chat; resolves to the agent's exact reply (or null on failure).
  const send = useCallback(
    async (text) => {
      const msg = text.trim();
      if (!msg || !chat.session || chat.sending) return null;
      setChat((c) => ({ ...c, sending: true, error: "", history: [...c.history, ["user", msg]] }));
      try {
        const r = await api("chat", { session: chat.session, text: msg });
        setChat((c) => ({ ...c, sending: false, history: [...c.history, ["assistant", r.reply]] }));
        if (!initialScreen) refresh();
        return r.reply;
      } catch {
        setChat((c) => ({ ...c, sending: false, error: "That message didn't go through. Check the server, then send it again." }));
        return null;
      }
    },
    [chat.session, chat.sending, refresh, initialScreen],
  );

  if (!screen) return <p className="loading">Loading…</p>;

  const reset = () =>
    api("reset", {}).then(() => {
      newChat();
      if (!initialScreen) refresh();
    });
  const tryInput = (text) => {
    setTab(0);
    return send(text);
  };

  return (
    <div className="layout">
      <Sidebar s={screen.sidebar} title={screen.title} onReset={reset} onTry={tryInput} busy={chat.sending} />
      <main>
        <nav className="tabs" role="tablist" aria-label="Views">
          {screen.tabs.map((t, i) => (
            <button key={t} role="tab" aria-selected={tab === i} onClick={() => setTab(i)}>
              {t}
            </button>
          ))}
        </nav>
        {tab === 0 ? (
          <Chat chat={chat} onSend={send} onNew={newChat} suggestions={screen.sidebar.try_it} />
        ) : (
          <section aria-label={screen.tabs[1]}>
            <div className="panels">
              {screen.panels.map((p) => (
                <Panel key={p.name} p={p} />
              ))}
            </div>
          </section>
        )}
      </main>
      <Toaster position="bottom-center" duration={1600} />
    </div>
  );
}
