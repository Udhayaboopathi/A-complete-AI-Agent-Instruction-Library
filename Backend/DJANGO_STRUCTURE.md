# AGENT INSTRUCTIONS — Django (Python) Backend

> **HOW TO USE THIS FILE**
> Drop this file into your project root. When starting a new chat, say:
> _"Read `DJANGO_STRUCTURE.md` deeply and follow every instruction in it for all code you generate."_
> This file is the single source of truth. No exceptions.

---

## YOUR IDENTITY

You are a senior Python backend engineer building production Django REST APIs.
Every file you generate MUST follow the exact structure, patterns, and rules in this document.
You have creative freedom only over business logic inside the defined boundaries.

---

## TECH STACK — USE EXACTLY THESE

```
Framework       : Django 5.x              + Django REST Framework 3.15
Language        : Python 3.12
ORM             : Django ORM              (built-in)
Database        : PostgreSQL 16
Migrations      : Django Migrations       (built-in)
Auth            : djangorestframework-simplejwt 5.x
Validation      : DRF Serializers         (built-in)
CORS            : django-cors-headers 4.x
Filtering       : django-filter 24.x
Settings split  : django-environ 0.11.x   (env vars)
Testing         : pytest-django 4.x       + factory_boy
```

---

## MANDATORY FOLDER STRUCTURE

```
project_name/
│
├── config/                                 # Project-level config (not an app)
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                         # All shared settings
│   │   ├── development.py                  # Dev overrides
│   │   └── production.py                   # Prod overrides
│   ├── urls.py                             # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                                   # All Django apps live here
│   │
│   ├── core/                               # Shared utilities — not a feature app
│   │   ├── __init__.py
│   │   ├── models.py                       # BaseModel (id, timestamps)
│   │   ├── pagination.py                   # Standard pagination class
│   │   ├── permissions.py                  # Shared DRF permission classes
│   │   └── exceptions.py                   # Custom exception classes
│   │
│   ├── users/                              # One folder per feature domain
│   │   ├── __init__.py
│   │   ├── models.py                       # User ORM model
│   │   ├── serializers.py                  # DRF serializers (input + output)
│   │   ├── views.py                        # DRF ViewSets
│   │   ├── urls.py                         # App-level URL routing
│   │   ├── services.py                     # Business logic functions
│   │   ├── permissions.py                  # App-specific permissions
│   │   ├── filters.py                      # django-filter FilterSets
│   │   ├── admin.py                        # Django admin registration
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── factories.py                # factory_boy model factories
│   │       ├── test_models.py
│   │       ├── test_serializers.py
│   │       ├── test_services.py
│   │       └── test_views.py
│   │
│   └── items/                              # Same structure for every app
│       ├── __init__.py
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── services.py
│       ├── filters.py
│       ├── admin.py
│       └── tests/
│           ├── __init__.py
│           ├── factories.py
│           └── test_views.py
│
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── manage.py
├── .env
└── .env.example
```

---

## ARCHITECTURAL LAYERS

```
apps/core/models.py    → BaseModel only. Shared by all apps.
apps/{app}/models.py   → ORM table definitions. No queries. No business logic.
apps/{app}/serializers.py → DRF input validation + output serialization. No queries.
apps/{app}/services.py → ALL business logic. Calls ORM directly. Raises exceptions.
apps/{app}/views.py    → DRF ViewSets. Calls services. Returns Response. No logic.
apps/{app}/urls.py     → Router registration only.
apps/{app}/filters.py  → django-filter FilterSets for list endpoints.
apps/{app}/permissions.py → DRF IsAuthenticated subclasses.
```

---

## LAYER 1 — `apps/core/models.py` — Base Model

```python
# apps/core/models.py
import uuid
from django.db import models


class BaseModel(models.Model):
    """
    Every app model must inherit this.
    Provides UUID primary key and auto timestamps.
    """
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True   # MUST be abstract — never instantiated directly
```

---

