from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.routes import ping
from app.core.config import settings
from app.core.logger import logger
from app.db.session import engine
from app.storage.s3 import get_s3_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful!")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")

    # Startup: Initialize S3 storage
    try:
        s3_storage = await get_s3_client()
        await s3_storage.ensure_bucket_exists()
        logger.info("✅ S3 storage initialized successfully!")
    except Exception as e:
        logger.error(f"❌ S3 storage initialization failed: {e}")

    logger.info(f"🚀 {settings.APP_NAME} started!")
    yield

    # Shutdown: Close database connections
    await engine.dispose()
    logger.info("🔌 Database connections closed")


# -------------------------------
# 3. FastAPI aplication
# -------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ping.router)
