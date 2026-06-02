import { useEffect, useRef } from 'react'
import cytoscape from 'cytoscape'

// Files render as COMPOUND nodes (boxes) that contain their top-level functions
// and classes. Containment is derived from the shared `filePath` — a member is
// parented to the file node with the same path. Import edges connect the file
// boxes. Colour follows architectural layer; shape distinguishes file (box) /
// function (ellipse) / class (hexagon).
export default function Graph({ graph, layerColors, onSelect, showMembers, query, hiddenLayers, onReady }) {
  const containerRef = useRef(null)

  useEffect(() => {
    if (!containerRef.current || !graph) return

    const fileNodes = graph.nodes.filter((n) => n.type === 'file')
    const memberNodes = graph.nodes.filter((n) => n.type === 'function' || n.type === 'class')

    // filePath -> file node id, so members can be parented to their file.
    const pathToFileId = Object.fromEntries(fileNodes.map((n) => [n.filePath, n.id]))

    // Compute visible nodes: exclude files in hidden layers and their members.
    const visibleFileIds = new Set(
      fileNodes
        .filter((n) => !hiddenLayers?.has(n.layer))
        .map((n) => n.id)
    )
    const visibleMemberIds = new Set(
      memberNodes
        .filter((n) => !hiddenLayers?.has(n.layer))
        .map((n) => n.id)
    )
    const visibleIds = new Set([...visibleFileIds, ...visibleMemberIds])

    const elements = [
      ...fileNodes
        .filter((n) => visibleFileIds.has(n.id))
        .map((n) => ({
          data: { id: n.id, label: n.name, layer: n.layer || 'none', kind: 'file' }
        })),
      ...(showMembers ? memberNodes : [])
        .filter((n) => visibleMemberIds.has(n.id))
        .map((n) => ({
          data: { id: n.id, label: n.name, layer: n.layer || 'none', kind: n.type, parent: pathToFileId[n.filePath] }
        })),
      // Import edges connect file boxes; both endpoints are always file nodes.
      ...graph.edges
        .filter((e) => e.type === 'imports' && visibleIds.has(e.source) && visibleIds.has(e.target))
        .map((e) => ({ data: { source: e.source, target: e.target, type: e.type } })),
      // Calls and inherits edges connect members; only add if showMembers is on.
      ...(showMembers
        ? graph.edges
            .filter((e) => (e.type === 'calls' || e.type === 'inherits') && visibleIds.has(e.source) && visibleIds.has(e.target))
            .map((e) => ({ data: { source: e.source, target: e.target, type: e.type } }))
        : [])
    ]

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': (ele) => layerColors[ele.data('layer')] || '#94a3b8',
            label: 'data(label)',
            color: '#0f172a',
            'font-size': '11px',
            'font-weight': 500,
            'text-valign': 'bottom',
            'text-margin-y': 4,
            width: 24,
            height: 24
          }
        },
        {
          selector: 'node[kind="function"]',
          style: {
            shape: 'ellipse',
            width: 20,
            height: 20,
            'text-valign': 'center',
            'text-margin-y': 0,
            color: '#ffffff',
            'font-size': '9px',
            'text-outline-width': 2,
            'text-outline-color': (ele) => layerColors[ele.data('layer')] || '#94a3b8'
          }
        },
        {
          selector: 'node[kind="class"]',
          style: {
            shape: 'hexagon',
            width: 26,
            height: 24,
            'text-valign': 'center',
            'text-margin-y': 0,
            color: '#ffffff',
            'font-size': '9px',
            'text-outline-width': 2,
            'text-outline-color': (ele) => layerColors[ele.data('layer')] || '#94a3b8'
          }
        },
        {
          // Any node with children becomes a labelled container box.
          selector: ':parent',
          style: {
            shape: 'round-rectangle',
            'background-color': (ele) => layerColors[ele.data('layer')] || '#94a3b8',
            'background-opacity': 0.08,
            'border-width': 2,
            'border-color': (ele) => layerColors[ele.data('layer')] || '#94a3b8',
            'border-opacity': 0.7,
            label: 'data(label)',
            'text-valign': 'top',
            'text-halign': 'center',
            'text-margin-y': -4,
            'font-weight': 700,
            'font-size': '12px',
            color: '#0f172a',
            padding: 14
          }
        },
        {
          selector: 'edge',
          style: {
            width: 1.6,
            'line-color': '#cbd5e1',
            'target-arrow-color': '#cbd5e1',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            opacity: 0.75
          }
        },
        {
          selector: 'edge[type="calls"]',
          style: {
            'line-color': '#2563eb',
            'target-arrow-color': '#2563eb'
          }
        },
        {
          selector: 'edge[type="inherits"]',
          style: {
            'line-color': '#9333ea',
            'target-arrow-color': '#9333ea',
            'line-style': 'dashed'
          }
        },
        {
          selector: 'node:selected',
          style: { 'border-width': 3, 'border-color': '#2563eb', 'border-opacity': 1 }
        },
        { selector: '.dim', style: { opacity: 0.12 } }
      ],
      layout: {
        name: 'cose',
        animate: false,
        padding: 36,
        nodeRepulsion: 9000,
        idealEdgeLength: 120,
        componentSpacing: 120,
        nestingFactor: 0.9
      }
    })

    // Search: dim everything that doesn't match (and isn't kin of a match).
    const q = (query || '').trim().toLowerCase()
    if (q) {
      const matched = new Set()
      cy.nodes().forEach((n) => {
        if ((n.data('label') || '').toLowerCase().includes(q)) {
          matched.add(n.id())
          n.parent().forEach((p) => matched.add(p.id()))
          n.children().forEach((c) => matched.add(c.id()))
        }
      })
      cy.nodes().forEach((n) => { if (!matched.has(n.id())) n.addClass('dim') })
    }

    cy.on('tap', 'node', (evt) => {
      const node = graph.nodes.find((n) => n.id === evt.target.id())
      onSelect(node || null)
    })
    cy.on('tap', (evt) => { if (evt.target === cy) onSelect(null) })

    onReady?.(cy)
    return () => {
      onReady?.(null)
      cy.destroy()
    }
  }, [graph, layerColors, onSelect, showMembers, query, hiddenLayers, onReady])

  return <div ref={containerRef} className="graph-canvas" />
}
