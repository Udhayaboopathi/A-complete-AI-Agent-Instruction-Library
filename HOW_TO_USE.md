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
  NEXTJS_FRONTEND_STRUCTURE.md  → Next.js 15 frontend (SSR + App Router)
  REACTJS_FRONTEND_STRUCTURE.md → React + Vite SPA frontend
  ANGULARJS_FRONTEND_STRUCTURE.md → Angular 18+ frontend
  FLUTTER_STRUCTURE.md          → Flutter multi-platform (Mobile + Desktop + Web)

Database/
  DATABASE_STRUCTURE.md         → PostgreSQL schema management

Security/
  SECURITY_LAYER.md             → Full-stack security (Traefik + HMAC + headers)
```

---

## STEP 1 — PICK YOUR STACK

Choose one file from each category based on your project:

| Category | Options                                  | Pick one                     |
| -------- | ---------------------------------------- | ---------------------------- |
| Backend  | FastAPI · Django · ASP.NET · Spring Boot | Based on language preference |
| Frontend | Next.js · React · Angular · Flutter      | Based on platform            |
| Database | DATABASE_STRUCTURE.md                    | Always include this          |
| Security | SECURITY_LAYER.md                        | Always include this          |

**Common combinations:**

```
Web App (Python)  : FastAPI + Next.js + Database + Security
Web App (Java)    : Spring Boot + Next.js + Database + Security
Web App (C#)      : ASP.NET + Angular + Database + Security
Mobile App        : FastAPI + Flutter + Database + Security
Full Python Stack : Django + React + Database + Security
```

---

## STEP 2 — SET UP YOUR PROJECT FOLDER

```
my-project/
├── backend/                   ← your backend code goes here
├── frontend/                  ← your frontend code goes here
├── DataStructure/             ← database SQL files go here
│
├── FASTAPI_ORM_STRUCTURE.md   ← drop here (or whichever backend you chose)
├── NEXTJS_FRONTEND_STRUCTURE.md ← drop here (or whichever frontend)
├── DATABASE_STRUCTURE.md      ← always drop here
├── SECURITY_LAYER.md          ← always drop here
└── HOW_TO_USE.md              ← this file
```

Drop only the files you need. You don't need all 10 in one project.

---

## STEP 3 — THE MASTER PROMPT (copy this at the start of every chat)

Replace the placeholders with your actual file names:

```
Read the following files in my project root deeply and follow every instruction in all of them for all code you generate. These files are your single source of truth. No exceptions.

Files to read:
- FASTAPI_ORM_STRUCTURE.md       (backend architecture + code patterns)
- NEXTJS_FRONTEND_STRUCTURE.md   (frontend architecture + code patterns)
- DATABASE_STRUCTURE.md          (database schema + SQL standards)
- SECURITY_LAYER.md              (security layer — Traefik, HMAC, headers)

After reading, confirm you understand by summarizing the folder structure for each file in one sentence each. Then wait for my first task.
```

**Why ask for a confirmation summary?**
It forces the agent to process all 4 files before generating any code. Without this, agents sometimes skip reading and default to their training data.

---

## STEP 4 — PROJECT SETUP ORDER (do this once per project)

Follow this exact sequence when starting a new project:

### Phase 1 — Database First

```
1. Create DataStructure/ folder
2. Write Tables/01_users.sql (use DATABASE_STRUCTURE.md as template)
3. Write Tables/02_your_main_entity.sql
4. Write Functions/01_update_timestamp.sql
5. Write Triggers/01_users_updated_at.sql
6. Write Indexing/01_users_indexes.sql
7. Run: python DB_Load.py
8. Verify schema.sql and schema.md were generated
```

### Phase 2 — Backend Second

```
1. Run: uvicorn / dotnet new / mvn spring-boot:run to init project
2. Copy the relevant backend .md file to project root
3. Prompt: "Set up the base project structure from FASTAPI_ORM_STRUCTURE.md"
4. Agent generates: main.py, config.py, db/, core/, alembic/, requirements.txt
5. Run: pip install -r requirements.txt
6. Run: alembic init alembic
7. Configure alembic/env.py (agent does this with the instruction file)
8. Run: alembic revision --autogenerate -m "initial"
9. Run: alembic upgrade head
```

### Phase 3 — Security Third

```
1. Set up Traefik using docker-compose.yml from SECURITY_LAYER.md
2. Configure traefik/traefik.yml and traefik/dynamic.yml
3. Add REQUEST_SIGNING_SECRET to .env (backend) and .env.local (frontend)
4. Generate secret: openssl rand -hex 32
5. Use SAME secret in both backend and frontend .env files
6. Test: docker compose up -d
7. Verify: curl -I https://api.localhost/health (check security headers)
```

### Phase 4 — Frontend Last

```
1. Run: npx create-next-app / npm create vite / ng new / flutter create
2. Copy the relevant frontend .md file to project root
3. Prompt: "Set up the base project structure from NEXTJS_FRONTEND_STRUCTURE.md"
4. Agent generates: lib/, components/, hooks/, middleware.ts, tsconfig.json
5. Run: npm install
6. Set NEXT_PUBLIC_API_URL in .env.local to Traefik proxy URL
7. Run: npm run dev
```

---

## STEP 5 — DAILY DEVELOPMENT WORKFLOW

### Adding a New Feature (e.g., "Orders")

Always follow this order — backend before frontend:

```
BACKEND:
  1. Prompt: "Add an Orders feature following DATABASE_STRUCTURE.md"
     → Agent creates Tables/03_orders.sql + Indexing/ + Triggers/
  2. Run: python DB_Load.py --file Tables/03_orders.sql
  3. Prompt: "Add Orders to the backend following FASTAPI_ORM_STRUCTURE.md"
     → Agent creates models/order.py, schemas/order.py, crud/order.py,
       services/order.py, api/v1/endpoints/order.py, updates router.py

FRONTEND:
  4. Prompt: "Add Orders to the frontend following NEXTJS_FRONTEND_STRUCTURE.md"
     → Agent creates lib/types/order.types.ts, lib/api/endpoints.ts updates,
       lib/query/keys.ts updates, components/pages/orders/ full feature folder
```

### Prompts That Work Well

```
Good prompts:
  "Add a [Feature] feature following all the instruction files."
  "Generate the [layer] for [feature] — follow the patterns exactly."
  "Create a migration for adding [column] to [table] table."
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
REQUEST_SIGNING_SECRET=            # openssl rand -hex 32  ← SAME VALUE AS FRONTEND
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
ALLOWED_HOSTS=["localhost","127.0.0.1"]

# (Django specific)
DJANGO_SECRET_KEY=                 # openssl rand -hex 32

# (ASP.NET specific — use environment variables, NOT appsettings.json)
ConnectionStrings__Default=Host=127.0.0.1;Database=myapp;Username=appuser;Password=pass
Jwt__Secret=                       # same as JWT_SECRET above
Security__SigningSecret=           # same as REQUEST_SIGNING_SECRET

# (Spring Boot specific)
APP_SIGNING_SECRET=                # same as REQUEST_SIGNING_SECRET
```

### Frontend `.env.local` (Next.js / React)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1   # dev: backend URL
NEXT_PUBLIC_BACKEND_TYPE=fastapi                    # fastapi | aspnet | springboot
NEXT_PUBLIC_REQUEST_SIGNING_SECRET=                 # SAME VALUE AS BACKEND
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=                                    # openssl rand -base64 32
```

### Flutter `.env`

```bash
API_URL=http://localhost:8000/api/v1
BACKEND_TYPE=fastapi
REQUEST_SIGNING_SECRET=                             # SAME VALUE AS BACKEND
ENVIRONMENT=development
```

### Generate All Secrets at Once

```bash
echo "SECRET_KEY=$(openssl rand -hex 32)"
echo "JWT_SECRET=$(openssl rand -hex 32)"
echo "REQUEST_SIGNING_SECRET=$(openssl rand -hex 32)"
echo "NEXTAUTH_SECRET=$(openssl rand -base64 32)"
```

**CRITICAL:** `REQUEST_SIGNING_SECRET` must be the SAME value in backend `.env` and frontend `.env.local`.

---

## STEP 7 — FILE-BY-FILE QUICK REFERENCE

### `DATABASE_STRUCTURE.md`

**Purpose:** PostgreSQL schema management with numbered SQL files.
**Use when:** Starting a project, adding tables, adding indexes, changing schema.
**Key command:**

```bash
python DB_Load.py              # full setup
python DB_Load.py --dry-run    # preview
python DB_Load.py --schema-only  # regenerate schema.sql + schema.md
```

**Folder to create:** `DataStructure/Tables/`, `Functions/`, `Triggers/`, `Indexing/`, `Views/`

---

### `FASTAPI_ORM_STRUCTURE.md`

**Purpose:** Python FastAPI + SQLAlchemy async backend.
**Use when:** Building REST API with Python.
**Key pattern:** `models/ → schemas/ → crud/ → services/ → api/endpoints/`
**Remember:**

- Run `alembic revision --autogenerate` after every model change
- `settings.PRODUCTION=true` hides `/docs`
- All middleware registered in `core/middleware/__init__.py`

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

**Purpose:** C# ASP.NET Core 9 backend.
**Use when:** Building REST API with .NET.
**Key pattern:** `Models/ → DTOs/ → Repositories/ → Services/ → Controllers/`
**Remember:**

- Use environment variables with `__` separator for config overrides
- `CancellationToken` on every async method
- `SaveChangesAsync` only in repositories, never services

---

### `SPRINGBOOT_STRUCTURE.md`

**Purpose:** Java 21 Spring Boot backend.
**Use when:** Building REST API with Java.
**Key pattern:** `domain/ → dto/ → repository/ → service/ → controller/`
**Remember:**

- `@Transactional(readOnly=true)` on all read operations
- Constructor injection only — never `@Autowired` on fields
- MapStruct for all entity↔DTO mapping — never manual
- Run `mvn spring-boot:run` to start

---

### `NEXTJS_FRONTEND_STRUCTURE.md`

**Purpose:** Next.js 15 App Router frontend.
**Use when:** Building web app with SSR, SEO requirements.
**Key pattern:** `app/page.tsx → components/pages/{feature}/ → lib/api/`
**Remember:**

- `page.tsx` = max 8 lines — one import, one return
- Default = Server Component. `"use client"` only when needed
- `middleware.ts` handles auth redirect at Edge (< 1ms)

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

**Purpose:** Angular 18+ standalone components frontend.
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

**Purpose:** Full security layer — Traefik + HMAC + headers.
**Use when:** Always. Every project.
**Key pattern:** Browser → Traefik → Backend (backend IP never exposed)
**Remember:**

- `acme.json` must be `chmod 600`
- `REQUEST_SIGNING_SECRET` must be identical in backend and frontend `.env`
- Backend binds to `0.0.0.0` inside Docker (safe — no published ports), `127.0.0.1` on bare metal
- Auth routes (`/api/v1/auth/*`) get stricter rate limiting: 10 req/min

---

## STEP 8 — WHEN SOMETHING GOES WRONG

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
  [ ] All migrations applied: alembic upgrade head / flyway migrate / dotnet ef database update
  [ ] Extensions installed by superuser (not app user)
  [ ] audit_logs table exists
  [ ] All indexes created (run Indexing/ files)

Backend:
  [ ] PRODUCTION=true (FastAPI/Django) / ASPNETCORE_ENVIRONMENT=Production
  [ ] /docs and /openapi.json disabled
  [ ] CORS origins set to real domain names (not localhost)
  [ ] REQUEST_SIGNING_SECRET set (same as frontend)
  [ ] JWT secret is 32+ chars randomly generated
  [ ] Error responses show no stack traces

Frontend:
  [ ] NEXT_PUBLIC_API_URL points to https:// proxy URL (not raw IP)
  [ ] NEXT_PUBLIC_BACKEND_TYPE set correctly
  [ ] REQUEST_SIGNING_SECRET matches backend
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
    image: postgres:16-alpine
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
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
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
    image: traefik:v3.0
    ports: ["80:80", "443:443"]
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik/traefik.yml:/etc/traefik/traefik.yml:ro
      - ./traefik/dynamic.yml:/etc/traefik/dynamic.yml:ro
      - traefik-certs:/letsencrypt
    security_opt: [no-new-privileges:true]
    networks: [proxy]
    labels:
      - "traefik.enable=false"

volumes:
  postgres-data:
  traefik-certs:

networks:
  proxy:
    driver: bridge
```

---

## SUMMARY — THE 3 THINGS TO REMEMBER

```
1. ALWAYS start a chat by referencing the instruction files.
   The agent WILL drift without them.

2. ALWAYS set REQUEST_SIGNING_SECRET to the same value
   in backend .env AND frontend .env.local.

3. ALWAYS run python DB_Load.py --schema-only after
   any database change to keep schema.sql and schema.md in sync.
```

---

_Library version: 2.0 | Fixes applied: 20 | Files: 10 + this guide_
_FastAPI · Django · ASP.NET Core · Spring Boot · Next.js · React · Angular · Flutter · PostgreSQL · Traefik_

---

## Copyright

© 2026 **Udhayaboopathi V**. All rights reserved.

- Author:  Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub:  [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
