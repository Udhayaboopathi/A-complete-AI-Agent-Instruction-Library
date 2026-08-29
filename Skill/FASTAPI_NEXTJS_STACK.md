# AGENT INSTRUCTIONS — FastAPI + Next.js Stack

> **File name:** `FASTAPI_NEXTJS_STACK.md`
> This is the only stack file for this product. It does not replace the four source files. It tells the agent **which files to read, in what order, and how to follow them**.

---

## YOUR IDENTITY

You are the stack orchestrator for **one** product built on this stack only:

| Layer | File | Role |
| --- | --- | --- |
| Database | `Database/DATABASE_STRUCTURE.md` | Desired schema + inspect → diff → deploy |
| Backend | `Backend/FASTAPI_ORM_STRUCTURE.md` | FastAPI modular monolith — ORM uses DB, never creates/alters it |
| Frontend | `Frontend/NEXTJS_FRONTEND_STRUCTURE.md` | Next.js 15 App Router |
| Security | `Security/SECURITY_LAYER.md` | Traefik, HMAC, TLS, headers |

Do not invent a fifth architecture. Do not switch to Django, ASP.NET, Spring Boot, React Vite, Angular, or Flutter unless the user explicitly changes stack.

You have no creative freedom over folder layout, deploy order, or security defaults. You have creative freedom only over product business logic **inside** those files.

---

## THE MASTER PROMPT

Copy this at the start of every new chat. Do not shorten it.

```
Read these files deeply. They are the single source of truth. Follow every instruction in all of them for all code you generate. No exceptions.

Files to read — in this order:
1. Skill/FASTAPI_NEXTJS_STACK.md
2. Database/DATABASE_STRUCTURE.md
3. Backend/FASTAPI_ORM_STRUCTURE.md
4. Frontend/NEXTJS_FRONTEND_STRUCTURE.md
5. Security/SECURITY_LAYER.md

After reading, confirm in four sentences:
- database/ folder layout + deploy command
- backend modules/ layout
- frontend feature folder rule
- security: Traefik in front, REQUEST_SIGNING_SECRET same on both sides

Then wait for my first task.

If any change you are about to make would affect another product or another SaaS that shares this database, API, auth, or tenants — stop and tell me before you edit or deploy. Do not apply that change silently.
```

---

## HOW TO USE THIS FILE

### In a real product repo

```
my-project/
├── database/
├── backend/
├── frontend/
├── FASTAPI_NEXTJS_STACK.md          ← this file (or keep it under Skill/)
├── DATABASE_STRUCTURE.md
├── FASTAPI_ORM_STRUCTURE.md
├── NEXTJS_FRONTEND_STRUCTURE.md
└── SECURITY_LAYER.md
```

Drop **only** these four layer files plus this stack file. You do not need Django, ASP.NET, Spring Boot, React, Angular, or Flutter files for this stack.

### In Cursor

Start the chat with the master prompt above, or say:

```
Use FASTAPI_NEXTJS_STACK. Follow the four layer files. Wait after you confirm.
```

The agent must finish the four-sentence confirmation **before** writing code.

---

## HOW THE AGENT FOLLOWS THESE FILES

1. **This file first** — stack, order, cross-product rule.
2. **Then the layer file that owns the task.** A column change is `DATABASE_STRUCTURE.md`. A route is `FASTAPI_ORM_STRUCTURE.md`. A page is `NEXTJS_FRONTEND_STRUCTURE.md`. Headers, HMAC, Traefik is `SECURITY_LAYER.md`.
3. **If two layers are involved, follow both.** Example: new table → database file, then backend `modules/{feature}/`, then frontend feature folder, then security if the route is public.
4. **Never override a layer file** with training-data defaults (`app/crud/`, `DataStructure/`, `DB_Load.py`, Pages Router, `localStorage` tokens).
5. **If a layer file and this file disagree,** the layer file wins on structure. This file wins on **order of work** and **cross-product stop**.

---

## BUILD AND PUSH ORDER

Always this sequence. Never backend-first. Never frontend-first.

```
1. database/     edit schema/ → db_diff.py → db_deploy.py
                 STATUS must be: ✓ DATABASE IS IN SYNC
2. backend/      modules match the live schema
3. security      Traefik / HMAC / env secrets if the change is public
4. frontend/     types, endpoints, feature UI
```

```
Push order:  database/  →  backend/  →  frontend/
```

Daily feature (example: Orders):

```
DATABASE   schema/tables/{domain}/orders.sql + indexes + triggers + rls
           python scripts/db_diff.py
           python scripts/db_deploy.py
BACKEND    app/modules/orders/  (models, schemas, repository, service, router, exceptions)
FRONTEND   components/pages/orders/ + lib/types + lib/api
SECURITY   new public route gets headers, signing, rate limit
```

---

## WHAT EACH FILE FORBIDS (DO NOT DRIFT)

| File | Do not generate |
| --- | --- |
| Database | `DataStructure/`, `DB_Load.py`, blind `CREATE IF NOT EXISTS` as deploy |
| Backend | `app/models/`, `app/crud/`, `app/services/`, `app/api/v1/endpoints/`, Alembic, `create_all` |
| Frontend | Pages Router, fat `page.tsx`, `localStorage` tokens |
| Security | Published backend ports, `/docs` in production, mismatched signing secrets |

---

## CROSS-PRODUCT / OTHER SAAS — STOP AND TELL ME

This stack may share a database, API, auth, or tenant with **another product or another SaaS**.

Before you edit or deploy, ask: **will this change affect another product or another SaaS?**

Affect means any of these:

- shared table, column, type, view, function, RLS, or role
- shared `/api/v1` contract (path, field, status code, auth)
- shared JWT, `REQUEST_SIGNING_SECRET`, or tenant id
- shared Traefik host, CORS origin, or rate-limit rule
- a migration or type change other apps still read as the old shape

**If yes — stop. Do not edit. Do not run `db_deploy.py`. Tell me:**

```
CROSS-PRODUCT IMPACT — waiting for you

Change     : [what]
Would hit  : [other product / other SaaS / shared object]
Risk       : [data, API break, auth, tenant isolation]
Need from you: approve, isolate the change, or split the schema
```

Do not apply a “small” column rename, type narrow, or auth change because it looks local. Shared identity, billing, and tenant tables are assumed shared until I say they are not.

If you are sure the change is isolated to this product, say so in one line and continue.

---

## PRE-COMPLETION CHECKLIST

```
[ ] Master prompt files were followed — no extra stack invented
[ ] Database deployed first when schema changed (diff → deploy → in sync)
[ ] Backend is modules/{feature}/ — not crud/services leftovers
[ ] Frontend change lives in the feature folder — page.tsx stays thin
[ ] REQUEST_SIGNING_SECRET matches backend and frontend
[ ] Production: docs off, backend not published, security headers on
[ ] If another product or SaaS could be affected — I stopped and told you
```

---

_Stack: PostgreSQL 16 · FastAPI 0.115+ · Next.js 15 · Traefik · HMAC | Skill v1.0_

---

## Copyright

© 2026 **Udhayaboopathi V**. All rights reserved.

- Author: Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub: [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
