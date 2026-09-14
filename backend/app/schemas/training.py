from datetime import datetime

from pydantic import BaseModel


class TrainingCardOut(BaseModel):
    """
    Everything the frontend needs to show one training card: the position
    to display (the parent's FEN, i.e. before the move), and enough of the
    correct answer to check the user's attempt and give feedback.
    """

    node_id: int
    position_fen: str  # board position to show -- BEFORE the move
    correct_move_san: str
    correct_move_uci: str
    resulting_fen: str  # position after the correct move -- for feedback display
    repetitions: int
    due_count: int  # how many cards (including this one) are currently due


class AnswerRequest(BaseModel):
    node_id: int
    correct: bool


class AnswerResponse(BaseModel):
    node_id: int
    ease_factor: float
    interval_days: float
    repetitions: int
    next_review_at: datetime
    last_result: str