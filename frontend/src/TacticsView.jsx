import { useEffect, useState } from 'react'
import { Chessboard } from 'react-chessboard'
import { Chess } from 'chess.js'
import { api } from './api'

function TacticsView() {
  const [card, setCard] = useState(undefined) // undefined = loading, null = none due
  const [fen, setFen] = useState('start')
  const [feedback, setFeedback] = useState(null) // null | 'correct' | 'incorrect'
  const [correctMoveSan, setCorrectMoveSan] = useState(null)
  const [error, setError] = useState(null)

  async function loadNextTactic() {
    setFeedback(null)
    setCorrectMoveSan(null)
    setError(null)
    setCard(undefined)
    try {
      const next = await api.getNextTactic()
      setCard(next)
      setFen(next ? next.fen : 'start')
    } catch (err) {
      setError(err.message)
      setCard(null)
    }
  }

  useEffect(() => {
    loadNextTactic()
  }, [])

  async function onDrop(sourceSquare, targetSquare) {
    if (!card || feedback) return false

    // Try the move locally first purely to get its SAN/legality -- the
    // actual correctness check happens server-side against the stored
    // solution, since the solution move isn't sent to the client.
    const attempt = new Chess(card.fen)
    const move = attempt.move({ from: sourceSquare, to: targetSquare, promotion: 'q' })
    if (move === null) return false

    setFen(attempt.fen())

    try {
      const result = await api.submitTacticAnswer(card.tactic_id, move.san)
      setFeedback(result.correct ? 'correct' : 'incorrect')
      setCorrectMoveSan(result.correct_move_san)
    } catch (err) {
      setError(err.message)
    }
    return true
  }

  if (card === undefined) {
    return <p className="hint">Loading...</p>
  }

  if (card === null) {
    return (
      <div className="training-empty">
        <p>🎉 No tactics due right now.</p>
        <p className="hint">
          Add more puzzles (see backend/README.md for how to import a free
          puzzle set) or check back later.
        </p>
        <button onClick={loadNextTactic}>Check again</button>
      </div>
    )
  }

  return (
    <div className="tactics-view">
      <p className="due-count">{card.due_count} puzzle(s) due</p>
      {card.motif_tags.length > 0 && (
        <p className="motif-tags">{card.motif_tags.join(', ')}</p>
      )}

      <div className="board-wrapper">
        <Chessboard position={fen} onPieceDrop={onDrop} boardWidth={480} />
      </div>

      <div className="training-feedback">
        {feedback === null && <p className="hint">Find the best move.</p>}
        {feedback === 'correct' && <p className="feedback ok">✓ Correct!</p>}
        {feedback === 'incorrect' && (
          <p className="feedback warn">
            ✗ Not quite -- the right move was <strong>{correctMoveSan}</strong>
          </p>
        )}
        {error && <p className="feedback warn">Error: {error}</p>}
      </div>

      <div className="board-actions">
        {feedback !== null && <button onClick={loadNextTactic}>Next puzzle</button>}
      </div>
    </div>
  )
}

export default TacticsView