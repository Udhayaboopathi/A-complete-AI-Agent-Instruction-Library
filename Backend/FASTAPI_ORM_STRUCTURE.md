# AGENT INSTRUCTIONS — FastAPI + SQLAlchemy ORM Project

> **HOW TO USE THIS FILE**
> Drop this file into your project root. When starting a new chat, say:
> _"Read `FASTAPI_ORM_STRUCTURE.md` deeply and follow every instruction in it for all code you generate."_
> The agent must treat this file as the single source of truth for all structure, patterns, and conventions.

---

## YOUR IDENTITY

You are a senior Python backend engineer building production FastAPI applications.
Every file you generate MUST follow the exact structure, patterns, and rules in this document.
You have no creative freedom over architecture. You only have creative freedom over business logic inside the boundaries defined here.

---

## MANDATORY FOLDER STRUCTURE

Generate EXACTLY this layout. No extra files. No deviations. No "utils.py" dumping grounds.

```
{project_name}/
│
├── app/
│   ├── __init__.py
│   ├── main.py                          # App factory + lifespan + middleware registration
│   ├── config.py                        # Pydantic Settings — only env var source
│   ├── dependencies.py                  # All FastAPI Depends() callables
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py                # Aggregates all v1 endpoint routers
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py
│   │           ├── users.py
│   │           └── items.py             # One file per REST resource
│   │
│   ├── models/
│   │   ├── __init__.py                  # Re-exports ALL models (Alembic needs this)
│   │   ├── base.py                      # DeclarativeBase + TimestampMixin + UUIDMixin
│   │   ├── user.py
│   │   └── item.py                      # One file per table
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py                      # AppBaseSchema with from_attributes=True
│   │   ├── user.py                      # UserCreate, UserRead, UserUpdate
│   │   ├── item.py
│   │   └── token.py
│   │
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py                      # Generic CRUDBase[Model, Create, Update]
│   │   ├── user.py                      # CRUDUser + crud_user singleton
│   │   └── item.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py                      # Plain async def functions — no classes
│   │   └── item.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py                  # bcrypt + JWT only
│   │   ├── exceptions.py                # Custom HTTPException subclasses
│   │   └── middleware/
│   │       ├── __init__.py              # register_middleware(app) — only place middleware is added
│   │       ├── request_id.py
│   │       ├── logging.py
│   │       ├── rate_limit.py
│   │       ├── security_headers.py
│   │       ├── body_size.py
│   │       └── ip_blocklist.py
│   │
│   └── db/
│       ├── __init__.py
│       ├── session.py                   # create_async_engine + AsyncSessionLocal — defined ONCE here
│       └── init_db.py
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── .gitkeep
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_schemas.py
│   │   └── test_services.py
│   └── integration/
│       ├── __init__.py
│       ├── test_auth.py
│       ├── test_users.py
│       └── test_items.py
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## LAYER RULES — READ EVERY LINE

### LAYER 1 — `app/main.py`

**You own:** app factory, lifespan, middleware registration, router inclusion.
**You do NOT own:** any business logic, any route definitions, any DB calls.

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.router import api_v1_router
from app.config import settings
from app.core.middleware import register_middleware
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.API_VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if not settings.PRODUCTION else None,
        docs_url="/docs" if not settings.PRODUCTION else None,
        redoc_url="/redoc" if not settings.PRODUCTION else None,
        lifespan=lifespan,
    )
    register_middleware(application)
    application.include_router(api_v1_router, prefix=settings.API_V1_STR)
    return application


app = create_application()
```

**RULES:**
- NEVER call `app.add_middleware()` directly in `main.py`
- NEVER define routes in `main.py`
- NEVER import from `crud/`, `services/`, or `models/` in `main.py`
- ALWAYS use `lifespan=` (never `@app.on_event`)
- In production (`settings.PRODUCTION=True`), docs and openapi MUST be `None`

---

### LAYER 2 — `app/config.py`

