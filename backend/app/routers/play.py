from fastapi import APIRouter, HTTPException

from app.schemas.play import EngineMoveRequest, EngineMoveResponse
from app.services import engine as engine_service
from app.services.chess_logic import is_valid_fen

router = APIRouter(prefix="/play", tags=["play"])


@router.post("/engine-move", response_model=EngineMoveResponse)
def get_engine_move(payload: EngineMoveRequest):
    if not is_valid_fen(payload.fen):
        raise HTTPException(400, "Invalid FEN")

    try:
        return engine_service.best_move_at_strength(payload.fen, payload.elo)
    except FileNotFoundError as exc:
        raise HTTPException(503, str(exc)) from exc