# HOW TO USE — Agent Prompt Library

> This is your complete guide for using these agent instruction files in a real project.
> Read this once. Follow the steps. Your AI agent will write production-quality code every time.

---

## WHAT THIS LIBRARY IS

10 agent instruction files that define the exact architecture, code patterns, and rules for every layer of an enterprise application. Drop the relevant files into your project, reference them in your chat prompt, and the agent follows them without deviation.

```
Backend/
  FASTAPI_ORM_STRUCTURE.md      → Python FastAPI + SQLAlchemy backend
  DJANGO_STRUCTURE.md           → Python Django + DRF backend
  ASPNET_STRUCTURE.md           → C# ASP.NET Core backend
  SPRINGBOOT_STRUCTURE.md       → Java Spring Boot backend

Frontend/
  NEXTJS_FRONTEND_STRUCTURE.md  → Next.js 16.4 frontend (SSR + App Router)
  REACTJS_FRONTEND_STRUCTURE.md → React + Vite SPA frontend
  ANGULARJS_FRONTEND_STRUCTURE.md → Angular 22 frontend
  FLUTTER_STRUCTURE.md          → Flutter multi-platform (Mobile + Desktop + Web)

Database/
  DATABASE_STRUCTURE.md         → Standalone PostgreSQL project + reconcile engine

Security/
  SECURITY_LAYER.md             → Full-stack security (Traefik + TLS + auth + headers)

Skill/
  FASTAPI_NEXTJS_STACK.md       → Master prompt for FastAPI + Next.js + DB + Security
```

---

## STEP 1 — PICK YOUR STACK

Choose one file from each category based on your project:

| Category | Options                                  | Pick one                     |
| -------- | ---------------------------------------- | ---------------------------- |
| Backend  | FastAPI · Django · ASP.NET · Spring Boot | Based on language preference |
| Frontend | Next.js · React · Angular · Flutter      | Based on platform            |
| Database | DATABASE_STRUCTURE.md                    | Include only when explicitly selected as the schema owner |
| Security | SECURITY_LAYER.md                        | Always include this          |

**Common combinations:**

```
Web App (Python)  : FastAPI + Next.js + standalone Database + Security
Web App (Java)    : Spring Boot + Next.js + Flyway OR standalone Database + Security
Web App (C#)      : ASP.NET + Angular + EF migrations OR standalone Database + Security
Mobile App        : FastAPI + Flutter + standalone Database + Security
Full Python Stack : Django + React + Django migrations + Security
```

---

## STEP 2 — SET UP YOUR PROJECT FOLDER

```
my-project/
├── backend/                   ← your backend code goes here
├── frontend/                  ← your frontend code goes here
├── database/                  ← optional; only for standalone DB ownership
│
├── FASTAPI_ORM_STRUCTURE.md   ← drop here (or whichever backend you chose)
├── NEXTJS_FRONTEND_STRUCTURE.md ← drop here (or whichever frontend)
├── DATABASE_STRUCTURE.md      ← only when standalone DB ownership was selected
├── SECURITY_LAYER.md          ← always drop here
└── HOW_TO_USE.md              ← this file
```

Drop only the files you need. You don't need all 10 in one project.

**Existing frontend:** choose the target frontend file and use its **Mode B — Total Frontend Migration**. The source may use any framework. The agent converts the implementation and structure but must preserve the existing UI design, colors, logos, visible text, fonts, theme, layout, responsive behavior, interactions, and animations unless you explicitly request a design change.

---

## STEP 3 — THE MASTER PROMPT (copy this at the start of every chat)

Replace the placeholders with your actual file names:

```
Read the following files in my project root deeply and follow every instruction in all of them for all code you generate. These files are your single source of truth. No exceptions.

Files to read (omit the database file when backend-native migrations own the schema):
- FASTAPI_ORM_STRUCTURE.md       (backend architecture + code patterns)
- NEXTJS_FRONTEND_STRUCTURE.md   (frontend architecture + code patterns)
- DATABASE_STRUCTURE.md          (database schema + SQL standards)
- SECURITY_LAYER.md              (security layer — Traefik, TLS, auth, CSRF, headers)

After reading, summarize the applicable structure briefly, then continue with my current task. If I did not provide a task, ask for one concise task.
```

