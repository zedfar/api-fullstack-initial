from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import timedelta
from app.database import get_postgres_db
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserLoginMetadata
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.config import settings
# from app.dependencies import active_tokens  # DISABLED: uncomment to enable active_tokens checking
from app.dependencies import get_current_active_user, oauth2_scheme
from app.models.role import Role

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me", response_model=UserLoginMetadata)
async def get_current_user(
    current_user=Depends(get_current_active_user)
):
    """
    Return current user info based on active Bearer token
    """
    # current_user sudah di-decode di get_current_active_user
    return current_user


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_postgres_db)
):
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(
            (User.email == user_data.email) | (
                User.username == user_data.username)
        )
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    hashed_password = get_password_hash(user_data.password)
    print(hashed_password)

    # 🧩 Ambil role default "user" kalau role_id tidak dikirim
    role_id = getattr(user_data, "role_id", None)
    if not role_id:
        result = await db.execute(select(Role).where(Role.name == "user"))
        role_user = result.scalar_one_or_none()
        if not role_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default role 'user' not found in database"
            )
        role_id = role_user.id

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role_id=role_id
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == new_user.id)
    )

    user_with_role = result.scalar_one()

    # ============================================================================
    # Generate access token for newly registered user (auto-login after register)
    # ============================================================================
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_with_role.username}, expires_delta=access_token_expires
    )

    # ============================================================================
    # ACTIVE TOKENS TRACKING - Currently DISABLED
    # ============================================================================
    # Uncomment line below to add token to active_tokens set
    # active_tokens.add(access_token)
    # ============================================================================

    # Build metadata for user
    user_metadata = UserLoginMetadata.from_orm(user_with_role)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "metadata": user_metadata
    }


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_postgres_db)
):
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    user_response = UserLoginMetadata.from_orm(user)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # ============================================================================
    # ACTIVE TOKENS TRACKING - Currently DISABLED
    # ============================================================================
    # Uncomment line below to add token to active_tokens set
    # active_tokens.add(access_token)
    # ============================================================================

    return {
        "access_token": access_token, "token_type": "bearer", "metadata": user_response
        # {
        #     "email": user.email,
        #     "username": user.username,
        #     "full_name": user.full_name,
        #     "role": role_obj,
        #     "is_active": user.is_active

        # }
    }


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    # ============================================================================
    # ACTIVE TOKENS TRACKING - Currently DISABLED
    # ============================================================================
    # Uncomment lines below to remove token from active_tokens set
    # if token in active_tokens:
    #     active_tokens.remove(token)
    # ============================================================================

    # Note: With active_tokens disabled, logout doesn't invalidate the token.
    # Token will remain valid until JWT expiry (4 hours).
    # For true logout, implement token blacklist or use database storage.

    return {"message": "Successfully logged out (token still valid until expiry)"}
