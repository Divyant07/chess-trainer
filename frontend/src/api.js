const BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request to ${path} failed (${res.status})`)
  }
  return res.json()
}

export const api = {
  listRepertoires: () => request('/repertoires'),
  createRepertoire: (name, color) =>
    request('/repertoires', {
      method: 'POST',
      body: JSON.stringify({ name, color }),
    }),
  listNodes: (repertoireId) => request(`/repertoires/${repertoireId}/nodes`),
  createNode: (repertoireId, parentId, move) =>
    request(`/repertoires/${repertoireId}/nodes`, {
      method: 'POST',
      body: JSON.stringify({ parent_id: parentId, move }),
    }),
  getNextCard: (repertoireId) =>
    request(`/training/next-card?repertoire_id=${repertoireId}`),
  submitAnswer: (nodeId, correct) =>
    request('/training/answer', {
      method: 'POST',
      body: JSON.stringify({ node_id: nodeId, correct }),
    }),
  getEngineMove: (fen, elo) =>
    request('/play/engine-move', {
      method: 'POST',
      body: JSON.stringify({ fen, elo }),
    }),
  getNextTactic: () => request('/tactics/next-card'),
  submitTacticAnswer: (tacticId, move) =>
    request('/tactics/answer', {
      method: 'POST',
      body: JSON.stringify({ tactic_id: tacticId, move }),
    }),
}