**This stack (FastAPI + Next.js + Database + Security):** copy the master prompt from `Skill/FASTAPI_NEXTJS_STACK.md` instead. It includes file order and the cross-product stop rule.

**Why mention a confirmation summary?**
It provides a quick check that the applicable files were processed. For a concrete coding request, keep it brief and continue working instead of pausing unnecessarily.

---

## STEP 4 — PROJECT SETUP ORDER (do this once per project)

Follow this exact sequence when starting a new project:

### Phase 1 — Database First (only in standalone database-owner mode)

```
1. Create database/ from DATABASE_STRUCTURE.md
2. Write schema/schemas/, schema/extensions/, schema/tables/{domain}/
3. Write matching indexes/, functions/, triggers/, rls/
4. Set DATABASE_URL in database/.env
5. Run: python scripts/db_diff.py          # preview drift — no writes
6. Run: python scripts/db_deploy.py        # inspect → apply → re-check → report
7. Confirm STATUS: ✓ DATABASE IS IN SYNC and read CHANGES THIS RUN
```

### Phase 2 — Backend Second

```
1. Run: uvicorn / dotnet new / mvn spring-boot:run to init project
2. Copy the relevant backend .md file to project root
3. Prompt: "Set up the base project structure from FASTAPI_ORM_STRUCTURE.md"
4. Agent generates: main.py, app/core/, app/modules/, app/api/, pyproject.toml
5. Run: uv sync
6. Map ORM models to the already-deployed database — the ORM never creates or alters tables
```

### Phase 3 — Security Third

```
1. Set up Traefik using docker-compose.yml from SECURITY_LAYER.md
2. Configure traefik/traefik.yml and traefik/dynamic.yml
3. Configure HttpOnly session/refresh cookies, CSRF protection, strict CORS, and rate limits
4. Keep every secret server-side; never put shared secrets in browser/mobile env files
5. Test: docker compose up -d
6. Verify: curl -I https://api.localhost/health (check TLS and security headers)
```

### Phase 4 — Frontend Last

```
1. Run: npx create-next-app / npm create vite / ng new / flutter create
2. Copy the relevant frontend .md file to project root
3. Prompt: "Set up the base project structure from NEXTJS_FRONTEND_STRUCTURE.md"
4. Agent generates: lib/, components/, hooks/, proxy.ts, tsconfig.json
5. Run: npm install
6. For Next.js set server-only BACKEND_API_URL; for SPA/mobile set the public proxy API URL
7. Run: npm run dev
```

---

## STEP 5 — DAILY DEVELOPMENT WORKFLOW

### Adding a New Feature (e.g., "Orders")

In standalone database-owner mode, follow database → backend → frontend. In backend-native mode, create and apply the framework migration before code that depends on the new schema:

```
DATABASE:
  1. Prompt: "Add an Orders feature following DATABASE_STRUCTURE.md"
     → Agent creates schema/tables/{domain}/orders.sql + indexes/ + triggers/ + rls/
  2. Run: python scripts/db_diff.py
  3. Run: python scripts/db_deploy.py
     → Inspect live DB, apply missing columns/types/views, re-check once, print report

BACKEND:
  4. Prompt: "Add Orders to the backend following FASTAPI_ORM_STRUCTURE.md"
     → Agent creates app/modules/orders/ (models, schemas, repository,
       service, router, exceptions), exports the model, updates api/v1/router.py

FRONTEND:
  5. Prompt: "Add Orders to the frontend following NEXTJS_FRONTEND_STRUCTURE.md"
     → Agent creates lib/types/order.types.ts, lib/api/endpoints.ts updates,
       lib/query/keys.ts updates, components/pages/orders/ full feature folder
```

### Prompts That Work Well

```
Good prompts:
  "Add a [Feature] feature following all the instruction files."
  "Convert this complete frontend to [Next.js / React / Angular / Flutter].
   Use Mode B. Preserve the UI and product identity exactly."
  "Generate the [layer] for [feature] — follow the patterns exactly."
  "Add [column] to [table] in database/schema and deploy with db_deploy.py."
  "Fix the [file] — it's not following the rules in the instruction file."

Bad prompts (too vague):
  "Make a user management page."    ← No reference to instruction files
  "Add authentication."             ← Agent will invent its own pattern
  "Create the database."            ← No structure specified
```

