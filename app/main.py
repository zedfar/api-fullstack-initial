from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.config import settings
from app.database import get_async_sessionmaker, get_mongodb, Base
from app.seed_data import seed_roles
# from app.models import Base
from app.routers import auth, categories, products, users, books, roles


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- PostgreSQL init ---
    SessionLocal = get_async_sessionmaker()
    async with SessionLocal().bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_roles()

    # --- MongoDB init (optional) ---
    # async for _ in get_mongodb():
    #     break

    yield

    # (tidak perlu explicit close karena Vercel ephemeral)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error": str(exc)},
    )


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to FastAPI Management API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
    }


# --- Routers ---
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(products.router, prefix=settings.API_V1_PREFIX)
# app.include_router(books.router, prefix=settings.API_V1_PREFIX)
app.include_router(roles.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)
