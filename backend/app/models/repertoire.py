from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Repertoire(Base):
    __tablename__ = "repertoires"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    color: Mapped[str] = mapped_column(String(5))  # "white" or "black"
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    nodes: Mapped[list["Node"]] = relationship(
        back_populates="repertoire", cascade="all, delete-orphan"
    )


class Node(Base):
    """
    A single position in a repertoire tree. The root node of a repertoire
    has parent_id = None and represents the starting position.
    """

    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    repertoire_id: Mapped[int] = mapped_column(ForeignKey("repertoires.id"))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("nodes.id"), nullable=True)

    fen: Mapped[str] = mapped_column(String(100))
    move_san: Mapped[str | None] = mapped_column(String(10), nullable=True)
    move_uci: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_main_line: Mapped[bool] = mapped_column(Boolean, default=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    depth: Mapped[int] = mapped_column(Integer, default=0)

    repertoire: Mapped["Repertoire"] = relationship(back_populates="nodes")
    children: Mapped[list["Node"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan"
    )
    parent: Mapped["Node | None"] = relationship(
        back_populates="children", remote_side=[id]
    )
