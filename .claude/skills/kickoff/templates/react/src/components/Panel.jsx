// One owner-dashboard panel: an honest ⬜ placeholder until its phase is ticked, then metrics / a table / lines.
export default function Panel({ p }) {
  return (
    <article className="panel">
      <h2>{p.name}</h2>
      {p.text && <p className="placeholder">{p.text}</p>}
      {p.warning && <p className="warning">{p.warning}</p>}
      {p.kind === "metrics" && (
        <div className="metrics">
          {p.items.map((m) => (
            <div key={m.label} className="metric">
              <span>{m.label}</span>
              <strong>{String(m.value)}</strong>
            </div>
          ))}
        </div>
      )}
      {p.kind === "table" &&
        (p.rows.length ? (
          <table>
            <thead>
              <tr>
                {Object.keys(p.rows[0]).map((k) => (
                  <th key={k}>{k}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {p.rows.map((r, i) => (
                <tr key={i}>
                  {Object.values(r).map((v, j) => (
                    <td key={j}>{String(v)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="muted">{p.empty || "Nothing yet."}</p>
        ))}
      {p.kind === "lines" && p.lines.map((l) => <p key={l}>{l}</p>)}
    </article>
  );
}
