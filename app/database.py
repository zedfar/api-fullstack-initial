import ssl
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

Base = declarative_base()

# --- Lazy globals (loop-safe) ---
_engine = None
_SessionLocal = None
_mongo_client = None
_mongo_db = None

# --- PostgreSQL ---
def get_async_sessionmaker():
    """Create async sessionmaker per loop."""
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_async_engine(
            settings.async_postgres_url,
            echo=False,
            pool_size=5,
            max_overflow=0,
            future=True
        )
        _SessionLocal = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _SessionLocal


async def get_postgres_db():
    """Dependency for FastAPI endpoints"""
    SessionLocal = get_async_sessionmaker()
    async with SessionLocal() as session:
        yield session


async def init_postgres():
    """Manual init (local only)"""
    SessionLocal = get_async_sessionmaker()
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ PostgreSQL tables created")

# --- MongoDB ---
async def get_mongodb():
    """Lazy Mongo connection (safe for serverless)"""
    global _mongo_client, _mongo_db
    if _mongo_client is None:
        mongo_uri = getattr(settings, "MONGODB_URI", None)
        mongo_db_name = getattr(settings, "MONGODB_DB", None)

        if not mongo_uri or not mongo_db_name:
            print("⚠️ MongoDB credentials missing")
            return None

        _mongo_client = AsyncIOMotorClient(mongo_uri)
        _mongo_db = _mongo_client[mongo_db_name]
        print(f"✅ MongoDB connected to '{mongo_db_name}'")

    return _mongo_db


async def close_mongodb():
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        print("🛑 MongoDB closed")
