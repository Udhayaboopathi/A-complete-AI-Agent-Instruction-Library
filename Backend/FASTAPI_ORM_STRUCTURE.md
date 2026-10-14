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

This is a **modular monolith**. Features live in `app/modules/{feature}/`. Shared infrastructure lives in `core/`, `middleware/`, `common/`, and `integrations/`. You do NOT invent a layered `models/` + `crud/` + `services/` tree.

---

## THE ORM USES THE DATABASE — IT DOES NOT CREATE OR MODIFY IT

The `database/` project is the only place schema is created or changed.
This backend **uses** the already-deployed PostgreSQL. It never owns DDL.

```
database/schema/     +  db_deploy.py   →  CREATE / ALTER / DROP  (schema)
backend ORM          +  repositories   →  SELECT / INSERT / UPDATE / DELETE  (rows only)
```

**The ORM MUST NOT:**

- create tables, columns, indexes, views, functions, triggers, RLS, or roles
- alter types, rename columns, or drop objects
- call `Base.metadata.create_all()` or `drop_all()`
- run Alembic, `alembic revision`, `alembic upgrade`, or any migration tool
- execute `CREATE`, `ALTER`, `DROP`, `TRUNCATE` … `CASCADE`, or `CREATE EXTENSION`

**The ORM MAY:**

- map existing tables with `Mapped[]` / `__tablename__` / schema name
- read and write **rows** through repositories (`select`, `add`, `flush`, `delete`)

If a model does not match the live table: **stop**. Do not “fix” it with a migration. Tell the user to change `database/schema/` and run `db_deploy.py` first. Then map the new shape here.

Models are a **read of the live schema**, not a source of schema.

---

## TECH STACK — USE EXACTLY THESE

```
Framework       : FastAPI 0.143+
Language        : Python 3.15
ORM             : SQLAlchemy 2.0 async (Mapped[] / mapped_column) — maps existing tables only
Database        : PostgreSQL 18 + asyncpg  (schema owned by database/ — not this app)
Migrations      : NONE in this backend. Schema deploy is database/scripts/db_deploy.py
Validation      : Pydantic v2
Settings        : pydantic-settings
Auth            : PyJWT[crypto] + pwdlib[argon2]
Tasks           : Celery 5 + Redis
Package manager : uv  (pyproject.toml + uv.lock)
Testing         : pytest + pytest-asyncio + httpx
Server          : uvicorn
```

Before scaffolding, verify this baseline against official release/support pages, select the latest stable security patch in each compatible line, and commit `uv.lock`. Never use pre-release packages unless explicitly requested.

---

## MANDATORY FOLDER STRUCTURE

Generate EXACTLY this layout. No `app/models/`, no `app/crud/`, no `app/services/`, no `app/api/v1/endpoints/`. No catch-all `utils.py`.

```
backend/
│
├── main.py                              # FastAPI entry point — factory + lifespan only
│
├── app/
│   │
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                    # Load environment/settings — only env var source
│   │   ├── database.py                  # Engine + session + DeclarativeBase + mixins
│   │   ├── dependencies.py              # FastAPI Depends() callables
│   │   ├── security.py                  # JWT / password hashing
│   │   ├── exceptions.py                # Application exceptions + handlers
│   │   ├── logging.py                   # Logging configuration
│   │   └── constants.py                 # Global constants
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py                    # Root router — /health + version mounts
│   │   │
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── router.py                # Aggregates every module router
│   │
│   ├── modules/
│   │   ├── __init__.py                  # Re-exports ALL module models (maps live tables only)
│   │   │
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── users/
│   │   │   ├── __init__.py
│   │   │   ├── models.py                # Required when the module owns tables
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── organizations/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── email/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── billing/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── exceptions.py
│   │   │
│   │   └── payments/
│   │       ├── __init__.py
│   │       ├── models.py
│   │       ├── router.py
│   │       ├── schemas.py
│   │       ├── service.py
│   │       ├── repository.py
│   │       └── exceptions.py
│   │
│   ├── integrations/
│   │   ├── __init__.py
│   │   │
│   │   ├── payments/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── stripe.py
│   │   │   └── razorpay.py
│   │   │
│   │   ├── email/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── provider.py
│   │   │
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   └── provider.py
│   │   │
│   │   └── sms/
│   │       ├── __init__.py
│   │       └── provider.py
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   ├── email_tasks.py
│   │   ├── billing_tasks.py
│   │   └── notification_tasks.py
│   │
│   ├── middleware/
│   │   ├── __init__.py                  # register_middleware(app) — only place middleware is added
│   │   ├── request_id.py
│   │   ├── logging.py
│   │   ├── security_headers.py
│   │   ├── body_size.py
│   │   └── ip_blocklist.py
│   │
│   ├── common/
│   │   ├── __init__.py
│   │   ├── enums.py
│   │   ├── types.py
│   │   ├── pagination.py
│   │   ├── responses.py
│   │   └── repository.py                # Generic RepositoryBase
│   │
│   └── utils/
│       ├── __init__.py
│       ├── dates.py
│       ├── strings.py
│       └── identifiers.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   │
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   ├── users/
│   │   ├── billing/
│   │   └── payments/
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── repositories/
│   │   └── integrations/
│   │
│   └── api/
│       ├── __init__.py
│       ├── auth/
│       ├── users/
│       ├── billing/
│       └── payments/
│
├── scripts/
│   ├── __init__.py
│   ├── health_check.py
│   └── seed.py
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── development.md
│   └── deployment.md
│
├── .github/
│   ├── workflows/
│   │   ├── test.yml
│   │   ├── lint.yml
│   │   ├── build.yml
│   │   └── deploy.yml
│   │
│   └── pull_request_template.md
│
├── .env                                 # Local environment — NEVER commit
├── .env.production                      # Production environment — NEVER commit
├── .env.example                         # Safe template — commit this
│
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
│
├── pyproject.toml
├── uv.lock
├── Makefile
├── README.md
├── CHANGELOG.md
└── LICENSE
```