## LAYER 2 — `apps/{app}/models.py` — ORM Models

```python
# apps/users/models.py
from django.db import models
from apps.core.models import BaseModel


class User(BaseModel):
    class Role(models.TextChoices):
        ADMIN   = "admin",   "Admin"
        MANAGER = "manager", "Manager"
        STAFF   = "staff",   "Staff"
        VIEWER  = "viewer",  "Viewer"

    email           = models.EmailField(max_length=255, unique=True, db_index=True)
    hashed_password = models.CharField(max_length=255)
    full_name       = models.CharField(max_length=255, blank=True, null=True)
    is_active       = models.BooleanField(default=True)
    role            = models.CharField(max_length=50, choices=Role.choices,
                                       default=Role.STAFF)

    class Meta:
        db_table  = "users"
        ordering  = ["-created_at"]
        indexes   = [models.Index(fields=["email"])]

    def __str__(self):
        return self.email
```

```python
# apps/items/models.py
from django.db import models
from apps.core.models import BaseModel
from apps.users.models import User


class Item(BaseModel):
    title       = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    owner       = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="items"
    )

    class Meta:
        db_table = "items"
        ordering = ["-created_at"]
        indexes  = [models.Index(fields=["owner_id"])]

    def __str__(self):
        return self.title
```

**Model Rules:**
- ALWAYS inherit `BaseModel` — never define `id`/`created_at`/`updated_at` per-model
- ALWAYS set `db_table` explicitly — never use Django auto-naming
- ALWAYS use `TextChoices` for enum fields — never bare strings
- NEVER put business methods or query logic in models
- NEVER use `CharField` for passwords — always `hashed_password` with hash in service

---

## LAYER 3 — `apps/{app}/serializers.py` — DRF Serializers

```python
# apps/users/serializers.py
from rest_framework import serializers
from apps.users.models import User


class UserCreateSerializer(serializers.Serializer):
    """Input validation for POST /users/"""
    email     = serializers.EmailField(max_length=255)
    full_name = serializers.CharField(min_length=2, max_length=255)
    password  = serializers.CharField(min_length=8, max_length=128,
                                      write_only=True, style={"input_type": "password"})
    role      = serializers.ChoiceField(choices=User.Role.choices,
                                        default=User.Role.STAFF)

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate_password(self, value: str) -> str:
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("Password must contain an uppercase letter.")
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("Password must contain a number.")
        return value


class UserUpdateSerializer(serializers.Serializer):
    """Input validation for PATCH /users/{id}/"""
    email     = serializers.EmailField(max_length=255, required=False)
    full_name = serializers.CharField(min_length=2, max_length=255, required=False)
    password  = serializers.CharField(min_length=8, max_length=128,
                                      write_only=True, required=False,
                                      style={"input_type": "password"})
    is_active = serializers.BooleanField(required=False)


class UserResponseSerializer(serializers.ModelSerializer):
    """Output shape for all user responses. NEVER includes hashed_password."""
    class Meta:
        model  = User
        fields = ["id", "email", "full_name", "is_active", "role",
                  "created_at", "updated_at"]
        read_only_fields = fields   # response serializers are read-only


class UserListResponseSerializer(serializers.ModelSerializer):
    """Lighter response for list endpoints."""
    class Meta:
        model  = User
        fields = ["id", "email", "full_name", "is_active", "role", "created_at"]
        read_only_fields = fields
```

**Serializer Rules:**
- Input serializers (`Create`/`Update`) use `serializers.Serializer` — NOT `ModelSerializer`
- Output serializers (`Response`) use `ModelSerializer` — list only allowed fields explicitly
- `hashed_password` is NEVER in any output serializer `fields`
- `password` field always has `write_only=True`
- Cross-field uniqueness checks go in `validate_{field}` — not in service
- ALL fields in response serializer must be in `read_only_fields`

---

## LAYER 4 — `apps/{app}/services.py` — Business Logic

