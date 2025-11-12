import ssl
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

# --- PostgreSQL (SQLAlchemy + asyncpg) ---
Base = declarative_base()

# SSL context untuk Neon / Supabase
ssl_context = ssl.create_default_context(cafile=None)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Lazy initialization (biar ga bentrok event loop di Vercel)
_engine = None
_SessionLocal = None


def get_async_sessionmaker():
    """
    Membuat SQLAlchemy engine dan sessionmaker secara lazy.
    Dipanggil hanya saat ada request pertama kali.
    """
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_async_engine(
            settings.async_postgres_url,
            connect_args={"ssl": ssl_context},
            echo=False,
            future=True,
        )
        _SessionLocal = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _SessionLocal


async def get_postgres_db():
    """
    Dependency untuk FastAPI endpoint.
    Membuka dan menutup session per-request.
    """
    SessionLocal = get_async_sessionmaker()
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# --- MongoDB (Motor) ---
mongodb_client: AsyncIOMotorClient | None = None
mongodb = None


async def connect_mongodb():
    """Connect to MongoDB asynchronously"""
    global mongodb_client, mongodb
    mongo_uri = getattr(settings, "MONGODB_URL", None)
    mongo_db = getattr(settings, "MONGODB_DB_NAME", None)

    if mongo_uri and mongo_db:
        mongodb_client = AsyncIOMotorClient(mongo_uri)
        mongodb = mongodb_client[mongo_db]
        print(f"✅ MongoDB connected to '{mongo_db}'")
    else:
        print("⚠️ MongoDB credentials not found in .env — skipping Mongo connection.")


async def close_mongodb():
    """Close MongoDB connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("🛑 MongoDB connection closed.")


def get_mongodb():
    """
    Getter sederhana untuk akses database MongoDB.
    Return None kalau Mongo belum dikonfigurasi atau belum connect.
    """
    global mongodb
    if mongodb is None:
        print("⚠️ MongoDB belum terkoneksi.")
    return mongodb


# --- Utility (optional untuk seed_data.py dsb) ---
async def init_postgres():
    """
    Initialize PostgreSQL tables (manual run).
    Gunakan saat local dev / seeding.
    """
    SessionLocal = get_async_sessionmaker()
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ PostgreSQL tables created")