**Module file rules:**

- Every module that owns a database table MUST have `models.py`.
- A module with no tables (example: `auth` using the `users` table) MAY omit `models.py`.
- Every module MUST have `__init__.py`.
- Do not add extra files inside a module (`helpers.py`, `utils.py`, `helpers/`). Put shared helpers in `app/utils/` or `app/common/`.

---

## ARCHITECTURAL LAYERS

```
main.py                         → App factory, lifespan, router include. No business logic.
app/core/                       → Settings, DB session, security, deps, exceptions, logging.
app/middleware/                 → Request pipeline. No DB. No services.
app/api/                        → Router aggregation only. No handlers with logic.
app/modules/{feature}/models.py → Map existing tables only. No DDL. No queries. No validation.
app/modules/{feature}/schemas.py→ Pydantic request/response. No DB.
app/modules/{feature}/repository.py → Raw DB reads/writes. Return ORM or None.
app/modules/{feature}/service.py    → Business rules, hashing, orchestration, side-effects.
app/modules/{feature}/router.py     → HTTP only. Depends() + call service.
app/modules/{feature}/exceptions.py → Domain exceptions. Raised by service only.
app/integrations/               → Third-party SDKs. Called by services and tasks only.
app/tasks/                      → Celery jobs. Call services or integrations. Never routers.
app/common/                     → Shared pagination, enums, types, RepositoryBase.
app/utils/                      → Pure helpers. No I/O. No settings. No DB.
```

**Request flow:**

```
POST /api/v1/users/
  → middleware pipeline
  → api/v1/router.py            (mount)
  → modules/users/router.py     create_user()
  → modules/users/service.py    create_user()   [duplicate check, hash password]
  → modules/users/repository.py create()        [db.add + flush]
  → modules/users/models.py     User
  → modules/users/schemas.py    UserRead
```

**Cross-module rule:** a module may import another module's `service`, `repository`, `schemas`, `models`, or `exceptions`. A module must NEVER import another module's `router`. Routers never import integrations. Integrations never import modules.

---

### LAYER 1 — `main.py`

**You own:** app factory, lifespan, middleware registration, exception handlers, router inclusion.
**You do NOT own:** any business logic, any route definitions, any DB calls.

```python
# main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.middleware import register_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
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
    register_exception_handlers(application)
    application.include_router(api_router)
    return application


app = create_application()
```

**RULES:**

- NEVER call `app.add_middleware()` directly in `main.py`
- NEVER define routes in `main.py`
- NEVER import from `modules/`, `integrations/`, or `tasks/` in `main.py`
- ALWAYS use `lifespan=` (never `@app.on_event`)
- In production (`settings.PRODUCTION=True`), docs and openapi MUST be `None`

---

### LAYER 2 — `app/core/config.py`

**You own:** all environment variables, one `settings` singleton.
**You do NOT own:** anything else. This is the only place env vars exist.

```python
# app/core/config.py
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    ALGORITHM: str = "HS256"  # prefer an asymmetric algorithm + KMS/JWKS across services
    JWT_ISSUER: str
    JWT_AUDIENCE: str

    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    ASYNC_DATABASE_URL: str = ""

    # Redis / Celery
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""

    # Payments
    PAYMENT_PROVIDER: str = "stripe"  # stripe | razorpay
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""

    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""

    # CORS & Security Middleware
    BACKEND_CORS_ORIGINS: list[str] = []
    ALLOWED_HOSTS: list[str] = ["*"]
    MAX_BODY_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    IP_BLOCKLIST: list[str] = []

    @model_validator(mode="after")
    def assemble_urls(self) -> "Settings":
        if not self.ASYNC_DATABASE_URL:
            self.ASYNC_DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
            )
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = self.REDIS_URL
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = self.REDIS_URL
        return self


settings = Settings()
```

**RULES:**

- NEVER use `os.environ.get()` or `os.getenv()` anywhere — always `settings.*`
- Secrets (`SECRET_KEY`, DB credentials) MUST have NO default value — crash on startup if missing
- The `settings` singleton is imported everywhere; NEVER create a second `Settings()` instance
- Provider secrets (Stripe, SMTP) MAY have empty defaults; the integration MUST fail clearly if used while empty

---

### LAYER 3 — `app/core/database.py`

**You own:** async engine (once), session factory (once), `DeclarativeBase`, timestamp/UUID mixins.
**You do NOT own:** queries, models of features, `AsyncSessionLocal()` calls outside `get_db()`.

```python
# app/core/database.py
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.config import settings

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
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)


async def init_db() -> None:
    """Prove the database is reachable. Never create or alter schema."""
    from sqlalchemy import text

    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
```

