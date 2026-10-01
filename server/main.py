"""Compliance AI API — FastAPI entrypoint."""

from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from app.api.v1.routes.users import users_router
from app.api.v1.routes.auth import auth_router
from app.api.v1.routes.organization import organization_router
from app.api.v1.routes.documents import docs_router
from app.api.v1.routes.system import system_router

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SERVER_ROOT = Path(__file__).resolve().parent
for _p in (_PROJECT_ROOT, _SERVER_ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.main import get_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # await init_db()
    yield


app = FastAPI(
    title="Support Assistant Agent",
    description="Support Assistant Agent API.",
    lifespan=lifespan,
)

_origins = [
    o.strip()
    for o in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(organization_router)
app.include_router(docs_router)
app.include_router(system_router)



@app.get("/health")
async def health():
    return {"status": "AI Support Agent is running..."}
