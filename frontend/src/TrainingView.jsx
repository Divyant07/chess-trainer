import { useEffect, useState } from 'react'
import { Chessboard } from 'react-chessboard'
import { Chess } from 'chess.js'
import { api } from './api'

function TrainingView({ repertoireId }) {
  const [card, setCard] = useState(undefined) // undefined = loading, null = none due
  const [game, setGame] = useState(() => new Chess())
  const [fen, setFen] = useState('start')
  const [feedback, setFeedback] = useState(null) // null | 'correct' | 'incorrect'
  const [error, setError] = useState(null)

  async function loadNextCard() {
    setFeedback(null)
    setError(null)
    setCard(undefined)
    try {
      const next = await api.getNextCard(repertoireId)
      setCard(next)
      if (next) {
        const g = new Chess(next.position_fen)
        setGame(g)
        setFen(g.fen())
      }
    } catch (err) {
      setError(err.message)
      setCard(null)
    }
  }

  useEffect(() => {
    if (repertoireId != null) loadNextCard()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [repertoireId])

  async function onDrop(sourceSquare, targetSquare) {
    if (!card || feedback) return false // already answered, waiting for "Next"

    // Try the move on a throwaway copy so a wrong/illegal attempt doesn't
    // corrupt the board before we've recorded the answer.
    const attempt = new Chess(card.position_fen)
    const move = attempt.move({ from: sourceSquare, to: targetSquare, promotion: 'q' })
    if (move === null) return false // illegal move entirely, snap back

    const isCorrect = move.san === card.correct_move_san
    setGame(attempt)
    setFen(attempt.fen())
    setFeedback(isCorrect ? 'correct' : 'incorrect')

    try {
      await api.submitAnswer(card.node_id, isCorrect)
    } catch (err) {
      setError(err.message)
    }
    return true
  }

  function showAnswer() {
    if (!card) return
    const g = new Chess(card.resulting_fen)
    setGame(g)
    setFen(g.fen())
  }

  if (repertoireId == null) {
    return <p className="hint">Select a repertoire to start training.</p>
  }

  if (card === undefined) {
    return <p className="hint">Loading...</p>
  }

  if (card === null) {
    return (
      <div className="training-empty">
        <p>🎉 Nothing due for review right now.</p>
        <p className="hint">
          Come back later, or save more lines in Build mode to add cards to
          your queue.
        </p>
        <button onClick={loadNextCard}>Check again</button>
      </div>
    )
  }

  return (
    <div className="training-view">
      <p className="due-count">{card.due_count} card(s) due</p>

      <div className="board-wrapper">
        <Chessboard position={fen} onPieceDrop={onDrop} boardWidth={480} />
      </div>

      <div className="training-feedback">
        {feedback === null && <p className="hint">What's the move here?</p>}
        {feedback === 'correct' && <p className="feedback ok">✓ Correct!</p>}
        {feedback === 'incorrect' && (
          <p className="feedback warn">
            ✗ Not quite -- the right move was <strong>{card.correct_move_san}</strong>
          </p>
        )}
        {error && <p className="feedback warn">Error: {error}</p>}
      </div>

      <div className="board-actions">
        {feedback === null && (
          <button onClick={showAnswer}>Show answer</button>
        )}
        {feedback !== null && <button onClick={loadNextCard}>Next card</button>}
      </div>
    </div>
  )
}

export default TrainingView