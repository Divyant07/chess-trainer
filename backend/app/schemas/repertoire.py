from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RepertoireCreate(BaseModel):
    name: str
    color: str  # "white" or "black"


class RepertoireOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    color: str
    created_at: datetime


class NodeCreate(BaseModel):
    parent_id: int | None = None
    move: str  # SAN or UCI, e.g. "Nf3" or "g1f3"
    comment: str | None = None


class NodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    repertoire_id: int
    parent_id: int | None
    fen: str
    move_san: str | None
    move_uci: str | None
    is_main_line: bool
    comment: str | None
    depth: int