```python
# apps/users/services.py
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.users.models import User
from apps.users.serializers import UserCreateSerializer, UserUpdateSerializer


def create_user(*, data: dict) -> User:
    """
    Validates data, hashes password, and creates a User.
    Raises ValidationError if email already exists (checked in serializer).
    """
    serializer = UserCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    validated = serializer.validated_data
    user = User.objects.create(
        email           = validated["email"],
        full_name       = validated.get("full_name"),
        hashed_password = make_password(validated["password"]),
        role            = validated.get("role", User.Role.STAFF),
    )
    return user


def get_user_by_id(*, user_id: str) -> User:
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise NotFound(f"User {user_id} not found.")


def update_user(*, user_id: str, data: dict, requesting_user: User) -> User:
    user = get_user_by_id(user_id=user_id)

    if str(user.id) != str(requesting_user.id) and requesting_user.role != User.Role.ADMIN:
        raise PermissionDenied("You do not have permission to update this user.")

    serializer = UserUpdateSerializer(data=data, partial=True)
    serializer.is_valid(raise_exception=True)

    validated = serializer.validated_data
    for field in ["email", "full_name", "is_active"]:
        if field in validated:
            setattr(user, field, validated[field])

    if "password" in validated:
        user.hashed_password = make_password(validated["password"])

    user.save()
    return user


def delete_user(*, user_id: str) -> None:
    user = get_user_by_id(user_id=user_id)
    user.delete()


def authenticate_user(*, email: str, password: str) -> User | None:
    try:
        user = User.objects.get(email=email.lower(), is_active=True)
    except User.DoesNotExist:
        return None
    return user if check_password(password, user.hashed_password) else None
```

**Service Rules:**
- Services are ALWAYS plain functions — NEVER class-based
- ALWAYS use keyword-only arguments (`*`) — prevents positional argument confusion
- ALWAYS raise DRF exceptions (`NotFound`, `PermissionDenied`, `ValidationError`)
- Password hashing ALWAYS in service — never in views or models
- Services NEVER return `None` to indicate failure — always raise

---

## LAYER 5 — `apps/{app}/views.py` — DRF ViewSets

```python
# apps/users/views.py
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.core.pagination import StandardPagination
from apps.users import services as user_service
from apps.users.models import User
from apps.users.permissions import IsAdminUser, IsAdminOrSelf
from apps.users.serializers import UserCreateSerializer, UserResponseSerializer


class UserViewSet(ViewSet):
    """
    list:   GET  /api/v1/users/
    create: POST /api/v1/users/
    retrieve: GET  /api/v1/users/{id}/
    partial_update: PATCH /api/v1/users/{id}/
    destroy: DELETE /api/v1/users/{id}/
    """
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.action in ["create", "destroy"]:
            return [IsAdminUser()]
        if self.action == "partial_update":
            return [IsAdminOrSelf()]
        return [IsAuthenticated()]

    def list(self, request: Request) -> Response:
        queryset   = User.objects.filter(is_active=True).order_by("-created_at")
        paginator  = self.pagination_class()
        page       = paginator.paginate_queryset(queryset, request)
        serializer = UserResponseSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request: Request) -> Response:
        user       = user_service.create_user(data=request.data)
        serializer = UserResponseSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request: Request, pk: str = None) -> Response:
        user       = user_service.get_user_by_id(user_id=pk)
        serializer = UserResponseSerializer(user)
        return Response(serializer.data)

    def partial_update(self, request: Request, pk: str = None) -> Response:
        user = user_service.update_user(
            user_id          = pk,
            data             = request.data,
            requesting_user  = request.user,
        )
        return Response(UserResponseSerializer(user).data)

    def destroy(self, request: Request, pk: str = None) -> Response:
        user_service.delete_user(user_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request: Request) -> Response:
        return Response(UserResponseSerializer(request.user).data)
```

**View Rules:**
- ViewSets call service functions — never ORM queries directly in views
- `get_permissions` controls access per action — not inline `if` checks
- NEVER put validation logic in views — serializers and services handle it
- NEVER return `hashed_password` in any response

