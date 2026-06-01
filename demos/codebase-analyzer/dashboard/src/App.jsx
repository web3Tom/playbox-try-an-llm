import { useEffect, useMemo, useState } from 'react'
import Graph from './Graph'

// A small, fixed palette assigned to layers in order. Enough distinct hues for
// the 3–6 layers the architecture stage produces.
const PALETTE = ['#0066cc', '#cc6600', '#2e9e5b', '#9b59b6', '#d9534f', '#16a2b8']

export default function App() {
  const [graph, setGraph] = useState(null)
  const [error, setError] = useState(null)
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    fetch('/knowledge-graph.json')
      .then((r) => {
        if (!r.ok) throw new Error(`could not load knowledge-graph.json (${r.status})`)
        return r.json()
      })
      .then(setGraph)
      .catch((e) => setError(e.message))
  }, [])

  // Map each layer id -> color, in the order layers appear.
  const layerColors = useMemo(() => {
    if (!graph) return {}
    return Object.fromEntries(graph.layers.map((l, i) => [l.id, PALETTE[i % PALETTE.length]]))
  }, [graph])

  if (error) {
    return (
      <div className="app">
        <div className="empty-state">
          <h2>No graph to show</h2>
          <p>{error}</p>
          <p>Run the analyzer first:</p>
          <code>uv run python demos/codebase-analyzer/analyze.py</code>
        </div>
      </div>
    )
  }

  if (!graph) return <div className="app"><div className="empty-state">Loading…</div></div>

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>{graph.project.name}</h1>
          <p className="subtitle">{graph.project.description}</p>
        </div>
        <div className="stats">
          <span>{graph.nodes.length} files</span>
          <span>{graph.edges.length} imports</span>
          <span>{graph.layers.length} layers</span>
          {graph.project.truncated && (
            <span className="warn" title="The repo had more files than the analysis cap.">
              ⚠ truncated ({graph.project.analyzedFileCount}/{graph.project.fileCount})
            </span>
          )}
        </div>
      </header>

      <div className="body">
        <Graph graph={graph} layerColors={layerColors} onSelect={setSelected} />

        <aside className="sidebar">
          <section>
            <h3>Layers</h3>
            <ul className="legend">
              {graph.layers.map((l) => (
                <li key={l.id}>
                  <span className="swatch" style={{ background: layerColors[l.id] }} />
                  <span className="legend-text">
                    <strong>{l.name}</strong>
                    <small>{l.description}</small>
                  </span>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h3>Selected file</h3>
            {selected ? (
              <div className="node-detail">
                <code>{selected.filePath}</code>
                <p>{selected.summary || 'No summary.'}</p>
                <p className="meta">complexity: {selected.complexity}</p>
                {selected.tags?.length > 0 && (
                  <div className="tags">
                    {selected.tags.map((t) => <span key={t} className="tag">{t}</span>)}
                  </div>
                )}
              </div>
            ) : (
              <p className="hint">Click a node to inspect it.</p>
            )}
          </section>
        </aside>
      </div>

      <footer className="app-footer">
        <p>Extend this dashboard with the Kilo Code react-frontend role (gpt-5.2).</p>
      </footer>
    </div>
  )
}