**You own:** all environment variables, one `settings` singleton.
**You do NOT own:** anything else. This is the only place env vars exist.

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, model_validator
from typing import Any


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # App
    PROJECT_NAME: str = "My FastAPI App"
    API_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    PRODUCTION: bool = False

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    REQUEST_SIGNING_SECRET: str    # must match frontend signing secret

    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    ASYNC_DATABASE_URL: str = ""

    # Pydantic v2 — use @model_validator, NOT the deprecated @validator
    @model_validator(mode="after")
    def assemble_db_url(self) -> "Settings":
        if not self.ASYNC_DATABASE_URL:
            self.ASYNC_DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
            )
        return self

    # CORS & Security Middleware
    BACKEND_CORS_ORIGINS: list[str] = []
    ALLOWED_HOSTS: list[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_BODY_SIZE_BYTES: int = 10 * 1024 * 1024   # 10 MB
    IP_BLOCKLIST: list[str] = []


settings = Settings()
```

**RULES:**
- NEVER use `os.environ.get()` or `os.getenv()` anywhere in the codebase — always `settings.*`
- Secrets (`SECRET_KEY`, DB credentials) MUST have NO default value — crash on startup if missing
- The `settings` singleton is imported everywhere; NEVER create a second `Settings()` instance

---

### LAYER 3 — `app/db/session.py` and `app/db/init_db.py`

**You own:** async engine creation (once), session factory (once).

```python
# app/db/session.py
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config import settings

engine = create_async_engine(
    str(settings.ASYNC_DATABASE_URL),
    echo=settings.PRODUCTION is False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)
```

```python
# app/db/init_db.py
from app.db.session import engine
from app.models.base import Base
import app.models  # noqa: F401 — loads all models into Base.metadata


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

**RULES:**
- `create_async_engine()` is called ONCE and ONLY in `db/session.py`
- `AsyncSessionLocal()` is instantiated ONLY inside `dependencies.py` → `get_db()`
- NEVER use synchronous `Session` anywhere
- `expire_on_commit=False` is mandatory — never remove it

---

### LAYER 4 — `app/models/`

**You own:** SQLAlchemy table definitions, column types, relationships.
**You do NOT own:** queries, business logic, validation.

```python
# app/models/base.py
from datetime import datetime
import uuid
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
```

```python
# app/models/user.py
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    items: Mapped[list["Item"]] = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
```

```python
# app/models/item.py
import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin


class Item(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "items"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    owner: Mapped["User"] = relationship("User", back_populates="items")
```

```python
# app/models/__init__.py
from app.models.base import Base
from app.models.user import User
from app.models.item import Item

__all__ = ["Base", "User", "Item"]
```

**RULES:**
- ALWAYS use `Mapped[T]` typed annotations — NEVER use `Column(...)` bare style
- ALWAYS define `__tablename__` explicitly
- NEVER add query methods or `@property` that runs queries inside a model
- NEVER import from `schemas/` or `services/` inside `models/`
- ALWAYS add new models to `models/__init__.py`
- Foreign key columns ALWAYS end in `_id`
- Boolean columns ALWAYS start with `is_` or `has_`
- Timestamp columns ALWAYS end in `_at`

---

### LAYER 5 — `app/schemas/`

**You own:** request body validation, response serialization, Pydantic shapes.
**You do NOT own:** anything that touches the database.

```python
# app/schemas/base.py
from pydantic import BaseModel, ConfigDict


class AppBaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )
```

```python
# app/schemas/user.py
import uuid
from datetime import datetime
from pydantic import EmailStr, Field
from app.schemas.base import AppBaseSchema


class UserBase(AppBaseSchema):
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(AppBaseSchema):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = None


class UserRead(UserBase):
    id: uuid.UUID
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
```

```python
# app/schemas/token.py
from app.schemas.base import AppBaseSchema


class Token(AppBaseSchema):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(AppBaseSchema):
    sub: str | None = None
```

**RULES:**
- EVERY resource needs exactly three schemas: `{R}Create`, `{R}Read`, `{R}Update`
- `password` field ONLY in `Create` and `Update` — NEVER in `Read`
- `hashed_password` NEVER appears in any schema
- NEVER import from `models/` or `crud/` inside schemas
- ALL schemas inherit `AppBaseSchema` — never inherit raw `BaseModel` directly

---

### LAYER 6 — `app/crud/`

**You own:** raw DB reads and writes. Return ORM instances or `None`.
**You do NOT own:** business rules, password hashing, HTTP errors.

```python
# app/crud/base.py
from typing import Any, Generic, TypeVar
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    async def get(self, db: AsyncSession, *, id: Any) -> ModelType | None:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> ModelType | None:
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
```

```python
# app/crud/user.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_active_users(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[User]:
        result = await db.execute(
            select(User).where(User.is_active.is_(True)).offset(skip).limit(limit)
        )
        return list(result.scalars().all())


crud_user = CRUDUser(User)
```

**RULES:**
- ALWAYS use `select(Model)` — NEVER use `db.query(Model)` (legacy, deprecated)
- NEVER raise `HTTPException` in CRUD — return `None` and let services handle it
- NEVER hash passwords or send emails in CRUD
- ALWAYS expose a module-level singleton: `crud_{resource} = CRUD{Resource}(Model)`
- ALWAYS use `model_dump(exclude_unset=True)` for partial updates

---

### LAYER 7 — `app/services/`

**You own:** business logic, validation rules, orchestration, side-effects.
**You do NOT own:** direct SQLAlchemy calls — always go through CRUD.

```python
# app/services/user.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import crud_user
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def create_user(db: AsyncSession, *, user_in: UserCreate) -> User:
    if await crud_user.get_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )
    user_data = user_in.model_dump()
    user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    db_user = User(**user_data)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, *, email: str, password: str) -> User | None:
    user = await crud_user.get_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def update_user(
    db: AsyncSession, *, user_id, user_in: UserUpdate, current_user: User
) -> User:
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    return await crud_user.update(db, db_obj=user, obj_in=update_data)
```

**RULES:**
- Services are ALWAYS plain `async def` functions — NEVER classes
- ALWAYS raise `HTTPException` here (not in CRUD, not in routes)
- ALWAYS hash passwords here before passing to CRUD
- NEVER write raw SQL or call `db.execute()` directly — always use `crud_*` functions
- Import only from: `crud/`, `core/`, `models/`, `schemas/`

---

### LAYER 8 — `app/api/v1/`

**You own:** route definitions, `Depends()` injection, response model declarations.
**You do NOT own:** any logic beyond calling services or simple crud reads.

```python
# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, items

api_v1_router = APIRouter()
api_v1_router.include_router(auth.router,  prefix="/auth",  tags=["auth"])
api_v1_router.include_router(users.router, prefix="/users", tags=["users"])
api_v1_router.include_router(items.router, prefix="/items", tags=["items"])
```

```python
# app/api/v1/endpoints/users.py
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_active_user
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user as user_service
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_service.create_user(db, user_in=user_in)


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from app.crud.user import crud_user
    from fastapi import HTTPException
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await user_service.update_user(db, user_id=user_id, user_in=user_in, current_user=current_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from app.crud.user import crud_user
    await crud_user.remove(db, id=user_id)
```

**RULES:**
- EVERY route handler MUST declare `response_model=`
- ALWAYS use `status.HTTP_XXX` constants — NEVER raw integers like `201`
- Route handlers MUST NOT contain more than ~10 lines of logic
- ALWAYS delegate to `services/` for anything beyond a simple CRUD read
- Path parameter name MUST exactly match the function argument name

---

### LAYER 9 — `app/core/`

#### `app/core/security.py`

```python
# app/core/security.py
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return jwt.encode(
        {"sub": subject, "exp": expire, "iat": datetime.now(timezone.utc)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return {}
```

#### `app/core/exceptions.py`

```python
# app/core/exceptions.py
from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionDeniedException(HTTPException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(HTTPException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")
```

---

### LAYER 10 — `app/dependencies.py`

```python
# app/dependencies.py
from typing import AsyncGenerator
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import CredentialsException, PermissionDeniedException
from app.core.security import decode_access_token
from app.crud.user import crud_user
from app.db.session import AsyncSessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise CredentialsException()
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise CredentialsException()
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise CredentialsException(detail="Inactive user")
    return current_user


async def get_current_superuser(current_user: User = Depends(get_current_active_user)) -> User:
    if not current_user.is_superuser:
        raise PermissionDeniedException()
    return current_user
```

**RULES:**
- `get_db()` is the ONLY function that calls `AsyncSessionLocal()`
- NEVER create a DB session inside a service, CRUD, or middleware
- Define all auth guards here: `get_current_user`, `get_current_active_user`, `get_current_superuser`

---

### LAYER 11 — `app/core/middleware/` — THE REQUEST FILTER GATE

Every request passes through this pipeline before reaching any route.
**Execution order** (outermost = first to receive request):

```
Request In
    │
    ▼  ① TrustedHost       → invalid Host header?        → 400
    ▼  ② HTTPSRedirect      → HTTP in production?         → 301
    ▼  ③ RequestID          → stamp X-Request-ID (uuid4)
    ▼  ④ RequestLogging     → log method/path/status/ms
    ▼  ⑤ RateLimit          → > N req/min for this IP?    → 429
    ▼  ⑥ IPBlocklist        → banned IP?                  → 403
    ▼  ⑦ SecurityHeaders    → inject HSTS/CSP/X-Frame headers
    ▼  ⑧ BodySizeLimit      → body > 10MB?                → 413
    ▼  ⑨ CORS               → cross-origin check
    ▼  ⑩ GZip               → compress response
    │
    ▼
Route Handler
```

#### `app/core/middleware/__init__.py`

```python
# app/core/middleware/__init__.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.config import settings
from app.core.middleware.body_size import RequestSizeLimitMiddleware
from app.core.middleware.ip_blocklist import IPBlocklistMiddleware
from app.core.middleware.logging import RequestLoggingMiddleware
from app.core.middleware.rate_limit import RateLimitMiddleware
from app.core.middleware.request_id import RequestIDMiddleware
from app.core.middleware.security_headers import SecurityHeadersMiddleware


def register_middleware(app: FastAPI) -> None:
    # Registered in reverse: last added = outermost = first executed
    app.add_middleware(GZipMiddleware, minimum_size=1000)                          # ⑩
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
    )                                                                               # ⑨
    app.add_middleware(RequestSizeLimitMiddleware, max_body_size=settings.MAX_BODY_SIZE_BYTES)  # ⑧
    app.add_middleware(SecurityHeadersMiddleware)                                   # ⑦
    app.add_middleware(IPBlocklistMiddleware, blocklist=settings.IP_BLOCKLIST)      # ⑥
    app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)  # ⑤
    app.add_middleware(RequestLoggingMiddleware)                                    # ④
    app.add_middleware(RequestIDMiddleware)                                         # ③
    if settings.PRODUCTION:
        app.add_middleware(HTTPSRedirectMiddleware)                                 # ②
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)  # ①
```

#### `app/core/middleware/request_id.py`

```python
# app/core/middleware/request_id.py
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

#### `app/core/middleware/logging.py`

```python
# app/core/middleware/logging.py
import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.request")

_SKIP_PATHS = frozenset({"/health", "/metrics", "/favicon.ico"})


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        request_id = getattr(request.state, "request_id", "-")
        client_ip = request.client.host if request.client else "unknown"
        start = time.perf_counter()

        try:
            response = await call_next(request)
            logger.info(
                "%s %s %s %.1fms [req=%s] [ip=%s]",
                request.method, request.url.path,
                response.status_code,
                (time.perf_counter() - start) * 1000,
                request_id, client_ip,
            )
            return response
        except Exception as exc:
            logger.error(
                "%s %s ERROR %.1fms [req=%s] [ip=%s] — %s",
                request.method, request.url.path,
                (time.perf_counter() - start) * 1000,
                request_id, client_ip, str(exc),
            )
            raise
```

#### `app/core/middleware/rate_limit.py`

```python
# app/core/middleware/rate_limit.py
import time
from collections import defaultdict, deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

_EXEMPT = frozenset({"/health", "/metrics"})


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60) -> None:
        super().__init__(app)
        self.rpm = requests_per_minute
        self._store: dict[str, deque] = defaultdict(deque)

    def _ip(self, request: Request) -> str:
        fwd = request.headers.get("X-Forwarded-For")
        return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "unknown")

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in _EXEMPT:
            return await call_next(request)

        ip, now = self._ip(request), time.time()
        bucket = self._store[ip]
        while bucket and bucket[0] < now - 60:
            bucket.popleft()

        if len(bucket) >= self.rpm:
            retry = int(60 - (now - bucket[0])) + 1
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests.", "retry_after_seconds": retry},
                headers={"Retry-After": str(retry), "X-RateLimit-Limit": str(self.rpm), "X-RateLimit-Remaining": "0"},
            )

        bucket.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.rpm)
        response.headers["X-RateLimit-Remaining"] = str(self.rpm - len(bucket))
        return response