---

## STEP 6 — ENVIRONMENT VARIABLES REFERENCE

Every project needs these variables. Create them once, reuse across all files:

### Backend `.env`

```bash
# Core
PRODUCTION=false
PROJECT_NAME=MyApp

# Database
DATABASE_URL=postgres://appuser:password@127.0.0.1:5432/myapp
POSTGRES_SERVER=127.0.0.1
POSTGRES_USER=appuser
POSTGRES_PASSWORD=password
POSTGRES_DB=myapp

# Auth
SECRET_KEY=                        # openssl rand -hex 32
JWT_SECRET=                        # openssl rand -hex 32 (Spring Boot / Django)
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Security
# INTERNAL_SIGNING_KEYS_JSON=      # optional server-to-server/webhook keys only
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
ALLOWED_HOSTS=["localhost","127.0.0.1"]

# (Django specific)
DJANGO_SECRET_KEY=                 # openssl rand -hex 32

# (ASP.NET specific — use environment variables, NOT appsettings.json)
ConnectionStrings__Default=Host=127.0.0.1;Database=myapp;Username=appuser;Password=pass
Jwt__Secret=                       # same as JWT_SECRET above
```

### Frontend `.env.local` (Next.js / React)

```bash
BACKEND_API_URL=http://localhost:8000/api/v1        # Next.js server-only upstream
VITE_API_URL=http://localhost:8000/api/v1           # React SPA only
NEXT_PUBLIC_BACKEND_TYPE=fastapi                    # fastapi | aspnet | springboot
AUTH_URL=http://localhost:3000
AUTH_SECRET=                                        # openssl rand -base64 32
```

### Flutter `.env`

```bash
API_URL=http://localhost:8000/api/v1
BACKEND_TYPE=fastapi
ENVIRONMENT=development
```

### Generate All Secrets at Once

```bash
echo "SECRET_KEY=$(openssl rand -hex 32)"
echo "JWT_SECRET=$(openssl rand -hex 32)"
echo "AUTH_SECRET=$(openssl rand -base64 32)"
```

**CRITICAL:** never place a shared signing secret in a browser-exposed variable or Flutter asset. HMAC is optional and server-to-server only.

---

## STEP 7 — FILE-BY-FILE QUICK REFERENCE

### `DATABASE_STRUCTURE.md`

**Purpose:** Standalone PostgreSQL project — desired schema + reconcile engine.
**Use when:** Starting a project, adding tables, changing columns/types/views.
**Key command:**

```bash
python scripts/db_diff.py      # inspect live DB, print plan — no writes
python scripts/db_deploy.py    # inspect → apply → re-check once → report
python scripts/db_check.py     # exit 0 only if already in sync
```

**Folder to create:** `database/schema/` (source of truth), `database/engine/`, `database/commands/`
**Remember:** Push `database/` first. Backend models match the live schema after deploy.

---

### `FASTAPI_ORM_STRUCTURE.md`

**Purpose:** Python FastAPI + SQLAlchemy async backend (modular monolith).
**Use when:** Building REST API with Python.
**Key pattern:** `modules/{feature}/models → schemas → repository → service → router`
**Remember:**

- One package per feature under `app/modules/` — never a global `crud/` or `services/` tree
- ORM **uses** the live DB only — never `create_all`, never Alembic; schema is `database/` + `db_deploy.py`
- `settings.PRODUCTION=true` hides `/docs`
- All middleware registered in `app/middleware/__init__.py`

---

### `DJANGO_STRUCTURE.md`

**Purpose:** Python Django + DRF backend.
**Use when:** Building REST API with Django.
**Key pattern:** `models.py → serializers.py → services.py → views.py → urls.py`
**Remember:**

- Service functions use keyword-only args: `def create_user(*, data:)`
- Input serializers = `serializers.Serializer`, NOT `ModelSerializer`
- Run `python manage.py makemigrations && migrate` after model changes

---

### `ASPNET_STRUCTURE.md`

**Purpose:** C# ASP.NET Core 10 LTS backend.
**Use when:** Building REST API with .NET.
**Key pattern:** `Models/ → DTOs/ → Repositories/ → Services/ → Controllers/`
**Remember:**