**RULES:**

- `create_async_engine()` is called ONCE and ONLY in `core/database.py`
- `AsyncSessionLocal()` is instantiated ONLY inside `core/dependencies.py` → `get_db()`
- NEVER use synchronous `Session` anywhere
- `expire_on_commit=False` is mandatory — never remove it
- NEVER call `Base.metadata.create_all()` or `drop_all()` — in any environment
- NEVER import or run Alembic from this project
- `init_db()` only checks connectivity. Schema already exists because `database/` deployed it

---

### LAYER 4 — `app/core/security.py`

```python
# app/core/security.py
from datetime import datetime, timedelta, timezone

import uuid

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return jwt.encode(
        {
            "sub": subject,
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "type": "access",
            "jti": str(uuid.uuid4()),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            options={"require": ["sub", "iss", "aud", "type", "jti", "exp", "iat"]},
        )
    except InvalidTokenError as exc:
        raise ValueError("Invalid access token") from exc
```

**RULES:**

- This file does JWT and password hashing ONLY
- NEVER import modules, repositories, or models here

---

### LAYER 5 — `app/core/exceptions.py`

```python
# app/core/exceptions.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, detail: str, *, status_code: int = 400) -> None:
        self.detail = detail
        self.status_code = status_code


class CredentialsException(AppException):
    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(detail, status_code=401)


class PermissionDeniedException(AppException):
    def __init__(self, detail: str = "Not enough permissions") -> None:
        super().__init__(detail, status_code=403)


class NotFoundException(AppException):
    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(f"{resource} not found", status_code=404)


class ConflictException(AppException):
    def __init__(self, detail: str) -> None:
        super().__init__(detail, status_code=409)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
        headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=headers,
        )
```

**RULES:**

- Module `exceptions.py` files MUST subclass `AppException` (or the classes above)
- Services raise these exceptions — routers do not convert them
- NEVER raise raw `HTTPException` inside repositories

---

### LAYER 6 — `app/core/dependencies.py`

```python
# app/core/dependencies.py
from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.exceptions import CredentialsException, PermissionDeniedException
from app.core.security import decode_access_token
from app.modules.users.models import User
from app.modules.users.repository import user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise CredentialsException()
    user = await user_repository.get(db, id=user_id)
    if not user:
        raise CredentialsException()
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise CredentialsException(detail="Inactive user")
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not current_user.is_superuser:
        raise PermissionDeniedException()
    return current_user
```

**RULES:**

- `get_db()` is the ONLY function that calls `AsyncSessionLocal()`
- `get_db()` commits on success and rolls back on error — repositories do NOT call `commit()`
- NEVER create a DB session inside a service, repository, task, or middleware
- Define all auth guards here: `get_current_user`, `get_current_active_user`, `get_current_superuser`

---

### LAYER 7 — `app/core/logging.py` and `app/core/constants.py`

```python
# app/core/logging.py
import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    level = logging.INFO if settings.PRODUCTION else logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        stream=sys.stdout,
        force=True,
    )
    logging.getLogger("uvicorn.access").disabled = True
```

```python
# app/core/constants.py
AUTH_TAG = "auth"
USERS_TAG = "users"
ORGANIZATIONS_TAG = "organizations"
BILLING_TAG = "billing"
PAYMENTS_TAG = "payments"
EMAIL_TAG = "email"

HEALTH_PATHS = frozenset({"/health", "/metrics", "/favicon.ico"})
```

**RULES:**

- `core/logging.py` configures the process logger. Request logging lives in `middleware/logging.py`
- Magic strings used in more than one module go in `constants.py` or `common/enums.py`

---

### LAYER 8 — `app/common/`

```python
# app/common/repository.py
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class RepositoryBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    async def get(self, db: AsyncSession, *, id: Any) -> ModelType | None:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType | dict[str, Any]) -> ModelType:
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump()
        db_obj = self.model(**data)
        db.add(db_obj)
        await db.flush()
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
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> ModelType | None:
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj
```

```python
# app/common/pagination.py
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class Page[T](BaseModel):
    items: list[T]
    total: int
    skip: int
    limit: int
```

```python
# app/common/responses.py
from typing import Any

from pydantic import BaseModel, ConfigDict


class AppBaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class MessageResponse(AppBaseSchema):
    detail: str


class ErrorResponse(AppBaseSchema):
    detail: str
    extra: dict[str, Any] | None = None
```

```python
# app/common/enums.py
from enum import StrEnum


class PaymentProvider(StrEnum):
    STRIPE = "stripe"
    RAZORPAY = "razorpay"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
```

```python
# app/common/types.py
import uuid
from typing import TypeAlias

UserId: TypeAlias = uuid.UUID
OrganizationId: TypeAlias = uuid.UUID
```

**RULES:**

- ALL module schemas inherit `AppBaseSchema` — never raw `BaseModel`
- Repositories ALWAYS `flush()` + `refresh()` — NEVER `commit()` (the session dependency commits)
- `common/` has no FastAPI routes and no third-party SDK calls

---

### LAYER 9 — MODULES

Each feature is a package under `app/modules/{feature}/`. The files below are the complete contract.

#### 9.1 Models — `app/modules/{feature}/models.py`

**You own:** mapping Python classes onto tables that **already exist** in PostgreSQL.
**You do NOT own:** creating those tables, altering them, queries, business logic, validation.