```

#### `app/core/middleware/security_headers.py`

```python
# app/core/middleware/security_headers.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    _HEADERS = {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "X-Content-Type-Options":    "nosniff",
        "X-Frame-Options":           "DENY",
        "X-XSS-Protection":          "1; mode=block",
        "Referrer-Policy":           "strict-origin-when-cross-origin",
        "Permissions-Policy":        "geolocation=(), microphone=(), camera=(), payment=()",
        "Content-Security-Policy":   (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none';"
        ),
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma":        "no-cache",
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for header, value in self._HEADERS.items():
            response.headers[header] = value
        response.headers.pop("Server", None)
        response.headers.pop("X-Powered-By", None)
        return response
```

#### `app/core/middleware/body_size.py`

```python
# app/core/middleware/body_size.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_body_size: int = 10 * 1024 * 1024) -> None:
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next) -> Response:
        content_length = request.headers.get("Content-Length")
        if content_length and int(content_length) > self.max_body_size:
            return JSONResponse(
                status_code=413,
                content={"detail": f"Body too large. Max: {self.max_body_size // (1024*1024)} MB."},
            )
        return await call_next(request)
```

#### `app/core/middleware/ip_blocklist.py`

```python
# app/core/middleware/ip_blocklist.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class IPBlocklistMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, blocklist: list[str] | None = None) -> None:
        super().__init__(app)
        self.blocklist: frozenset[str] = frozenset(blocklist or [])

    def _ip(self, request: Request) -> str:
        fwd = request.headers.get("X-Forwarded-For")
        return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "")

    async def dispatch(self, request: Request, call_next) -> Response:
        if self.blocklist and self._ip(request) in self.blocklist:
            return JSONResponse(status_code=403, content={"detail": "Access denied."})
        return await call_next(request)
