from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TrainingStats(Base):
    """
    SM-2 style spaced repetition state, one row per trainable node.
    Kept separate from Node so the same table shape could later be reused
    for tactics (see models/tactics.py) without cramming SRS fields into
    every content model.
    """

    __tablename__ = "training_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    node_id: Mapped[int] = mapped_column(ForeignKey("nodes.id"))

    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval_days: Mapped[float] = mapped_column(Float, default=0.0)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    next_review_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    last_result: Mapped[str | None] = mapped_column(String(10), nullable=True)

    node: Mapped["Node"] = relationship()  # noqa: F821
