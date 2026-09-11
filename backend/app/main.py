from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import analysis, repertoires

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


@app.get("/health")
def health_check():
    return {"status": "ok"}