```python
# app/modules/users/models.py
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "identity"}  # must match database/schema/tables/identity/users.sql

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    memberships: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember", back_populates="user", cascade="all, delete-orphan"
    )
```

```python
# app/modules/organizations/models.py
import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin


class Organization(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    members: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember", back_populates="organization", cascade="all, delete-orphan"
    )


class OrganizationMember(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "organization_members"
    __table_args__ = (UniqueConstraint("organization_id", "user_id", name="uq_org_user"),)

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(50), default="member", nullable=False)

    organization: Mapped[Organization] = relationship("Organization", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="memberships")
```

```python
# app/modules/__init__.py
from app.modules.users.models import User
from app.modules.organizations.models import Organization, OrganizationMember

__all__ = ["User", "Organization", "OrganizationMember"]
```

**RULES:**

- ALWAYS use `Mapped[T]` — NEVER bare `Column(...)`
- ALWAYS define `__tablename__` and the PostgreSQL schema (`__table_args__ = {"schema": "..."}`)
- Columns, types, and names MUST match `database/schema/` — do not invent extra columns
- NEVER add query methods or a `@property` that runs queries
- NEVER import from `schemas/`, `service.py`, or `router.py` inside `models.py`
- ALWAYS add new models to `app/modules/__init__.py`
- Foreign key columns ALWAYS end in `_id`
- Boolean columns ALWAYS start with `is_` or `has_`
- Timestamp columns ALWAYS end in `_at`
- NEVER add a model for a table that has not been deployed by `database/`

#### 9.2 Schemas — `app/modules/{feature}/schemas.py`

**You own:** request body validation, response serialization.
**You do NOT own:** anything that touches the database.

```python
# app/modules/users/schemas.py
import uuid
from datetime import datetime

from pydantic import EmailStr, Field

from app.common.responses import AppBaseSchema


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
# app/modules/auth/schemas.py
from pydantic import EmailStr, Field

from app.common.responses import AppBaseSchema


class LoginRequest(AppBaseSchema):
    email: EmailStr
    password: str = Field(min_length=1)


class Token(AppBaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    # Return refresh_token only to trusted server/native clients. Browser SPAs
    # receive it as a Secure HttpOnly cookie instead.
    refresh_token: str | None = None


class TokenPayload(AppBaseSchema):
    sub: str | None = None
```

**RULES:**

- EVERY resource needs `{R}Create`, `{R}Read`, `{R}Update`
- `password` ONLY in Create/Update/Login — NEVER in Read
- `hashed_password` NEVER appears in any schema
- NEVER import models or repositories inside schemas
- ALL schemas inherit `AppBaseSchema`

#### 9.3 Repository — `app/modules/{feature}/repository.py`

**You own:** raw DB reads and writes. Return ORM instances or `None`.
**You do NOT own:** business rules, password hashing, HTTP errors, `commit()`.

```python
# app/modules/users/repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repository import RepositoryBase
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserUpdate


class UserRepository(RepositoryBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_active_users(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[User]:
        result = await db.execute(
            select(User).where(User.is_active.is_(True)).offset(skip).limit(limit)
        )
        return list(result.scalars().all())


user_repository = UserRepository(User)
```

```python
# app/modules/auth/repository.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User
from app.modules.users.repository import user_repository


class AuthRepository:
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        return await user_repository.get_by_email(db, email=email)


auth_repository = AuthRepository()
```

**RULES:**

- ALWAYS use `select(Model)` — NEVER `db.query(Model)`
- NEVER raise `HTTPException` / `AppException` in a repository — return `None`
- NEVER hash passwords or send emails in a repository
- ALWAYS expose a module-level singleton: `{resource}_repository = {Resource}Repository(...)`
- ALWAYS use `model_dump(exclude_unset=True)` for partial updates
- NEVER call `db.commit()` — `get_db()` commits
- NEVER execute DDL (`CREATE`, `ALTER`, `DROP`, `TRUNCATE` of schema objects) — rows only

#### 9.4 Service — `app/modules/{feature}/service.py`

**You own:** business logic, validation rules, orchestration, side-effects.
**You do NOT own:** direct SQLAlchemy calls — always go through the repository.

```python
# app/modules/users/service.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, PermissionDeniedException
from app.core.security import get_password_hash
from app.modules.users.exceptions import UserAlreadyExists
from app.modules.users.models import User
from app.modules.users.repository import user_repository
from app.modules.users.schemas import UserCreate, UserUpdate


async def create_user(db: AsyncSession, *, user_in: UserCreate) -> User:
    if await user_repository.get_by_email(db, email=user_in.email):
        raise UserAlreadyExists()
    user_data = user_in.model_dump()
    user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    return await user_repository.create(db, obj_in=user_data)


async def get_user(db: AsyncSession, *, user_id) -> User:
    user = await user_repository.get(db, id=user_id)
    if not user:
        raise NotFoundException("User")
    return user


async def update_user(
    db: AsyncSession, *, user_id, user_in: UserUpdate, current_user: User
) -> User:
    user = await get_user(db, user_id=user_id)
    if user.id != current_user.id and not current_user.is_superuser:
        raise PermissionDeniedException()
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    return await user_repository.update(db, db_obj=user, obj_in=update_data)
```

