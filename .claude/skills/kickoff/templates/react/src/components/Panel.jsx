// One owner-dashboard panel: an honest placeholder (what it will show, and when) until its phase is ticked,
// then metrics / a table / lines. `wide` and `shows` come from ui/api.py (plan §2b).
import { Clock } from "lucide-react";

export default function Panel({ p }) {
  return (
    <article className={`panel${p.wide ? " wide" : ""}${p.live ? "" : " pending"}`}>
      <header>
        <h2>{p.name}</h2>
        {!p.live && (
          <span className="badge">
            <Clock size={12} aria-hidden /> Phase {p.phase}
          </span>
        )}
      </header>
      {p.text && <p className="placeholder">{p.text}</p>}
      {p.text && p.shows && <p className="shows">Will show: {p.shows}</p>}
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
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  {Object.keys(p.rows[0]).map((k) => (
                    <th key={k} scope="col">
                      {k}
                    </th>
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
          </div>
        ) : (
          <p className="muted">{p.empty || "Nothing yet."}</p>
        ))}
      {p.kind === "lines" && p.lines.map((l) => <p key={l}>{l}</p>)}
    </article>
  );
}
