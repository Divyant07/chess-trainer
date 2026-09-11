from fastapi import APIRouter, HTTPException

from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.services import engine as engine_service
from app.services.chess_logic import is_valid_fen

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("", response_model=AnalyzeResponse)
def analyze_position(payload: AnalyzeRequest):
    if not is_valid_fen(payload.fen):
        raise HTTPException(400, "Invalid FEN")

    try:
        return engine_service.analyze(payload.fen, depth=payload.depth)
    except FileNotFoundError as exc:
        # Stockfish not installed -- this is an optional feature, so we
        # surface a clear 503 rather than a raw stack trace.
        raise HTTPException(503, str(exc)) from exc