```python
# app/modules/auth/service.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.modules.auth.exceptions import InvalidCredentials
from app.modules.auth.repository import auth_repository
from app.modules.auth.schemas import Token
from app.modules.users.models import User


async def authenticate_user(db: AsyncSession, *, email: str, password: str) -> User:
    user = await auth_repository.get_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentials()
    if not user.is_active:
        raise InvalidCredentials()
    return user


async def login(db: AsyncSession, *, email: str, password: str) -> Token:
    user = await authenticate_user(db, email=email, password=password)
    # The production implementation also creates a hashed, rotating refresh
    # session as required by the canonical auth contract below.
    return Token(
        access_token=create_access_token(subject=str(user.id)),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
```

**RULES:**

- Services are ALWAYS plain `async def` functions — NEVER classes
- ALWAYS raise `AppException` subclasses here (not in repositories, not in routers)
- ALWAYS hash passwords here before passing to the repository
- NEVER write raw SQL or call `db.execute()` — always use `{resource}_repository`
- Side-effects (email, payments, SMS) go through `app/integrations/` or `app/tasks/`
- Import only from: repositories, `core/`, models, schemas, exceptions, integrations, tasks, common, utils

#### 9.5 Module exceptions — `app/modules/{feature}/exceptions.py`

```python
# app/modules/users/exceptions.py
from app.core.exceptions import ConflictException


class UserAlreadyExists(ConflictException):
    def __init__(self) -> None:
        super().__init__("A user with this email already exists.")
```

```python
# app/modules/auth/exceptions.py
from app.core.exceptions import CredentialsException


class InvalidCredentials(CredentialsException):
    def __init__(self) -> None:
        super().__init__("Invalid email or password")
```

**RULES:**

- Domain exceptions live next to the module that raises them
- They MUST subclass `AppException` (or a core subclass)
- Routers never catch and re-wrap these

#### 9.6 Module router — `app/modules/{feature}/router.py`

**You own:** route definitions, `Depends()` injection, `response_model`.
**You do NOT own:** any logic beyond calling the service.

```python
# app/modules/users/router.py
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import USERS_TAG
from app.core.dependencies import get_current_active_user, get_db
from app.modules.users import service as user_service
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=[USERS_TAG])


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
    return await user_service.get_user(db, user_id=user_id)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await user_service.update_user(
        db, user_id=user_id, user_in=user_in, current_user=current_user
    )
```

```python
# app/modules/auth/router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import AUTH_TAG
from app.core.dependencies import get_db
from app.modules.auth import service as auth_service
from app.modules.auth.schemas import LoginRequest, Token

router = APIRouter(prefix="/auth", tags=[AUTH_TAG])


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(db, email=payload.email, password=payload.password)
```

### Canonical auth contract — implement all four routes

Every backend in this library must expose the same JSON contract under `/api/v1/auth`:

- `POST /login` with `{ "email", "password" }` returns a short-lived access token, `expires_in`, and sets a rotating `Secure; HttpOnly; SameSite=Lax` refresh cookie for browser clients. A trusted BFF/native flow may receive a refresh token through its confidential/native channel.
- `POST /refresh` rotates the refresh token, detects reuse against a server-side hashed session record, and returns a new short-lived access token. Do not accept a non-rotating bearer token forever.
- `POST /logout` revokes the current refresh-token family, clears the cookie, and is idempotent.
- `GET /me` requires the access token and returns `UserRead`. Keep `/users/me` only as a documented compatibility alias if an existing client needs it.

Refresh-token records must store a hash, subject, family/session ID, expiry, revoked/replaced timestamps, and device/audit metadata. Never store raw refresh tokens. Rate-limit login and refresh. Browser cookie flows must validate CSRF and Origin on state-changing requests.

**RULES:**

- EVERY route handler MUST declare `response_model=`
- ALWAYS use `status.HTTP_XXX` — NEVER raw integers like `201`
- Route handlers MUST NOT contain more than ~10 lines of logic
- ALWAYS delegate to `service.py` for anything beyond returning `current_user`
- Path parameter name MUST exactly match the function argument name
- The router variable is ALWAYS named `router`
- Prefix and tags live on the module router, not in `api/v1/router.py`

---

### LAYER 10 — `app/api/`

```python
# app/api/router.py
from fastapi import APIRouter

from app.api.v1.router import api_v1_router
from app.core.config import settings

api_router = APIRouter()


@api_router.get("/health", include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "ok"}


api_router.include_router(api_v1_router, prefix=settings.API_V1_STR)
```

```python
# app/api/v1/router.py
from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.billing.router import router as billing_router
from app.modules.email.router import router as email_router
from app.modules.organizations.router import router as organizations_router
from app.modules.payments.router import router as payments_router
from app.modules.users.router import router as users_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(organizations_router)
api_v1_router.include_router(email_router)
api_v1_router.include_router(billing_router)
api_v1_router.include_router(payments_router)
```

**RULES:**

- `api/` NEVER contains endpoint handler logic except `/health`
- A new module is not public until it is included in `app/api/v1/router.py`
- Do not invent `app/api/v1/endpoints/`

---

### LAYER 11 — `app/integrations/`

**You own:** third-party SDKs (Stripe, Razorpay, SMTP, S3, SMS).
**You do NOT own:** HTTP routes, ORM models, business rules.

