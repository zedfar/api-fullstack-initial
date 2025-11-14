from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.database import get_postgres_db
from app.models.user import User
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ============================================================================
# ACTIVE TOKENS CHECKING - Currently DISABLED (rely on JWT expiry only)
# ============================================================================
# Uncomment code below to enable in-memory active tokens tracking
# Note: This will require restart = tokens lost. For persistent storage, use database.
# active_tokens = set()
# ============================================================================


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_postgres_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # ============================================================================
    # ACTIVE TOKENS CHECKING - Currently DISABLED
    # ============================================================================
    # Uncomment lines below to check if token is in active_tokens set
    # if token not in active_tokens:
    #     raise credentials_exception
    # ============================================================================

    username = decode_access_token(token)
    if username is None:
        raise credentials_exception

    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
