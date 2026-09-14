/**
 * The backend returns nodes as a flat list (see repertoires.py: list_nodes).
 * These helpers turn that flat list into something the UI can walk --
 * a children-by-parent-id map -- and enumerate root-to-leaf paths for
 * the sidebar's "saved lines" view.
 */

export function findRoot(nodes) {
  return nodes.find((n) => n.parent_id === null) || null
}

export function buildChildrenMap(nodes) {
  const map = {}
  for (const node of nodes) {
    if (node.parent_id === null) continue
    if (!map[node.parent_id]) map[node.parent_id] = []
    map[node.parent_id].push(node)
  }
  return map
}

/**
 * Returns every root-to-leaf path in the tree as an array of move lists,
 * e.g. [["e4", "e5", "Nf3"], ["e4", "c5"]] -- one entry per saved line.
 */
export function collectLines(rootId, childrenMap) {
  const results = []

  function walk(nodeId, path) {
    const children = childrenMap[nodeId] || []
    if (children.length === 0) {
      if (path.length > 0) results.push(path)
      return
    }
    for (const child of children) {
      walk(child.id, [...path, child])
    }
  }

  walk(rootId, [])
  return results
}

/** Formats a path of nodes as "1. e4 e5 2. Nf3" style move text. */
export function formatLine(path) {
  return path
    .map((node, i) => {
      const moveNumber = Math.floor(i / 2) + 1
      const isWhiteMove = i % 2 === 0
      return isWhiteMove ? `${moveNumber}. ${node.move_san}` : node.move_san
    })
    .join(' ')
}