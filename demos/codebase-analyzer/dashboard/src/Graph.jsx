import { useEffect, useRef } from 'react'
import cytoscape from 'cytoscape'

// Renders the knowledge graph with cytoscape's built-in force-directed (cose)
// layout. Nodes are colored by architectural layer; clicking one calls onSelect.
export default function Graph({ graph, layerColors, onSelect }) {
  const containerRef = useRef(null)

  useEffect(() => {
    if (!containerRef.current || !graph) return

    const elements = [
      ...graph.nodes.map((n) => ({
        data: { id: n.id, label: n.name, layer: n.layer || 'none' }
      })),
      ...graph.edges.map((e) => ({
        data: { source: e.source, target: e.target, type: e.type }
      }))
    ]

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': (ele) => layerColors[ele.data('layer')] || '#888',
            label: 'data(label)',
            color: 'var(--color-text)',
            'font-size': '11px',
            'text-valign': 'bottom',
            'text-margin-y': 4,
            width: 26,
            height: 26
          }
        },
        {
          selector: 'edge',
          style: {
            width: 1.5,
            'line-color': '#bbb',
            'target-arrow-color': '#bbb',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            opacity: 0.6
          }
        },
        {
          selector: 'node:selected',
          style: { 'border-width': 3, 'border-color': 'var(--color-accent)' }
        }
      ],
      layout: { name: 'cose', animate: false, padding: 30, nodeRepulsion: 8000 }
    })

    cy.on('tap', 'node', (evt) => {
      const node = graph.nodes.find((n) => n.id === evt.target.id())
      onSelect(node || null)
    })
    cy.on('tap', (evt) => {
      if (evt.target === cy) onSelect(null) // tap background clears selection
    })

    return () => cy.destroy()
  }, [graph, layerColors, onSelect])

  return <div ref={containerRef} className="graph-canvas" />
}
