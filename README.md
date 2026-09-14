# Chess Trainer

A personal opening repertoire trainer + tactics trainer, built as a learning
project. See project plan below for phases.

## Phase 0 (this scaffold)

- FastAPI backend with SQLite, SQLAlchemy models for the full planned schema
  (Repertoire, Node, TrainingStats, Tactic, Game), and Alembic ready to go
- A `/health` endpoint and a `/analysis` endpoint (Stockfish eval, optional)
- A `/repertoires` CRUD API already wired up (a bit ahead of Phase 0, but it
  was cheap to include since the models needed to exist anyway)
- React (Vite) frontend with an interactive chessboard and a live check
  that it can reach the backend

## Getting started

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000/docs for interactive API docs (FastAPI's
auto-generated Swagger UI -- very useful while building).

### Installing Stockfish (optional, for the /analysis endpoint)

Stockfish is free and open-source (GPL license) but is a separate binary
from the `python-chess` pip package -- you need to install it yourself:

- **macOS:** `brew install stockfish`
- **Ubuntu/Debian:** `sudo apt install stockfish`
- **Windows:** download from https://stockfishchess.org/download/ and note
  the path to the .exe

Then update `STOCKFISH_PATH` in your `.env` to match wherever it landed.
Run `which stockfish` (macOS/Linux) to find it after installing via a
package manager.

The rest of the app works fine without Stockfish installed -- only the
`/analysis` endpoint needs it, and it fails with a clear error message if
the binary isn't found rather than crashing anything else.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173. The Vite dev server proxies `/api/*` requests
to the backend on port 8000 (see `vite.config.js`), so make sure the
backend is running too.

## Project structure

```
chess-trainer/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + router registration
│   │   ├── core/               # config, DB session setup
│   │   ├── models/             # SQLAlchemy models (full schema, all phases)
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── routers/            # API endpoints
│   │   └── services/            # chess_logic.py (python-chess wrapper),
│   │                             engine.py (Stockfish wrapper)
│   ├── alembic/                 # DB migrations
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.jsx              # chessboard + backend connectivity check
        └── main.jsx
```

## Roadmap

- **Phase 1** -- Repertoire builder: click-to-move UI that saves lines via
  the already-built `/repertoires` API (done)
- **Phase 2** -- Spaced repetition trainer (SM-2) for quizzing your saved
  lines (done), plus:
  - **Play vs Engine** -- full games against Stockfish at adjustable
    strength (Elo presets), with undo
  - **Tactics** -- puzzle trainer using the same SM-2 scheduling as the
    repertoire trainer
- **Phase 3** -- Import games from chess.com/lichess, detect where you
  deviated from your repertoire, flag it against Stockfish eval
- **Phase 4** -- Dashboard: win rate by opening, common deviation points,
  weakest tactical patterns

## Getting more tactics puzzles

Two starter puzzles are included so the Tactics tab isn't empty on day
one -- both hand-verified (a king+queen corner mate and a knight fork).
Seed them by running, from `backend/` with your venv active:

```bash
python -m scripts.seed_tactics
```

For real volume, Lichess publishes their entire puzzle database for free
under a CC0 (public domain) license:
https://database.lichess.org/#puzzles

It's a large CSV (`.csv.zst` compressed) with millions of rated,
human-verified puzzles tagged by theme (fork, pin, back rank, etc).
Decompress it (7-Zip on Windows handles `.zst`, or `pip install
zstandard` and decompress in a couple lines of Python), then you can
write a small import script that reads the CSV and calls `POST /tactics`
for each row you want -- filter by rating range or theme so you don't
import all several million at once.