```python
# app/integrations/payments/base.py
from abc import ABC, abstractmethod
from typing import Any


class PaymentGateway(ABC):
    @abstractmethod
    async def create_checkout(self, *, amount_cents: int, currency: str, metadata: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    async def verify_webhook(self, *, payload: bytes, signature: str) -> dict[str, Any]:
        ...
```

```python
# app/integrations/payments/stripe.py
from typing import Any

import stripe

from app.core.config import settings
from app.integrations.payments.base import PaymentGateway


class StripeGateway(PaymentGateway):
    def __init__(self) -> None:
        stripe.api_key = settings.STRIPE_SECRET_KEY

    async def create_checkout(
        self, *, amount_cents: int, currency: str, metadata: dict[str, Any]
    ) -> dict[str, Any]:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": currency,
                    "unit_amount": amount_cents,
                    "product_data": {"name": metadata.get("description", "Payment")},
                },
                "quantity": 1,
            }],
            success_url=metadata["success_url"],
            cancel_url=metadata["cancel_url"],
            metadata=metadata,
        )
        return {"provider": "stripe", "id": session.id, "url": session.url}

    async def verify_webhook(self, *, payload: bytes, signature: str) -> dict[str, Any]:
        event = stripe.Webhook.construct_event(
            payload, signature, settings.STRIPE_WEBHOOK_SECRET
        )
        return {"type": event["type"], "data": event["data"]["object"]}
```

```python
# app/integrations/email/base.py
from abc import ABC, abstractmethod


class EmailProvider(ABC):
    @abstractmethod
    async def send(self, *, to: str, subject: str, html: str) -> None:
        ...
```

Pick the gateway from `settings.PAYMENT_PROVIDER` inside the **module service**, not inside the router.

**RULES:**

- Integrations NEVER import from `modules/`
- Routers NEVER import from `integrations/`
- Wrap every SDK call. Do not scatter `stripe.` / SMTP clients through services
- One class per provider file

---

### LAYER 12 — `app/tasks/`

```python
# app/tasks/celery_app.py
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)
celery_app.conf.update(task_serializer="json", accept_content=["json"], result_serializer="json")
```

```python
# app/tasks/email_tasks.py
from app.integrations.email.provider import email_provider
from app.tasks.celery_app import celery_app


@celery_app.task(name="email.send")
def send_email_task(to: str, subject: str, html: str) -> None:
    import asyncio

    asyncio.run(email_provider.send(to=to, subject=subject, html=html))
```

**RULES:**

- Tasks call services or integrations — NEVER routers
- Tasks do not accept ORM instances — pass IDs and primitives only
- Do not put Celery config in `main.py`

---

### LAYER 13 — `app/utils/`

```python
# app/utils/dates.py
from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
```

```python
# app/utils/strings.py
import re

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    return _SLUG_RE.sub("-", value.strip().lower()).strip("-")
```

```python
# app/utils/identifiers.py
import uuid


def new_id() -> uuid.UUID:
    return uuid.uuid4()
```

**RULES:**

- Pure functions only — no I/O, no `settings`, no DB, no FastAPI
- NEVER create `utils.py` at any folder root
- A function used by one module stays in that module's `service.py`

---

### LAYER 14 — `app/middleware/` — THE REQUEST FILTER GATE

Every request passes through this pipeline before reaching any route.
**Execution order** (outermost = first to receive the request):

```
Request In
    │
    ▼  ① TrustedHost       → invalid Host header?        → 400
    ▼  ② HTTPSRedirect      → HTTP in production?         → 301
    ▼  ③ RequestID          → stamp X-Request-ID (uuid4)
    ▼  ④ RequestLogging     → log method/path/status/ms
    ▼  ⑤ IPBlocklist        → banned IP?                  → 403
    ▼  ⑥ SecurityHeaders    → inject API-safe headers
    ▼  ⑦ BodySizeLimit      → body > 10MB?                → 413
    ▼  ⑧ CORS               → cross-origin check
    ▼  ⑨ GZip               → compress response
    │
    ▼
Route Handler
```

#### `app/middleware/__init__.py`

```python
# app/middleware/__init__.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.middleware.body_size import RequestSizeLimitMiddleware
from app.middleware.ip_blocklist import IPBlocklistMiddleware
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware


def register_middleware(app: FastAPI) -> None:
    # Registered in reverse: last added = outermost = first executed
    app.add_middleware(GZipMiddleware, minimum_size=1000)  # ⑨
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-CSRF-Token"],
        expose_headers=["X-Request-ID"],
    )  # ⑧
    app.add_middleware(RequestSizeLimitMiddleware, max_body_size=settings.MAX_BODY_SIZE_BYTES)  # ⑦
    app.add_middleware(SecurityHeadersMiddleware)  # ⑥
    app.add_middleware(IPBlocklistMiddleware, blocklist=settings.IP_BLOCKLIST)  # ⑤
    app.add_middleware(RequestLoggingMiddleware)  # ④
    app.add_middleware(RequestIDMiddleware)  # ③
    if settings.PRODUCTION:
        app.add_middleware(HTTPSRedirectMiddleware)  # ②
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)  # ①
```

#### `app/middleware/request_id.py`

```python
# app/middleware/request_id.py
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

#### `app/middleware/logging.py`

```python
# app/middleware/logging.py
import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.constants import HEALTH_PATHS