---

## LAYER 6 — `apps/{app}/urls.py` — Routing

```python
# apps/users/urls.py
from rest_framework.routers import DefaultRouter
from apps.users.views import UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = router.urls
```

```python
# config/urls.py
from django.urls import path, include

urlpatterns = [
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/", include("apps.items.urls")),
    # Add new app URLs here
]
```

---

## LAYER 7 — `apps/core/pagination.py`

```python
# apps/core/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_size              = 20
    page_size_query_param  = "size"
    max_page_size          = 100
    page_query_param       = "page"

    def get_paginated_response(self, data):
        return Response({
            "items":  data,
            "total":  self.page.paginator.count,
            "page":   self.page.number,
            "size":   self.get_page_size(self.request),
            "pages":  self.page.paginator.num_pages,
        })

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "items": schema,
                "total": {"type": "integer"},
                "page":  {"type": "integer"},
                "size":  {"type": "integer"},
                "pages": {"type": "integer"},
            },
        }
```

---

## LAYER 8 — `config/settings/base.py`

```python
# config/settings/base.py
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG      = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    # Project apps — always use full path
    "apps.core",
    "apps.users",
    "apps.items",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # MUST be first
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": env.db("DATABASE_URL")
    # DATABASE_URL=postgres://user:password@127.0.0.1:5432/dbname
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",   # JSON only — no BrowsableAPI in prod
    ],
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "apps.core.exceptions.custom_exception_handler",
}

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=env.int("JWT_ACCESS_MINUTES", 30)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_DAYS", 7)),
    "ALGORITHM":              "HS256",
    "SIGNING_KEY":            env("JWT_SECRET_KEY"),
    "AUTH_HEADER_TYPES":      ("Bearer",),
}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True
```

```python
# config/settings/production.py
from .base import *

DEBUG = False

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    # BrowsableAPIRenderer NOT included — never show in production
]

SECURE_HSTS_SECONDS              = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS   = True
SECURE_HSTS_PRELOAD              = True
SECURE_SSL_REDIRECT              = True
SESSION_COOKIE_SECURE            = True
CSRF_COOKIE_SECURE               = True
```

---

## LAYER 9 — `apps/core/exceptions.py`

```python
# apps/core/exceptions.py
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Returns consistent error shape for all API errors.
    Production: generic 500 message — never stack trace.
    """
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "detail":     response.data.get("detail", str(response.data)),
            "status_code": response.status_code,
        }
        return response

    # Unhandled exception — log it, return generic message
    logger.exception("Unhandled exception in %s", context.get("view"))
    return Response(
        {"detail": "An internal error occurred.", "status_code": 500},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
```

---

## LAYER 10 — `.env` and `requirements/`

```bash
# .env
DJANGO_SECRET_KEY=generate-with-python-secrets-token-hex-32
DEBUG=false
ALLOWED_HOSTS=api.yourdomain.com
DATABASE_URL=postgres://appuser:strong-password@127.0.0.1:5432/appdb
JWT_SECRET_KEY=generate-with-python-secrets-token-hex-32
JWT_ACCESS_MINUTES=30
JWT_REFRESH_DAYS=7
CORS_ALLOWED_ORIGINS=https://app.yourdomain.com,https://admin.yourdomain.com
```

```text
# requirements/base.txt
Django>=5.0,<6.0
djangorestframework>=3.15,<4.0
djangorestframework-simplejwt>=5.3,<6.0
django-cors-headers>=4.3,<5.0
django-filter>=24.0,<25.0
django-environ>=0.11,<1.0
psycopg[binary]>=3.1,<4.0
```

```text
# requirements/development.txt
-r base.txt
pytest-django>=4.8,<5.0
factory-boy>=3.3,<4.0
```

```text
# requirements/production.txt
-r base.txt
gunicorn>=22.0,<23.0
```

---

