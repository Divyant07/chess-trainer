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


# Stockfish's UCI_Elo option only accepts values in this range (as of the
# NNUE-era versions bundled with most package managers). We clamp to it
# so an out-of-range request doesn't just get silently ignored by the engine.
MIN_ELO = 1320
MAX_ELO = 3190


def best_move_at_strength(fen: str, elo: int, think_time: float = 1.0) -> dict:
    """
    Ask Stockfish for a move, deliberately weakened to roughly the given
    Elo via UCI_LimitStrength + UCI_Elo. think_time is a wall-clock budget
    in seconds -- kept short so "Play vs Engine" stays responsive; the Elo
    limiting matters far more than search depth for making the engine feel
    beatable at lower ratings.
    """
    board = chess.Board(fen)
    clamped_elo = max(MIN_ELO, min(MAX_ELO, elo))

    try:
        with chess.engine.SimpleEngine.popen_uci(settings.stockfish_path) as engine:
            engine.configure({"UCI_LimitStrength": True, "UCI_Elo": clamped_elo})
            result = engine.play(board, chess.engine.Limit(time=think_time))
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Stockfish binary not found at '{settings.stockfish_path}'. "
            "Install it and/or set STOCKFISH_PATH in your .env file."
        ) from exc

    if result.move is None:
        # No legal move for the engine -- the game was already over
        # (checkmate/stalemate) before it was asked to move.
        return {"move_uci": None, "move_san": None, "is_game_over": True}

    san = board.san(result.move)
    board.push(result.move)

    return {
        "move_uci": result.move.uci(),
        "move_san": san,
        # Reflects the position AFTER the engine's move -- this is what
        # tells the frontend the engine just delivered checkmate/stalemate.
        "is_game_over": board.is_game_over(),
    }