logger = logging.getLogger("app.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in HEALTH_PATHS:
            return await call_next(request)

        request_id = getattr(request.state, "request_id", "-")
        client_ip = request.client.host if request.client else "unknown"
        start = time.perf_counter()

        try:
            response = await call_next(request)
            logger.info(
                "%s %s %s %.1fms [req=%s] [ip=%s]",
                request.method,
                request.url.path,
                response.status_code,
                (time.perf_counter() - start) * 1000,
                request_id,
                client_ip,
            )
            return response
        except Exception as exc:
            logger.error(
                "%s %s ERROR %.1fms [req=%s] [ip=%s] — %s",
                request.method,
                request.url.path,
                (time.perf_counter() - start) * 1000,
                request_id,
                client_ip,
                str(exc),
            )
            raise
```

#### Tenant isolation — authenticated claims, never request headers

Never trust `X-Tenant-ID` or any client-selected tenant identifier. Derive the active tenant from validated authentication claims and verified membership. A tenant-aware dependency must set `SET LOCAL app.tenant_id = :tenant_id` on the same `AsyncSession` transaction before tenant queries run. Every tenant-owned repository method must also include an explicit `tenant_id` predicate. PostgreSQL RLS is the final defense, not the only defense.

For users with access to multiple tenants, accept a tenant selection only as an opaque membership ID, verify it belongs to the current subject, then derive the tenant ID server-side. Clear transaction-local context automatically by ending the transaction; never use session-level `SET` with pooled connections.

#### Rate-limit policy

Use the reverse proxy/API gateway for coarse IP limits and Redis (atomic script/token bucket) for application/account limits. Never use an in-process dictionary/deque in production: it is bypassed across workers, loses state on restart, and can grow without bound. Trust `Forwarded`/`X-Forwarded-For` only from configured proxy IPs; otherwise use the direct peer address. Authentication, password reset, and expensive endpoints need distinct policies.

#### `app/middleware/security_headers.py`

```python
# app/middleware/security_headers.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    _HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=()",
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for header, value in self._HEADERS.items():
            response.headers[header] = value
        response.headers.pop("Server", None)
        response.headers.pop("X-Powered-By", None)
        return response
```

Set HSTS at the TLS-terminating proxy, not on an internal HTTP hop. Generate CSP in the HTML frontend with nonces/hashes. Apply `Cache-Control: no-store` only to sensitive/authenticated responses; do not disable caching globally for public immutable resources.

#### `app/middleware/body_size.py`

```python
# app/middleware/body_size.py
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
                content={"detail": f"Body too large. Max: {self.max_body_size // (1024 * 1024)} MB."},
            )
        return await call_next(request)
```

#### `app/middleware/ip_blocklist.py`

```python
# app/middleware/ip_blocklist.py
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
- NEVER import from `modules/` or `integrations/` in middleware
- NEVER log `Authorization`, `Cookie`, or `X-Api-Key` headers
- `X-Request-ID` MUST be present on every request and response
- `/health` and `/metrics` MUST be exempt from rate limiting
- `register_middleware()` is the ONLY place `app.add_middleware()` is called

---

### LAYER 15 — SCHEMA OWNERSHIP (not in this repo)

There is **no** `alembic/` folder and **no** `alembic.ini` in the backend.

| Who | What |
| --- | --- |
| `database/` + `python scripts/db_deploy.py` | Create and modify tables, columns, types, views, indexes, RLS |
| This FastAPI app | Map those objects. Read and write rows |

If the user asks for a new column or table in the backend chat: do **not** generate a migration. Point them at `DATABASE_STRUCTURE.md`, wait until deploy says `STATUS: ✓ DATABASE IS IN SYNC`, then add or update `models.py` to match.

---

### LAYER 16 — TESTS, SCRIPTS, DOCS, CI

```python
# tests/conftest.py
import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
```

**Test placement:**

| Kind | Path |
| --- | --- |
| Service / schema / exception unit tests | `tests/unit/{module}/` |
| Repository + real DB | `tests/integration/repositories/` |
| Provider adapters | `tests/integration/integrations/` |
| HTTP contracts | `tests/api/{module}/` |

```python
# scripts/seed.py
"""Idempotent local seed. Never import this from app code."""
```

```makefile
# Makefile
.PHONY: install run test lint

install:
	uv sync

run:
	uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000

test:
	uv run pytest

lint:
	uv run ruff check .
```

Schema changes are **not** a backend Make target. Run them from `database/`: `python scripts/db_deploy.py`.

**CI / Docker rules:**

- `.env` and `.env.production` are gitignored. `.env.example` is committed with empty secrets
- Dockerfile runs `uvicorn main:app --host 0.0.0.0 --port 8000`
- `docker-compose.yml` uses `expose` for the API port when Traefik is in front — do not publish the backend port
- GitHub workflows: `test.yml` runs pytest, `lint.yml` runs ruff, `build.yml` builds the image, `deploy.yml` is environment-specific

---

## NAMING CONVENTIONS — MEMORISE THESE

