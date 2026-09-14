"""
Seeds a couple of hand-verified starter tactics so the Tactics tab has
something to train on immediately, without waiting on a bulk import.

For real volume, see the Lichess puzzle database (CC0 licensed, free):
https://database.lichess.org/#puzzles -- import_lichess_puzzles.py (once
you've added one) can bulk-load thousands of rated, verified puzzles from
that CSV.

Run from the backend/ directory with the venv active:
    python -m scripts.seed_tactics
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.tactics import Tactic, TacticStats

STARTER_TACTICS = [
    {
        "fen": "k7/8/1K6/8/8/8/7Q/8 w - - 0 1",
        "solution_moves": ["h2h8"],  # Qh8# -- classic KQ vs K corner mate
        "motif_tags": ["checkmate"],
        "notes": "Basic king + queen mate: the queen delivers mate on the "
        "back rank while your own king cuts off both escape squares.",
    },
    {
        "fen": "r3k3/8/8/1N6/8/8/8/4K3 w - - 0 1",
        "solution_moves": ["b5c7"],  # Nc7+ forks king (e8) and rook (a8)
        "motif_tags": ["fork"],
        "notes": "Knight fork: Nc7+ checks the king and attacks the rook "
        "on a8 at the same time.",
    },
]


def seed():
    db = SessionLocal()
    try:
        created = 0
        for data in STARTER_TACTICS:
            exists = (
                db.query(Tactic)
                .filter(Tactic.fen == data["fen"], Tactic.source == "seed")
                .first()
            )
            if exists:
                continue

            tactic = Tactic(
                fen=data["fen"],
                solution_moves=data["solution_moves"],
                motif_tags=data["motif_tags"],
                source="seed",
                notes=data["notes"],
            )
            db.add(tactic)
            db.commit()
            db.refresh(tactic)

            db.add(TacticStats(tactic_id=tactic.id))
            db.commit()
            created += 1

        print(f"Seeded {created} new tactic(s) (skipped duplicates).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()