- Use environment variables with `__` separator for config overrides
- `CancellationToken` on every async method
- `SaveChangesAsync` only in repositories, never services

---

### `SPRINGBOOT_STRUCTURE.md`

**Purpose:** Java 25 LTS + Spring Boot 4.1 backend.
**Use when:** Building REST API with Java.
**Key pattern:** `domain/ → dto/ → repository/ → service/ → controller/`
**Remember:**

- `@Transactional(readOnly=true)` on all read operations
- Constructor injection only — never `@Autowired` on fields
- MapStruct for all entity↔DTO mapping — never manual
- Run `mvn spring-boot:run` to start

---

### `NEXTJS_FRONTEND_STRUCTURE.md`

**Purpose:** Next.js 16.4 App Router frontend.
**Use when:** Building web app with SSR, SEO requirements.
**Key pattern:** `app/page.tsx → components/pages/{feature}/ → lib/api/`
**Remember:**

- `page.tsx` = max 8 lines — one import, one return
- Default = Server Component. `"use client"` only when needed
- `proxy.ts` handles request-time auth redirects

---

### `REACTJS_FRONTEND_STRUCTURE.md`

**Purpose:** React 19 + Vite SPA frontend.
**Use when:** Building SPA without SSR needs.
**Key pattern:** `router/ → pages/ → components/pages/{feature}/ → lib/api/`
**Remember:**

- Token stored in memory (`tokenStore`) — never localStorage
- `ProtectedRoute` component handles auth guard
- Vite dev proxy hides backend port in development

---

### `ANGULARJS_FRONTEND_STRUCTURE.md`

**Purpose:** Angular 22 standalone components frontend.
**Use when:** Enterprise Angular projects.
**Key pattern:** `features/{feature}/ → UsersApiService → component class fields`
**Remember:**

- `injectQuery` must be a **class field** — never inside a method
- Every component is `standalone: true` — no NgModule
- Use `@if`, `@for` — never `*ngIf`, `*ngFor`

---

### `FLUTTER_STRUCTURE.md`

**Purpose:** Flutter multi-platform (iOS, Android, Desktop, Web).
**Use when:** Building native mobile or desktop apps.
**Key pattern:** `features/{feature}/data/ → providers/ → screens/`
**Remember:**

- Run `dart run build_runner build` after every `@freezed` or `@riverpod` change
- Token stored in `flutter_secure_storage` — never `SharedPreferences`
- `GoRouter` for navigation — never `Navigator.push()`
- Adaptive layout: mobile=BottomNav, tablet=Rail, desktop=Sidebar

---

### `SECURITY_LAYER.md`

**Purpose:** Full security layer — Traefik + TLS + secure auth/cookies + headers.
**Use when:** Always. Every project.
**Key pattern:** Browser → Traefik → Backend (backend IP never exposed)
**Remember:**

- `acme.json` must be `chmod 600`
- Shared secrets stay server-side; browser/mobile clients use sessions, short-lived tokens, or OAuth PKCE
- Backend binds to `0.0.0.0` inside Docker (safe — no published ports), `127.0.0.1` on bare metal
- Auth routes (`/api/v1/auth/*`) get stricter rate limiting: 10 req/min

---

## STEP 8 — WHEN SOMETHING GOES WRONG

Run the repository guard first:

```bash
python scripts/validate_library.py
```

It checks Markdown fences, required framework/security markers, and known stale or unsafe patterns before the instruction files are copied into another project.

### Agent ignores the instruction file

```
Re-prompt: "Stop. Re-read [FILENAME] from the project root completely.
Your last response did not follow the [specific rule].
Quote the rule from the file, then redo the task correctly."
```

### Agent generates the wrong pattern

```
Re-prompt: "This is wrong. The instruction file says [paste exact rule].
Regenerate following that rule exactly."
```

### Agent drifts after many messages

```
Re-prompt: "Re-read all instruction files. Confirm by summarizing the
key rules for [backend/frontend/database/security]. Then continue."
```

---

## STEP 9 — PRODUCTION DEPLOYMENT CHECKLIST

Before going live, verify all of these:

```
Database:
  [ ] python scripts/db_deploy.py against production (migration role)
  [ ] Report says STATUS: ✓ DATABASE IS IN SYNC
  [ ] CHANGES THIS RUN reviewed — no unexpected drops
  [ ] Extensions installed by superuser / migration role (not app user)
  [ ] RLS enabled on tenant-owned tables

Backend:
  [ ] PRODUCTION=true (FastAPI/Django) / ASPNETCORE_ENVIRONMENT=Production
  [ ] /docs and /openapi.json disabled
  [ ] CORS origins set to real domain names (not localhost)
  [ ] No shared secret is exposed to browser/mobile code
  [ ] JWT secret is 32+ chars randomly generated
  [ ] Error responses show no stack traces

Frontend:
  [ ] Next.js BACKEND_API_URL is server-only; SPA/mobile API URLs point to the HTTPS proxy
  [ ] NEXT_PUBLIC_BACKEND_TYPE set correctly
  [ ] Access tokens are not persisted in localStorage/sessionStorage
  [ ] No console.log in production code

Security (Traefik):
  [ ] acme.json has chmod 600
  [ ] api.dashboard: false in traefik.yml
  [ ] TLS 1.2+ only (modern cipher suite)
  [ ] All backend containers use expose: not ports:
  [ ] Rate limiting active (dynamic.yml)
  [ ] Auth endpoints have stricter rate limit (10/min)

Secrets:
  [ ] .env never committed to git
  [ ] .env.example committed with empty values
  [ ] All secrets generated with openssl rand
  [ ] No hardcoded secrets in any source file
```

---

## COMPLETE STACK EXAMPLE — FASTAPI + NEXT.JS

Here is what a complete `docker-compose.yml` looks like with all pieces wired together:

```yaml
services:
  # ── Database ────────────────────────────────────────────────────────
  postgres:
    image: postgres:18-alpine
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: changeme
      POSTGRES_DB: myapp
    expose:
      - "5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks: [proxy]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser"]
      interval: 10s
      retries: 5

  # ── Backend ─────────────────────────────────────────────────────────
  backend:
    build: ./backend
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    env_file: ./backend/.env
    expose: ["8000"]
    depends_on:
      postgres: { condition: service_healthy }
    networks: [proxy]
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`api.yourdomain.com`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
      - "traefik.http.routers.backend.middlewares=security-headers@file,rate-limit@file,body-limit@file,compress@file"
      - "traefik.http.services.backend.loadbalancer.server.port=8000"

  # ── Frontend ─────────────────────────────────────────────────────────
  frontend:
    build: ./frontend
    env_file: ./frontend/.env.local
    expose: ["3000"]
    networks: [proxy]
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`app.yourdomain.com`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
      - "traefik.http.routers.frontend.middlewares=security-headers@file,compress@file"
      - "traefik.http.services.frontend.loadbalancer.server.port=3000"

  # ── Traefik ──────────────────────────────────────────────────────────
  traefik:
    image: traefik:v3.7.15
    ports: ["80:80", "443:443"]
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik/traefik.yml:/etc/traefik/traefik.yml:ro
      - ./traefik/dynamic.yml:/etc/traefik/dynamic.yml:ro
      - ./traefik/acme.json:/letsencrypt/acme.json
    security_opt: [no-new-privileges:true]
    networks: [proxy]
    labels:
      - "traefik.enable=false"

volumes:
  postgres-data:

networks:
  proxy:
    driver: bridge
```

---

## SUMMARY — THE 3 THINGS TO REMEMBER

```
1. ALWAYS start a chat by referencing the instruction files.
   The agent WILL drift without them.

2. NEVER place authentication or signing secrets in browser/mobile builds.
   Use HttpOnly sessions, short-lived tokens, CSRF protection, or OAuth PKCE.

3. ALWAYS deploy database/ first (db_diff then db_deploy).
   Backend models change only after STATUS: ✓ DATABASE IS IN SYNC.
```

---

_Library version: 2.0 | Fixes applied: 20 | Files: 10 + this guide_
_FastAPI · Django · ASP.NET Core · Spring Boot · Next.js · React · Angular · Flutter · PostgreSQL · Traefik_

---

## Copyright

© 2026 **Udhayaboopathi V**. Released under the repository's MIT License.

- Author:  Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub:  [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