| What | Convention | Examples |
| --- | --- | --- |
| File names | `snake_case.py` | `repository.py` |
| Module folder | `snake_case` plural domain | `users`, `organizations` |
| ORM Model class | `PascalCase` | `OrganizationMember` |
| Table name | `snake_case` plural | `organization_members` |
| Schema class | `PascalCase` + suffix | `UserCreate`, `UserRead` |
| Repository class | `PascalCase` + `Repository` | `UserRepository` |
| Repository singleton | `{resource}_repository` | `user_repository` |
| Service function | `verb_noun` async def | `create_user()` |
| Route handler | `verb_noun` async def | `create_user()` |
| Router variable | always `router` | `router = APIRouter()` |
| Domain exception | `PascalCase` | `UserAlreadyExists` |
| Integration class | `PascalCase` + role | `StripeGateway`, `SmtpEmailProvider` |
| Foreign key column | `{singular}_id` | `user_id`, `organization_id` |
| Boolean column | `is_` / `has_` prefix | `is_active`, `has_verified` |
| Timestamp column | `_at` suffix | `created_at`, `deleted_at` |
| Env vars | `UPPER_SNAKE_CASE` | `ASYNC_DATABASE_URL` |

---

## WHEN ADDING A NEW MODULE

When the user asks you to add a new resource (e.g., "Order"), you MUST create ALL of these — no skipping.

The table MUST already exist in the live database (`database/` deployed it). If it does not, stop and say so. Do not create it from this app.

```
STEP 0  Confirm database/ already deployed the table (db_deploy.py in sync)
STEP 1  app/modules/orders/__init__.py
STEP 2  app/modules/orders/models.py           ← map the existing table only
STEP 3  app/modules/orders/schemas.py          ← OrderCreate, OrderRead, OrderUpdate
STEP 4  app/modules/orders/exceptions.py       ← domain exceptions
STEP 5  app/modules/orders/repository.py       ← OrderRepository + order_repository
STEP 6  app/modules/orders/service.py          ← async def business logic
STEP 7  app/modules/orders/router.py           ← APIRouter prefix="/orders"
STEP 8  app/modules/__init__.py                ← export Order
STEP 9  app/api/v1/router.py                   ← include_router(orders_router)
STEP 10 tests/unit/orders/ + tests/api/orders/
```

If the feature talks to a vendor, ALSO add `app/integrations/{vendor}/` and call it from the module service — never from the router.

---

## ABSOLUTE PROHIBITIONS — NEVER DO THESE

```
✗  os.getenv() or os.environ anywhere — use settings.*
✗  db.query(Model) — use select(Model)
✗  Session (sync) — use AsyncSession only
✗  create_async_engine() outside app/core/database.py
✗  AsyncSessionLocal() outside get_db()
✗  db.commit() inside a repository — get_db() commits
✗  HTTPException / AppException raised in repository
✗  import models inside schemas
✗  import modules/ or integrations/ inside middleware
✗  import another module's router
✗  Route definitions in main.py
✗  Business logic in route handlers
✗  app.add_middleware() outside register_middleware()
✗  Layered leftovers: app/models/, app/crud/, app/services/, app/api/v1/endpoints/
✗  Multiple features in one module package
✗  Plaintext passwords stored anywhere
✗  Auth headers (Authorization, Cookie) in log output
✗  /docs or /openapi.json exposed in production
✗  Base.metadata.create_all() or drop_all() — any environment
✗  Alembic, alembic.ini, alembic revision, or alembic upgrade
✗  CREATE / ALTER / DROP issued from the ORM or repositories
✗  Adding a model for a table that database/ has not deployed
✗  A catch-all utils.py
✗  SDK clients (stripe, smtp) used inside routers
```

---

## PRE-COMPLETION CHECKLIST

Before you say you are done with any task, verify every item:

```
[ ] New ORM model lives in app/modules/{feature}/models.py
[ ] New model exported from app/modules/__init__.py
[ ] New module router registered in app/api/v1/router.py
[ ] No route handler has more than ~10 lines of logic
[ ] No service calls db.execute() (goes through repository)
[ ] No repository calls db.commit()
[ ] No schema imports from models
[ ] Every route handler has response_model= declared
[ ] All DB-touching functions are async def
[ ] All config from settings.* — no os.getenv()
[ ] No Alembic and no create_all — schema comes from database/ only
[ ] New model maps a table that already exists in the live DB
[ ] Passwords hashed in the service — never plaintext
[ ] All middleware in register_middleware() only
[ ] SecurityHeadersMiddleware is in the middleware stack
[ ] No sensitive headers in any log line
[ ] X-Request-ID on all requests and responses
[ ] Production mode: docs_url=None, openapi_url=None
[ ] No app/models/, app/crud/, or app/services/ folders exist
```

---

## QUICK REFERENCE — REQUEST FLOW

```
POST /api/v1/users/
  → edge/gateway limits → middleware (RequestID → Log → IP policy → Security → ...)
  → app/api/router.py              /api/v1 mount
  → app/api/v1/router.py           users router
  → modules/users/router.py        create_user()
  → modules/users/service.py       create_user()   [duplicate check, hash password]
  → modules/users/repository.py    create()        [add + flush + refresh]
  → modules/users/models.py        User
  → modules/users/schemas.py       UserRead
```

---

_Stack baseline (verified 2026-10-14): Python 3.15 · FastAPI 0.143+ · SQLAlchemy 2.0 · Pydantic v2 · PostgreSQL 18 · Celery 5 · uv | v3.1_

---

## Copyright

© 2026 **Udhayaboopathi V**. Released under the repository's MIT License.

- Author: Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub: [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
