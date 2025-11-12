# app/main.py
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.config import settings
from app.database import get_mongodb, close_mongodb, get_async_sessionmaker, Base
from app.seed_data import seed_roles
from app.routers import auth, categories, products, users, books, roles


@asynccontextmanager
async def lifespan(app: FastAPI):
    # PostgreSQL: buat tabel
    SessionLocal = get_async_sessionmaker()
    async with SessionLocal().bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # MongoDB connect (lazy)
    await get_mongodb()

    # Seed
    await seed_roles()

    yield

    # Tutup MongoDB (optional)
    await close_mongodb()


# --- FastAPI App ---
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Global Error Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error": str(exc)},
    )


# --- Health Endpoints ---
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
app.include_router(books.router, prefix=settings.API_V1_PREFIX)
app.include_router(roles.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)


# --- Local Dev ---
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
