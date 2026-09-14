from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.tactics import Tactic, TacticStats
from app.schemas.tactics import (
    TacticAnswerRequest,
    TacticAnswerResponse,
    TacticCardOut,
    TacticCreate,
    TacticOut,
)
from app.services.chess_logic import IllegalMoveError, apply_move, uci_to_san
from app.services.spaced_repetition import review

router = APIRouter(prefix="/tactics", tags=["tactics"])


@router.post("", response_model=TacticOut)
def create_tactic(payload: TacticCreate, db: Session = Depends(get_db)):
    # Normalize the solution move (which may arrive as SAN or UCI) to UCI
    # for storage, the same way apply_move is used for repertoire nodes.
    try:
        result = apply_move(payload.fen, payload.solution_move)
    except IllegalMoveError as exc:
        raise HTTPException(400, str(exc)) from exc

    tactic = Tactic(
        fen=payload.fen,
        solution_moves=[result["uci"]],
        motif_tags=payload.motif_tags,
        source="manual",
        notes=payload.notes,
    )
    db.add(tactic)
    db.commit()
    db.refresh(tactic)

    # Immediately trainable, same pattern as repertoire nodes.
    stats = TacticStats(tactic_id=tactic.id)
    db.add(stats)
    db.commit()

    return tactic


@router.get("/next-card", response_model=TacticCardOut | None)
def next_card(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    due_query = (
        db.query(Tactic, TacticStats)
        .join(TacticStats, TacticStats.tactic_id == Tactic.id)
        .filter(TacticStats.next_review_at <= now)
    )

    due_count = due_query.count()
    if due_count == 0:
        return None

    tactic, _stats = due_query.order_by(TacticStats.next_review_at.asc()).first()

    return TacticCardOut(
        tactic_id=tactic.id,
        fen=tactic.fen,
        motif_tags=tactic.motif_tags,
        due_count=due_count,
    )


@router.post("/answer", response_model=TacticAnswerResponse)
def submit_answer(payload: TacticAnswerRequest, db: Session = Depends(get_db)):
    tactic = db.get(Tactic, payload.tactic_id)
    if not tactic:
        raise HTTPException(404, "Tactic not found")

    stats = db.query(TacticStats).filter(TacticStats.tactic_id == tactic.id).first()
    if not stats:
        raise HTTPException(404, "No training stats found for this tactic")

    correct_uci = tactic.solution_moves[0]
    correct_san = uci_to_san(tactic.fen, correct_uci)

    # An illegal or nonsensical move attempt just counts as incorrect
    # rather than erroring out -- the user gets it wrong, same as playing
    # a legal-but-wrong move.
    try:
        attempt = apply_move(tactic.fen, payload.move)
        is_correct = attempt["uci"] == correct_uci
    except IllegalMoveError:
        is_correct = False

    result = review(
        ease_factor=stats.ease_factor,
        interval_days=stats.interval_days,
        repetitions=stats.repetitions,
        correct=is_correct,
    )
    stats.ease_factor = result["ease_factor"]
    stats.interval_days = result["interval_days"]
    stats.repetitions = result["repetitions"]
    stats.next_review_at = result["next_review_at"]
    stats.last_result = result["last_result"]
    db.commit()
    db.refresh(stats)

    return TacticAnswerResponse(
        correct=is_correct,
        correct_move_san=correct_san,
        ease_factor=stats.ease_factor,
        interval_days=stats.interval_days,
        repetitions=stats.repetitions,
        next_review_at=stats.next_review_at,
    )