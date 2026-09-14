from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TacticCreate(BaseModel):
    fen: str
    solution_move: str  # SAN or UCI -- normalized to UCI server-side
    motif_tags: list[str] = []
    notes: str | None = None


class TacticOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fen: str
    solution_moves: list[str]
    motif_tags: list[str]
    source: str
    notes: str | None


class TacticCardOut(BaseModel):
    tactic_id: int
    fen: str
    motif_tags: list[str]
    due_count: int


class TacticAnswerRequest(BaseModel):
    tactic_id: int
    move: str  # SAN or UCI, whatever the user's board move produced


class TacticAnswerResponse(BaseModel):
    correct: bool
    correct_move_san: str
    ease_factor: float
    interval_days: float
    repetitions: int
    next_review_at: datetime