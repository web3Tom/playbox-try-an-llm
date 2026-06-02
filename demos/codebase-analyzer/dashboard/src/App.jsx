import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import Graph from './Graph'

// One hue per layer, assigned in order. Tuned to read well as both a filled
// member node and a translucent file-box border.
const PALETTE = ['#2563eb', '#ea580c', '#16a34a', '#9333ea', '#dc2626', '#0891b2']

export default function App() {
  const [graph, setGraph] = useState(null)
  const [error, setError] = useState(null)
  const [selected, setSelected] = useState(null)
  const [showMembers, setShowMembers] = useState(true)
  const [query, setQuery] = useState('')
  const [hiddenLayers, setHiddenLayers] = useState(new Set())
  const cyRef = useRef(null)

  // Stable identity so Graph's effect doesn't rebuild the whole cytoscape graph
  // (and re-run the layout) on every unrelated render — e.g. selecting a node.
  const handleReady = useCallback((cy) => { cyRef.current = cy }, [])

  useEffect(() => {
    fetch('/knowledge-graph.json')
      .then((r) => {
        if (!r.ok) throw new Error(`could not load knowledge-graph.json (${r.status})`)
        return r.json()
      })
      .then(setGraph)
      .catch((e) => setError(e.message))
  }, [])

  const layerColors = useMemo(() => {
    if (!graph) return {}
    return Object.fromEntries(graph.layers.map((l, i) => [l.id, PALETTE[i % PALETTE.length]]))
  }, [graph])

  // filePath -> the file's member nodes (functions/classes), for the detail panel.
  const membersByPath = useMemo(() => {
    const map = {}
    if (!graph) return map
    for (const n of graph.nodes) {
      if (n.type === 'function' || n.type === 'class') {
        ;(map[n.filePath] ||= []).push(n)
      }
    }
    return map
  }, [graph])

  const fileNodes = useMemo(
    () => (graph ? graph.nodes.filter((n) => n.type === 'file') : []),
    [graph]
  )
  const memberCount = useMemo(
    () => (graph ? graph.nodes.filter((n) => n.type !== 'file').length : 0),
    [graph]
  )

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

  const selectedMembers = selected?.type === 'file' ? membersByPath[selected.filePath] || [] : []
  const parentFile =
    selected && selected.type !== 'file'
      ? fileNodes.find((f) => f.filePath === selected.filePath)
      : null

  return (
    <div className="app">
      <header className="app-header">
        <div className="title-block">
          <h1>{graph.project.name}</h1>
          <p className="subtitle">{graph.project.description}</p>
        </div>
        <div className="stats">
          <span className="stat"><b>{fileNodes.length}</b> files</span>
          <span className="stat"><b>{memberCount}</b> modules</span>
          <span className="stat"><b>{graph.edges.length}</b> edges</span>
          <span className="stat"><b>{graph.layers.length}</b> layers</span>
          {graph.project.truncated && (
            <span className="stat warn" title="The repo had more files than the analysis cap.">
              ⚠ {graph.project.analyzedFileCount}/{graph.project.fileCount}
            </span>
          )}
        </div>
      </header>

      <div className="toolbar">
        <input
          className="search"
          type="search"
          placeholder="Search files, functions, classes…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <label className="toggle">
          <input
            type="checkbox"
            checked={showMembers}
            onChange={(e) => setShowMembers(e.target.checked)}
          />
          Show modules
        </label>
        <span className="shape-key">
          <i className="k-file" /> file
          <i className="k-fn" /> function
          <i className="k-cls" /> class
        </span>
        <span className="edge-legend">
          <i className="k-edge k-edge-imports" />
          imports
          <i className="k-edge k-edge-calls" />
          calls
          <i className="k-edge k-edge-inherits" />
          inherits
        </span>
        <button
          className="btn-export"
          onClick={() => {
            if (cyRef.current) {
              const png = cyRef.current.png({ full: true, scale: 2, bg: '#ffffff' })
              const a = document.createElement('a')
              a.href = png
              a.download = `${graph.project.name}-graph.png`
              a.click()
            }
          }}
        >
          Export PNG
        </button>
        <button
          className="btn-export"
          onClick={() => {
            const json = JSON.stringify(graph, null, 2)
            const blob = new Blob([json], { type: 'application/json' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `${graph.project.name}-knowledge-graph.json`
            a.click()
            URL.revokeObjectURL(url)
          }}
        >
          Export JSON
        </button>
      </div>

      <div className="body">
        <Graph
          graph={graph}
          layerColors={layerColors}
          onSelect={setSelected}
          showMembers={showMembers}
          query={query}
          hiddenLayers={hiddenLayers}
          onReady={handleReady}
        />

        <aside className="sidebar">
          <section className="card">
            <h3>Layers</h3>
            <ul className="legend">
              {graph.layers.map((l) => {
                const isHidden = hiddenLayers.has(l.id)
                return (
                  <li
                    key={l.id}
                    className={`layer-row ${isHidden ? 'hidden' : ''}`}
                    onClick={() => {
                      const updated = new Set(hiddenLayers)
                      if (isHidden) {
                        updated.delete(l.id)
                      } else {
                        updated.add(l.id)
                      }
                      setHiddenLayers(updated)
                    }}
                  >
                    <span className="swatch" style={{ background: layerColors[l.id] }} />
                    <span className="legend-text">
                      <strong>{l.name}</strong>
                      <small>{l.description}</small>
                    </span>
                  </li>
                )
              })}
            </ul>
          </section>

          {graph.tour && graph.tour.length > 0 && (
            <section className="card">
              <h3>Guided Tour</h3>
              <ul className="tour-list">
                {graph.tour.map((step) => (
                  <li key={step.order} className="tour-step">
                    <div className="tour-header">
                      <span className="tour-number">{step.order}</span>
                      <h4 className="tour-title">{step.title}</h4>
                    </div>
                    <p className="tour-explanation">{step.explanation}</p>
                    <button
                      className="tour-button"
                      onClick={() => {
                        const fileNode = graph.nodes.find((n) => n.filePath === step.filePath && n.type === 'file')
                        if (fileNode) setSelected(fileNode)
                      }}
                    >
                      Go to {step.filePath}
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          )}

          <section className="card">
            <h3>{selected ? (selected.type === 'file' ? 'Selected file' : 'Selected module') : 'Inspector'}</h3>
            {!selected && <p className="hint">Click a file box or a module to inspect it.</p>}

            {selected && (
              <div className="node-detail">
                <code>{selected.filePath}</code>
                {parentFile && (
                  <p className="backlink">
                    <span className={`pill pill-${selected.type}`}>{selected.type}</span>
                    in <button className="linkish" onClick={() => setSelected(parentFile)}>{parentFile.name}</button>
                  </p>
                )}
                <p>{selected.summary || 'No summary.'}</p>
                <p className="meta">
                  complexity:{' '}
                  <span className={`badge badge-${selected.complexity}`}>{selected.complexity}</span>
                </p>
                {selected.tags?.length > 0 && (
                  <div className="tags">
                    {selected.tags.map((t) => <span key={t} className="tag">{t}</span>)}
                  </div>
                )}

                {selected.type === 'file' && (
                  <div className="members">
                    <h4>Modules ({selectedMembers.length})</h4>
                    {selectedMembers.length === 0 ? (
                      <p className="hint">No top-level functions or classes extracted.</p>
                    ) : (
                      <ul className="member-list">
                        {selectedMembers.map((m) => (
                          <li key={m.id}>
                            <button className="member-item" onClick={() => setSelected(m)}>
                              <span className={`pill pill-${m.type}`}>{m.type === 'class' ? 'C' : 'ƒ'}</span>
                              <span className="member-name">{m.name}</span>
                            </button>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </div>
            )}
          </section>

          <section className="card">
            <h3>Files</h3>
            <ul className="file-list">
              {fileNodes.map((f) => {
                const count = (membersByPath[f.filePath] || []).length
                return (
                  <li key={f.id}>
                    <button
                      className={`file-item ${selected?.id === f.id ? 'active' : ''}`}
                      onClick={() => setSelected(f)}
                    >
                      <span className="dot" style={{ background: layerColors[f.layer] }} />
                      <span className="file-name">{f.name}</span>
                      <span className="file-count">{count}</span>
                    </button>
                  </li>
                )
              })}
            </ul>
          </section>
        </aside>
      </div>

      <footer className="app-footer">
        <p>Files contain their top-level functions &amp; classes · extend with the Kilo react-frontend role (gpt-5.2).</p>
      </footer>
    </div>
  )
}