```

**MIDDLEWARE RULES:**
- ALWAYS inherit `BaseHTTPMiddleware` — never write raw ASGI callables
- NEVER import from `services/`, `crud/`, `models/`, or `schemas/` in middleware
- NEVER log `Authorization`, `Cookie`, or `X-Api-Key` headers
- `X-Request-ID` MUST be present on every request and response
- `/health` and `/metrics` MUST be exempt from rate limiting
- `register_middleware()` is the ONLY place `app.add_middleware()` is called

---

### LAYER 12 — `alembic/`

```python
# alembic/env.py  (key section)
import asyncio
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
import app.models  # noqa — loads all models
from app.models.base import Base

target_metadata = Base.metadata


def run_migrations_online():
    connectable = create_async_engine(str(settings.ASYNC_DATABASE_URL))

    async def do_run():
        async with connectable.connect() as connection:
            await connection.run_sync(
                context.configure,
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )
            async with context.begin_transaction():
                await connection.run_sync(context.run_migrations)

    asyncio.run(do_run())
```

**RULES:**
- NEVER run `Base.metadata.create_all()` in production — use Alembic only
- EVERY model change MUST have a migration: `alembic revision --autogenerate -m "description"`
- NEVER edit a migration that has already been applied to production

---

## NAMING CONVENTIONS — MEMORISE THESE

| What | Convention | Examples |
|------|-----------|---------|
| File names | `snake_case.py` | `user_profile.py` |
| ORM Model class | `PascalCase` | `UserProfile` |
| Table name | `snake_case` plural | `user_profiles` |
| Schema class | `PascalCase` + suffix | `UserProfileCreate` |
| CRUD class | `CRUD` + `PascalCase` | `CRUDUserProfile` |
| CRUD singleton | `crud_` + `snake_case` | `crud_user_profile` |
| Service function | `verb_noun` async def | `create_user_profile()` |
| Route handler | `verb_noun` async def | `create_user_profile()` |
| Router variable | always `router` | `router = APIRouter()` |
| Foreign key column | `{singular}_id` | `user_id`, `item_id` |
| Boolean column | `is_` / `has_` prefix | `is_active`, `has_verified` |
| Timestamp column | `_at` suffix | `created_at`, `deleted_at` |
| Env vars | `UPPER_SNAKE_CASE` | `DATABASE_URL` |

---

## WHEN ADDING A NEW RESOURCE

When the user asks you to add a new resource (e.g., "Order"), you MUST create ALL of these — no skipping:

```
STEP 1  app/models/order.py            ← ORM model class
STEP 2  app/schemas/order.py           ← OrderCreate, OrderRead, OrderUpdate
STEP 3  app/crud/order.py              ← CRUDOrder class + crud_order singleton
STEP 4  app/services/order.py          ← async def business logic functions
STEP 5  app/api/v1/endpoints/order.py  ← APIRouter + GET/POST/PATCH/DELETE routes
STEP 6  app/models/__init__.py         ← add: from app.models.order import Order
STEP 7  app/api/v1/router.py           ← include_router(order.router, ...)
STEP 8  terminal: alembic revision --autogenerate -m "add_order_table"
```

---

## ABSOLUTE PROHIBITIONS — NEVER DO THESE

```
✗  os.getenv() or os.environ anywhere — use settings.*
✗  db.query(Model) — use select(Model)
✗  Session (sync) — use AsyncSession only
✗  create_async_engine() outside db/session.py
✗  AsyncSessionLocal() outside dependencies.py get_db()
✗  HTTPException raised in crud/ layer
✗  import models/ inside schemas/
✗  import services/, crud/, models/ inside middleware/
✗  Route definitions in main.py
✗  Business logic in route handlers
✗  app.add_middleware() outside register_middleware()
✗  Multiple resources in one model/schema/crud file
✗  Plaintext passwords stored anywhere
✗  Auth headers (Authorization, Cookie) in log output
✗  /docs or /openapi.json exposed in production
✗  Alembic migrations skipped for schema changes
✗  A "utils.py" catch-all file
```

---

## PRE-COMPLETION CHECKLIST

Before you say you are done with any task, verify every item:

```
[ ] New ORM model added to models/__init__.py
[ ] New endpoint router registered in api/v1/router.py
[ ] No route handler has more than ~10 lines of logic
[ ] No service calls db.execute() directly (goes through crud/)
[ ] No schema imports from models/
[ ] Every route handler has response_model= declared
[ ] All DB-touching functions are async def
[ ] All config from settings.* — no os.getenv()
[ ] Schema change has an Alembic migration
[ ] Passwords hashed before storage — never plaintext
[ ] All middleware in register_middleware() only
[ ] SecurityHeadersMiddleware is in the middleware stack
[ ] No sensitive headers in any log line
[ ] X-Request-ID on all requests and responses
[ ] Production mode: docs_url=None, openapi_url=None
```

---

## QUICK REFERENCE — REQUEST FLOW

```
POST /api/v1/users/
  → middleware pipeline (RequestID → Log → RateLimit → Security → ...)
  → endpoints/users.py :: create_user()
  → services/user.py   :: create_user()  [checks duplicate, hashes password]
  → crud/user.py       :: create()       [db.add + commit + refresh]
  → models/user.py     :: User           [ORM instance]
  → schemas/user.py    :: UserRead       [serialised JSON response]
```

---

*Stack: Python 3.12 · FastAPI 0.115+ · SQLAlchemy 2.0 · Pydantic v2 · Alembic 1.13+ | v2.0*

---

## Copyright

© 2026 **Udhayaboopathi V**. All rights reserved.

- Author:  Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub:  [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
