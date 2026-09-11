"""
Thin wrapper around Stockfish via python-chess's UCI engine interface.

Requires the Stockfish binary to be installed separately from pip --
see backend/README.md for install instructions per OS. Point
STOCKFISH_PATH (in .env) at the binary.

If Stockfish isn't installed, analyze() raises FileNotFoundError with a
clear message rather than crashing the whole app -- routers should catch
this and return a friendly error, since analysis is an optional feature,
not a hard dependency for the repertoire/training features to work.
"""

import chess
import chess.engine

from app.core.config import settings


def analyze(fen: str, depth: int = 15) -> dict:
    board = chess.Board(fen)

    try:
        with chess.engine.SimpleEngine.popen_uci(settings.stockfish_path) as engine:
            info = engine.analyse(board, chess.engine.Limit(depth=depth))
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Stockfish binary not found at '{settings.stockfish_path}'. "
            "Install it and/or set STOCKFISH_PATH in your .env file."
        ) from exc

    score = info["score"].white()  # normalize to White's perspective
    best_move = info.get("pv", [None])[0]

    return {
        "fen": fen,
        "depth": depth,
        # cp = centipawns (positive favors White). None if it's a forced mate.
        "eval_cp": score.score(mate_score=100000),
        "mate_in": score.mate(),
        "best_move_uci": best_move.uci() if best_move else None,
        "best_move_san": board.san(best_move) if best_move else None,
    }
