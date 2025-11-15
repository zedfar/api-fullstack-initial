import ssl
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

Base = declarative_base()


# --- PostgreSQL ---
def get_async_sessionmaker():
    """
    Factory sessionmaker aman untuk serverless (Vercel).
    Engine dibuat fresh di event loop aktif.
    """
    ssl_context = ssl.create_default_context(cafile=None)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    engine = create_async_engine(
        settings.async_postgres_url,
        connect_args={"ssl": ssl_context},
        echo=False,
        future=True,
        pool_size=1,
        max_overflow=0,
        pool_recycle=1800,
        pool_timeout=10
    )
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_postgres_db():
    """
    Dependency untuk FastAPI.
    Membuka session baru di tiap request.
    """
    SessionLocal = get_async_sessionmaker()
    async with SessionLocal() as session:
        yield session


# --- MongoDB ---
# ✅ untuk dependency injection
async def get_mongodb():
    mongo_uri = getattr(settings, "MONGODB_URL", None)
    mongo_db = getattr(settings, "MONGODB_DB_NAME", None)

    if not mongo_uri or not mongo_db:
        print("⚠️ MongoDB credentials missing")
        yield None
        return

    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    try:
        yield db
    finally:
        client.close()
