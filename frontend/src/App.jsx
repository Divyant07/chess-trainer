import { useEffect, useMemo, useState } from 'react'
import { Chessboard } from 'react-chessboard'
import { Chess } from 'chess.js'
import { api } from './api'
import { buildChildrenMap, collectLines, findRoot, formatLine } from './repertoireTree'
import RepertoireSidebar from './RepertoireSidebar'
import TrainingView from './TrainingView'
import PlayEngineView from './PlayEngineView'
import TacticsView from './TacticsView'
import './App.css'

function App() {
  const [apiStatus, setApiStatus] = useState('checking...')
  const [mode, setMode] = useState('build') // 'build' | 'train'

  const [repertoires, setRepertoires] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [nodes, setNodes] = useState([])
  const [loadError, setLoadError] = useState(null)

  // The live board state for "free play" -- not saved until the user
  // explicitly clicks "Save line".
  const [game] = useState(() => new Chess())
  const [fen, setFen] = useState(game.fen())
  const [saveStatus, setSaveStatus] = useState(null) // null | 'saving' | 'saved' | error string

  // --- initial load: health check + repertoires list ---
  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => setApiStatus(data.status === 'ok' ? 'connected' : 'unexpected response'))
      .catch(() => setApiStatus('backend unreachable (is it running on :8000?)'))

    api
      .listRepertoires()
      .then((data) => {
        setRepertoires(data)
        if (data.length > 0) setSelectedId(data[0].id)
      })
      .catch((err) => setLoadError(err.message))
  }, [])

  // --- fetch nodes whenever the selected repertoire changes ---
  useEffect(() => {
    if (selectedId == null) {
      setNodes([])
      return
    }
    api
      .listNodes(selectedId)
      .then(setNodes)
      .catch((err) => setLoadError(err.message))
  }, [selectedId])

  const childrenMap = useMemo(() => buildChildrenMap(nodes), [nodes])
  const root = useMemo(() => findRoot(nodes), [nodes])
  const lines = useMemo(() => {
    if (!root) return []
    return collectLines(root.id, childrenMap).map((path) => ({
      path,
      text: formatLine(path),
    }))
  }, [root, childrenMap])

  async function handleCreateRepertoire(name, color) {
    try {
      const created = await api.createRepertoire(name, color)
      setRepertoires((prev) => [...prev, created])
      setSelectedId(created.id)
    } catch (err) {
      setLoadError(err.message)
    }
  }

  function resetBoard() {
    game.reset()
    setFen(game.fen())
    setSaveStatus(null)
  }

  function onDrop(sourceSquare, targetSquare) {
    const move = game.move({ from: sourceSquare, to: targetSquare, promotion: 'q' })
    if (move === null) return false
    setFen(game.fen())
    setSaveStatus(null)
    return true
  }

  function loadLine(path) {
    game.reset()
    for (const node of path) {
      game.move(node.move_san)
    }
    setFen(game.fen())
    setSaveStatus(null)
  }

  async function saveCurrentLine() {
    if (!selectedId || !root) return
    const sanMoves = game.history()
    if (sanMoves.length === 0) return

    setSaveStatus('saving')
    try {
      // Walk from the root, reusing existing nodes where the line already
      // matches saved moves, and only creating nodes where it diverges or
      // extends past what's saved. This lets you replay an existing line
      // and extend it further without creating duplicate branches.
      let parentId = root.id
      let currentChildrenMap = childrenMap
      const newNodes = []

      for (const san of sanMoves) {
        const existing = (currentChildrenMap[parentId] || []).find(
          (n) => n.move_san === san
        )
        if (existing) {
          parentId = existing.id
          continue
        }
        const created = await api.createNode(selectedId, parentId, san)
        newNodes.push(created)
        currentChildrenMap = {
          ...currentChildrenMap,
          [parentId]: [...(currentChildrenMap[parentId] || []), created],
        }
        parentId = created.id
      }

      if (newNodes.length > 0) {
        setNodes((prev) => [...prev, ...newNodes])
      }
      setSaveStatus('saved')
    } catch (err) {
      setSaveStatus(err.message)
    }
  }

  const currentLineText =
    game.history().length > 0
      ? formatLine(
          game.history().map((san, i) => ({ move_san: san, id: `preview-${i}` }))
        )
      : '(no moves played yet)'

  return (
    <div className="app-layout">
      <RepertoireSidebar
        repertoires={repertoires}
        selectedId={selectedId}
        onSelect={setSelectedId}
        onCreate={handleCreateRepertoire}
        lines={lines}
        onLineClick={(line) => loadLine(line.path)}
      />

      <main className="main-panel">
        <header>
          <h1>Chess Trainer</h1>
          <p className={`api-status ${apiStatus === 'connected' ? 'ok' : 'warn'}`}>
            Backend: {apiStatus}
          </p>
          {loadError && <p className="api-status warn">Error: {loadError}</p>}
        </header>

        <div className="mode-tabs">
          <button
            className={mode === 'build' ? 'active' : ''}
            onClick={() => setMode('build')}
          >
            Build
          </button>
          <button
            className={mode === 'train' ? 'active' : ''}
            onClick={() => setMode('train')}
          >
            Train
          </button>
          <button
            className={mode === 'play' ? 'active' : ''}
            onClick={() => setMode('play')}
          >
            Play Engine
          </button>
          <button
            className={mode === 'tactics' ? 'active' : ''}
            onClick={() => setMode('tactics')}
          >
            Tactics
          </button>
        </div>

        {mode === 'build' && (
          <>
            <div className="board-wrapper">
              <Chessboard position={fen} onPieceDrop={onDrop} boardWidth={480} />
            </div>

            <div className="current-line">
              <strong>Current line:</strong> {currentLineText}
            </div>

            <div className="board-actions">
              <button onClick={resetBoard}>Reset board</button>
              <button
                onClick={saveCurrentLine}
                disabled={!selectedId || game.history().length === 0}
              >
                Save line
              </button>
              {saveStatus === 'saving' && <span className="save-status">Saving...</span>}
              {saveStatus === 'saved' && <span className="save-status ok">Saved ✓</span>}
              {saveStatus && !['saving', 'saved'].includes(saveStatus) && (
                <span className="save-status warn">{saveStatus}</span>
              )}
            </div>

            <p className="hint">
              Play a line freely on the board, then hit "Save line" to add it
              to your repertoire. Click a saved line in the sidebar to load
              it back onto the board -- you can then keep playing to extend
              it further.
            </p>
          </>
        )}

        {mode === 'train' && <TrainingView repertoireId={selectedId} />}
        {mode === 'play' && <PlayEngineView />}
        {mode === 'tactics' && <TacticsView />}
      </main>
    </div>
  )
}

export default App