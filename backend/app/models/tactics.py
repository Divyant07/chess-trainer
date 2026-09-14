from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Tactic(Base):
    """
    Standalone puzzle position, independent of any repertoire.
    solution_moves is stored as a list of UCI strings; v1 only checks the
    first move (i.e. "find the best move" style puzzles, not multi-move
    forced sequences).
    """

    __tablename__ = "tactics"

    id: Mapped[int] = mapped_column(primary_key=True)
    fen: Mapped[str] = mapped_column(String(100))
    solution_moves: Mapped[list] = mapped_column(JSON)  # list[str] of UCI moves
    motif_tags: Mapped[list] = mapped_column(JSON)  # list[str], e.g. ["fork", "pin"]
    source: Mapped[str] = mapped_column(String(20), default="manual")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class TacticStats(Base):
    """
    SM-2 style spaced repetition state for a tactic, mirroring
    models/training.py's TrainingStats but keyed on tactic_id instead of
    node_id. Kept as a separate table rather than a generalized polymorphic
    one -- simpler to reason about and query, at the cost of a little
    duplication between the two.
    """

    __tablename__ = "tactic_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    tactic_id: Mapped[int] = mapped_column(ForeignKey("tactics.id"))

    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval_days: Mapped[float] = mapped_column(Float, default=0.0)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    next_review_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    last_result: Mapped[str | None] = mapped_column(String(10), nullable=True)