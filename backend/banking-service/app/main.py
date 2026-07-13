from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from amenbank_shared.logging import setup_logging

from app.api.routes import router
from app.core.config import settings
from app.database.session import init_db, seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.service_name, settings.log_level)
    await init_db()
    await seed_demo_data()
    yield


app = FastAPI(title="Amen Bank Banking Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.service_name}
