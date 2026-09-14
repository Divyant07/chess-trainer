import { useEffect, useState } from 'react'
import { Chessboard } from 'react-chessboard'
import { Chess } from 'chess.js'
import { api } from './api'

const ELO_PRESETS = [
  { label: 'Beginner (~800)', value: 800 },
  { label: 'Casual (~1200)', value: 1200 },
  { label: 'Club player (~1600)', value: 1600 },
  { label: 'Strong club (~2000)', value: 2000 },
  { label: 'Expert (~2400)', value: 2400 },
  { label: 'Master (~2800)', value: 2800 },
]

/** Parses a UCI move string like "e2e4" or "e7e8q" into chess.js's move format. */
function uciToMoveObject(uci) {
  return {
    from: uci.slice(0, 2),
    to: uci.slice(2, 4),
    promotion: uci.length > 4 ? uci[4] : undefined,
  }
}

function PlayEngineView() {
  const [elo, setElo] = useState(1200)
  const [userColor, setUserColor] = useState('white')
  const [game, setGame] = useState(() => new Chess())
  const [fen, setFen] = useState('start')
  const [thinking, setThinking] = useState(false)
  const [statusMsg, setStatusMsg] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    startNewGame(userColor)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function describeGameOver(g) {
    if (g.isCheckmate()) {
      // The side whose turn it is has been mated -- so the OTHER side won.
      const winner = g.turn() === 'w' ? 'Black' : 'White'
      return `Checkmate -- ${winner} wins`
    }
    if (g.isStalemate()) return 'Draw by stalemate'
    if (g.isThreefoldRepetition()) return 'Draw by repetition'
    if (g.isInsufficientMaterial()) return 'Draw by insufficient material'
    if (g.isDraw()) return 'Draw'
    return null
  }

  function startNewGame(color) {
    const g = new Chess()
    setGame(g)
    setFen(g.fen())
    setStatusMsg(null)
    setError(null)
    setUserColor(color)

    if (color === 'black') {
      // Engine plays White's first move automatically.
      requestEngineMove(g)
    }
  }

  async function requestEngineMove(currentGame) {
    setThinking(true)
    try {
      const res = await api.getEngineMove(currentGame.fen(), elo)
      if (!res.move_uci) {
        // Engine had no legal move -- game was already over.
        setStatusMsg(describeGameOver(currentGame) || 'Game over')
        setThinking(false)
        return
      }
      currentGame.move(uciToMoveObject(res.move_uci))
      setFen(currentGame.fen())

      const overMsg = describeGameOver(currentGame)
      if (overMsg) setStatusMsg(overMsg)
    } catch (err) {
      setError(err.message)
    }
    setThinking(false)
  }

  function onDrop(sourceSquare, targetSquare) {
    if (thinking || statusMsg) return false

    const userTurnChar = userColor === 'white' ? 'w' : 'b'
    if (game.turn() !== userTurnChar) return false

    const move = game.move({ from: sourceSquare, to: targetSquare, promotion: 'q' })
    if (move === null) return false
    setFen(game.fen())

    const overMsg = describeGameOver(game)
    if (overMsg) {
      setStatusMsg(overMsg)
      return true
    }

    requestEngineMove(game)
    return true
  }

  function undoLastRound() {
    if (thinking) return
    // Undo both the engine's reply and your move, so you land back on
    // your own turn rather than the engine's -- a "takeback" undoes the
    // full round-trip, not just one ply.
    game.undo()
    game.undo()
    setFen(game.fen())
    setStatusMsg(null)
    setError(null)
  }

  const canUndo = game.history().length >= 2 && !thinking

  return (
    <div className="play-engine-view">
      <div className="play-controls">
        <label>
          Strength:
          <select
            value={elo}
            onChange={(e) => setElo(Number(e.target.value))}
            disabled={thinking}
          >
            {ELO_PRESETS.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          Play as:
          <select
            value={userColor}
            onChange={(e) => startNewGame(e.target.value)}
            disabled={thinking}
          >
            <option value="white">White</option>
            <option value="black">Black</option>
          </select>
        </label>
      </div>

      <div className="board-wrapper">
        <Chessboard
          position={fen}
          onPieceDrop={onDrop}
          boardWidth={480}
          boardOrientation={userColor}
        />
      </div>

      <div className="training-feedback">
        {thinking && <p className="hint">Engine is thinking...</p>}
        {statusMsg && <p className="feedback ok">{statusMsg}</p>}
        {error && <p className="feedback warn">Error: {error}</p>}
      </div>

      <div className="board-actions">
        <button onClick={() => startNewGame(userColor)}>New game</button>
        <button onClick={undoLastRound} disabled={!canUndo}>
          Undo
        </button>
      </div>

      <p className="hint">
        Set the engine's approximate strength and play a full game. Undo
        takes back your last move and the engine's reply together.
      </p>
    </div>
  )
}

export default PlayEngineView