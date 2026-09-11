"""
All direct use of the `chess` library should live here. Routers and models
work with plain FEN / SAN / UCI strings; this module is the only place that
touches chess.Board() directly. Keeping it isolated makes it easy to test
and easy to swap out later if needed.
"""

import chess

STARTING_FEN = chess.STARTING_FEN


class IllegalMoveError(Exception):
    pass


def apply_move(fen: str, move_input: str) -> dict:
    """
    Apply a move to a position given as FEN.

    move_input can be SAN (e.g. "Nf3") or UCI (e.g. "g1f3") -- we try SAN
    first since that's what a human typically enters, and fall back to UCI.

    Returns a dict with the resulting fen, san, and uci -- everything a
    caller needs to persist a new Node without touching chess.Board itself.
    """
    board = chess.Board(fen)

    move = None
    try:
        move = board.parse_san(move_input)
    except ValueError:
        try:
            move = chess.Move.from_uci(move_input)
            if move not in board.legal_moves:
                move = None
        except ValueError:
            move = None

    if move is None or move not in board.legal_moves:
        raise IllegalMoveError(f"'{move_input}' is not a legal move in position {fen}")

    san = board.san(move)
    uci = move.uci()
    board.push(move)

    return {
        "fen": board.fen(),
        "san": san,
        "uci": uci,
        "is_checkmate": board.is_checkmate(),
        "is_check": board.is_check(),
    }


def legal_moves(fen: str) -> list[str]:
    """Return legal moves from a position in SAN, useful for UI hints."""
    board = chess.Board(fen)
    return [board.san(m) for m in board.legal_moves]


def is_valid_fen(fen: str) -> bool:
    try:
        chess.Board(fen)
        return True
    except ValueError:
        return False
