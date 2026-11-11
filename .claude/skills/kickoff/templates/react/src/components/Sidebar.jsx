// Where am I (Progress), what to try (Try it), what works (Scenario board), what's next.
export default function Sidebar({ s, title, onReset }) {
  return (
    <aside className="sidebar">
      <h1>{title}</h1>
      <p>
        <strong>Progress</strong> {s.progress}
      </p>
      <p>
        <strong>Try it</strong> (phase {s.try_it_phase})
      </p>
      <ol className="tryit">
        {s.try_it.map((t) => (
          <li key={t}>{t}</li>
        ))}
      </ol>
      <p>
        <strong>Scenario board</strong>
      </p>
      {s.board.map((b) => (
        <details key={b.label} className="row">
          <summary>{b.label}</summary>
          {b.checks.map((c) => (
            <div key={c}>{c}</div>
          ))}
          {b.not_built && <div className="muted">not built yet (🚧 stub reply)</div>}
        </details>
      ))}
      <p>
        <strong>Next:</strong> <code>{s.next}</code>
      </p>
      <button className="secondary" onClick={onReset}>
        🔄 Reset demo data
      </button>
    </aside>
  );
}
