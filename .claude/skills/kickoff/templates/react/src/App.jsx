// The whole screen = a pure render of GET /api/screen. No rules here: every decision lives in the Python core.
import { useCallback, useEffect, useState } from "react";
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
  const [chatKey, setChatKey] = useState(0); // bump = a brand-new chat
  const refresh = useCallback(() => api("screen").then(setScreen), []);

  useEffect(() => {
    if (!initialScreen) refresh();
  }, [initialScreen, refresh]);

  if (!screen) return <p className="loading">Loading…</p>;

  const reset = () =>
    api("reset", {}).then(() => {
      setChatKey((k) => k + 1);
      refresh();
    });

  return (
    <div className="layout">
      <Sidebar s={screen.sidebar} title={screen.title} onReset={reset} />
      <main>
        <nav className="tabs" role="tablist">
          {screen.tabs.map((t, i) => (
            <button key={t} role="tab" aria-selected={tab === i} onClick={() => setTab(i)}>
              {t}
            </button>
          ))}
        </nav>
        {tab === 0 ? (
          <Chat key={chatKey} onChange={refresh} />
        ) : (
          <section className="panels">
            {screen.panels.map((p) => (
              <Panel key={p.name} p={p} />
            ))}
          </section>
        )}
      </main>
    </div>
  );
}
