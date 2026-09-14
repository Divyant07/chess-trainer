from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.repertoire import Node
from app.models.training import TrainingStats
from app.schemas.training import AnswerRequest, AnswerResponse, TrainingCardOut
from app.services.spaced_repetition import review

router = APIRouter(prefix="/training", tags=["training"])


@router.get("/next-card", response_model=TrainingCardOut | None)
def next_card(repertoire_id: int = Query(...), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    due_query = (
        db.query(Node, TrainingStats)
        .join(TrainingStats, TrainingStats.node_id == Node.id)
        .filter(Node.repertoire_id == repertoire_id)
        .filter(TrainingStats.next_review_at <= now)
    )

    due_count = due_query.count()
    if due_count == 0:
        return None

    node, stats = due_query.order_by(TrainingStats.next_review_at.asc()).first()

    parent = db.get(Node, node.parent_id)
    if not parent:
        # Shouldn't happen -- every non-root node has a parent -- but
        # guard against a corrupted tree rather than 500ing unhelpfully.
        raise HTTPException(500, f"Node {node.id} has no parent")

    return TrainingCardOut(
        node_id=node.id,
        position_fen=parent.fen,
        correct_move_san=node.move_san,
        correct_move_uci=node.move_uci,
        resulting_fen=node.fen,
        repetitions=stats.repetitions,
        due_count=due_count,
    )


@router.post("/answer", response_model=AnswerResponse)
def submit_answer(payload: AnswerRequest, db: Session = Depends(get_db)):
    stats = db.query(TrainingStats).filter(TrainingStats.node_id == payload.node_id).first()
    if not stats:
        raise HTTPException(404, "No training stats found for this node")

    result = review(
        ease_factor=stats.ease_factor,
        interval_days=stats.interval_days,
        repetitions=stats.repetitions,
        correct=payload.correct,
    )

    stats.ease_factor = result["ease_factor"]
    stats.interval_days = result["interval_days"]
    stats.repetitions = result["repetitions"]
    stats.next_review_at = result["next_review_at"]
    stats.last_result = result["last_result"]
    db.commit()
    db.refresh(stats)

    return AnswerResponse(
        node_id=stats.node_id,
        ease_factor=stats.ease_factor,
        interval_days=stats.interval_days,
        repetitions=stats.repetitions,
        next_review_at=stats.next_review_at,
        last_result=stats.last_result,
    )