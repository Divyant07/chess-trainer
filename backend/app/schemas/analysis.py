from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    fen: str
    depth: int = 15


class AnalyzeResponse(BaseModel):
    fen: str
    depth: int
    eval_cp: int | None
    mate_in: int | None
    best_move_uci: str | None
    best_move_san: str | None
