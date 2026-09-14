import asyncio
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import analysis, play, repertoires, tactics, training

# On Windows, python-chess's engine module (used for Stockfish analysis
# and Play vs Engine) launches Stockfish as a subprocess via asyncio.
# Windows has two asyncio event loop implementations, and only
# ProactorEventLoop supports subprocesses -- uvicorn doesn't select that
# one by default, which causes a NotImplementedError as soon as any
# engine endpoint is hit. Forcing the policy here, before anything else
# runs, fixes it without needing changes anywhere else.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Dev-only convenience: creates tables from models if they don't exist yet.
# Once you start using Alembic migrations for real schema changes, you can
# remove this and rely on `alembic upgrade head` instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chess Trainer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repertoires.router)
app.include_router(analysis.router)
app.include_router(training.router)
app.include_router(play.router)
app.include_router(tactics.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}