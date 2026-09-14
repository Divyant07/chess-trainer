from pydantic import BaseModel


class EngineMoveRequest(BaseModel):
    fen: str
    elo: int = 1200  # clamped server-side to Stockfish's supported range


class EngineMoveResponse(BaseModel):
    move_uci: str | None
    move_san: str | None
    is_game_over: bool