## NAMING CONVENTIONS

| What | Convention | Example |
|------|-----------|---------|
| App names | `lowercase` singular | `users`, `items` |
| Model classes | `PascalCase` singular | `User`, `ItemCategory` |
| Table names | `snake_case` plural via `db_table` | `users`, `item_categories` |
| Serializer classes | `{Resource}{Action}Serializer` | `UserCreateSerializer`, `UserResponseSerializer` |
| ViewSet classes | `{Resource}ViewSet` | `UserViewSet` |
| Service functions | `verb_noun` | `create_user()`, `get_user_by_id()` |
| URL basename | `lowercase` singular | `basename="user"` |
| Fixtures/factories | `{Model}Factory` | `UserFactory` |
| Test files | `test_{module}.py` | `test_views.py` |

---

## WHEN ADDING A NEW RESOURCE

```
STEP 1   Create Django app:
         python manage.py startapp {resource} apps/{resource}

STEP 2   apps/{resource}/models.py
         → Model class extending BaseModel with db_table set

STEP 3   config/settings/base.py
         → add "apps.{resource}" to INSTALLED_APPS

STEP 4   apps/{resource}/serializers.py
         → {Resource}CreateSerializer, {Resource}UpdateSerializer, {Resource}ResponseSerializer

STEP 5   apps/{resource}/services.py
         → create_{resource}(), get_{resource}_by_id(), update_{resource}(), delete_{resource}()

STEP 6   apps/{resource}/views.py
         → {Resource}ViewSet with get_permissions()

STEP 7   apps/{resource}/urls.py
         → DefaultRouter registration

STEP 8   config/urls.py
         → include("apps.{resource}.urls")

STEP 9   python manage.py makemigrations {resource}
         python manage.py migrate

STEP 10  apps/{resource}/filters.py
         → {Resource}Filter(django_filters.FilterSet) if the list endpoint needs filtering

STEP 11  apps/{resource}/admin.py
         → Register model with Django admin
```

---

## ABSOLUTE PROHIBITIONS

```
✗  ORM queries directly in views — always go through services
✗  hashed_password in any Response serializer fields list
✗  ModelSerializer for input (Create/Update) — use plain Serializer
✗  Business logic in serializers (beyond field-level validation)
✗  Password hashing in models or views — services only
✗  DEBUG=True in production
✗  BrowsableAPIRenderer in production — JSON only
✗  CORS_ALLOW_ALL_ORIGINS = True in production
✗  Generic Exception catch without logging
✗  Returning stack traces in production API responses
✗  db_table missing from any model Meta class
✗  Service functions using positional arguments — always keyword-only (*)
✗  Direct User.objects.get() in views — always through service
✗  manage.py runserver in production — use gunicorn
```

---

## PRE-COMPLETION CHECKLIST

```
[ ] All models inherit BaseModel — no manual id/timestamp fields
[ ] db_table set in every model Meta class
[ ] Input serializers use serializers.Serializer — not ModelSerializer
[ ] hashed_password never in any ResponseSerializer fields
[ ] password has write_only=True in all serializers
[ ] Service functions use keyword-only args (def fn(*, key=value))
[ ] Passwords hashed in service using make_password()
[ ] Views call services — no direct ORM queries
[ ] New app added to INSTALLED_APPS in settings/base.py
[ ] URL routing registered in config/urls.py
[ ] Migration created: python manage.py makemigrations
[ ] CORS_ALLOWED_ORIGINS is explicit list — never True
[ ] Production settings has BrowsableAPIRenderer removed
[ ] custom_exception_handler registered in REST_FRAMEWORK settings
[ ] .env never committed — .env.example committed with empty values
```

---

*Stack: Django 5.x · Python 3.12 · Django REST Framework · PostgreSQL · SimpleJWT · django-cors-headers · django-filter · pytest-django*

---

## Copyright

© 2026 **Udhayaboopathi V**. All rights reserved.

- Author:  Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub:  [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
