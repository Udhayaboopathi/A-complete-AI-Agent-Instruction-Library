---
name: fastapi-nextjs-stack
description: >-
  Orchestrates the FastAPI + Next.js + PostgreSQL + Traefik stack using
  FASTAPI_NEXTJS_STACK.md and the four layer instruction files. Use when the
  user mentions this stack, FASTAPI_NEXTJS_STACK, Skill folder, database deploy,
  FastAPI modules, Next.js App Router, SECURITY_LAYER, or starting a chat on
  this product.
---

# FastAPI + Next.js Stack

Read [Skill/FASTAPI_NEXTJS_STACK.md](../../../Skill/FASTAPI_NEXTJS_STACK.md) first and follow it exactly.

## Required reads (this order)

1. `Skill/FASTAPI_NEXTJS_STACK.md`
2. `Database/DATABASE_STRUCTURE.md`
3. `Backend/FASTAPI_ORM_STRUCTURE.md`
4. `Frontend/NEXTJS_FRONTEND_STRUCTURE.md`
5. `Security/SECURITY_LAYER.md`

Confirm in four sentences (database deploy, backend modules, frontend feature folder, signing secret), then wait.

## Work order

`database/` (diff → deploy → in sync) → `backend/` → security if public → `frontend/`

## Cross-product stop

If a change would affect another product or another SaaS (shared DB, API, auth, tenants), stop and tell the user before editing or deploying. Use the `CROSS-PRODUCT IMPACT` block in `FASTAPI_NEXTJS_STACK.md`.
