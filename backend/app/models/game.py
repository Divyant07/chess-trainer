from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Game(Base):
    """
    An imported game (chess.com / lichess). Not wired up yet -- Phase 4 --
    but defined now alongside the rest of the schema.
    """

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    pgn: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(20))  # "chess.com" or "lichess"
    played_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    result: Mapped[str | None] = mapped_column(String(10), nullable=True)

    deviation_node_id: Mapped[int | None] = mapped_column(
        ForeignKey("nodes.id"), nullable=True
    )
    deviation_ply: Mapped[int | None] = mapped_column(Integer, nullable=True)
