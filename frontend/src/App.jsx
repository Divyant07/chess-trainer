import { useEffect, useState } from 'react'
import { Chessboard } from 'react-chessboard'
import { Chess } from 'chess.js'
import './App.css'

function App() {
  const [game] = useState(() => new Chess())
  const [fen, setFen] = useState(game.fen())
  const [apiStatus, setApiStatus] = useState('checking...')

  // Phase 0 milestone: confirm frontend can reach the FastAPI backend.
  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => setApiStatus(data.status === 'ok' ? 'connected' : 'unexpected response'))
      .catch(() => setApiStatus('backend unreachable (is it running on :8000?)'))
  }, [])

  // Click-to-move handling comes in Phase 1 -- this just proves the board
  // is interactive and legal moves are enforced via chess.js.
  function onDrop(sourceSquare, targetSquare) {
    const move = game.move({
      from: sourceSquare,
      to: targetSquare,
      promotion: 'q',
    })
    if (move === null) return false // illegal move, snap back
    setFen(game.fen())
    return true
  }

  return (
    <div className="app">
      <header>
        <h1>Chess Trainer</h1>
        <p className={`api-status ${apiStatus === 'connected' ? 'ok' : 'warn'}`}>
          Backend: {apiStatus}
        </p>
      </header>

      <div className="board-wrapper">
        <Chessboard position={fen} onPieceDrop={onDrop} boardWidth={480} />
      </div>

      <p className="hint">
        This is the Phase 0 scaffold: a working board (chess.js enforces legal
        moves) and a live connection to the FastAPI backend. Repertoire
        building comes next.
      </p>
    </div>
  )
}

export default App
