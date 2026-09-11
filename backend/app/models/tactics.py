from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Tactic(Base):
    """
    Standalone puzzle position, independent of any repertoire.
    Not wired up to any router yet -- this is Phase 3 -- but defined now
    so the DB schema doesn't need a disruptive migration later.
    """

    __tablename__ = "tactics"

    id: Mapped[int] = mapped_column(primary_key=True)
    fen: Mapped[str] = mapped_column(String(100))
    solution_moves: Mapped[list] = mapped_column(JSON)  # list[str] of UCI moves
    motif_tags: Mapped[list] = mapped_column(JSON)  # list[str], e.g. ["fork", "pin"]
    source: Mapped[str] = mapped_column(String(20), default="manual")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
