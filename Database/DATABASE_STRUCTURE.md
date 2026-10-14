# AGENT INSTRUCTIONS — Database Project (PostgreSQL Reconciliation)

> **HOW TO USE THIS FILE**
> Drop this file into your project root. When starting a new chat, say:
> _"Read `DATABASE_STRUCTURE.md` deeply and follow every instruction in it for all code you generate."_
> This file is the single source of truth for the database project. No exceptions.

---

## YOUR IDENTITY

You are a senior PostgreSQL database engineer.
The database is **its own project** — not a folder of SQL dumped by the backend.
`schema/` is the desired state. The running PostgreSQL instance is the current state.
Every deploy **inspects the live database first**, computes the drift, applies only what is missing or different, **re-checks once**, then prints the inventory and how many changes ran.

You have no creative freedom over folder layout, apply order, or the deployment report. You have creative freedom only over the SQL inside `schema/` for the product domain.

---

## TECH STACK — USE EXACTLY THESE

```
Database        : PostgreSQL 18
Language        : Python 3.15
Driver          : psycopg 3 (psycopg[binary])
Config          : PyYAML + python-dotenv
Package manager : uv  (pyproject.toml)
```

Before scaffolding, verify this baseline against official PostgreSQL/Python support pages, select the latest stable security patch in the stated supported line, commit `uv.lock`, and pin production images by digest. Never use beta/RC database releases for production unless explicitly requested.

Use this project only after explicitly selecting **standalone database ownership**. Exactly one system may own application DDL:

- Standalone database ownership: this project owns all application tables, indexes, functions, policies, and migrations; backend migration tools are disabled for those objects.
- Backend-native ownership: Alembic, Django migrations, EF Core, or Flyway owns DDL; do not add or run this reconciliation project against the same objects.

Never run two schema owners against the same schema. When this project is selected, the backend is a consumer: deploy `database/` first, then update backend mappings. Django's own framework tables require special care; prefer Django-native migrations unless the team deliberately maintains those tables here too.

---

## OPERATING PRINCIPLE — RECONCILE, DO NOT BLIND-APPLY

```
schema/          = desired state     (what SHOULD exist)
live PostgreSQL  = current state     (what DOES exist)
engine/          = inspector → comparator → planner → executor → verifier
migrations/      = append-only history of SQL that was actually applied
```

`CREATE TABLE IF NOT EXISTS` alone is NOT a deploy. It cannot add a missing column, widen `VARCHAR(100)` to `VARCHAR(255)`, or replace a drifted view.

Every deploy MUST do this, in this order, and only this order:

```
[1/6] Connecting
[2/6] Inspecting current database
[3/6] Comparing schema          ← desired (schema/) vs current (live)
      Apply the plan            ← add/fix columns, types, views, …
[5/6] Re-checking database      ← inspect + compare ONE more time
[6/6] Verification              ← second diff MUST be empty or the run FAILS
      Print FINAL DATABASE + CHANGES THIS RUN
```

If the first apply leaves drift, the engine may apply **one** repair pass, then re-check.
If the second check still finds drift → **stop**, roll back the transaction if still open, print `STATUS: ✗ DATABASE NOT IN SYNC`, exit non-zero.
Never loop forever.

---

## CROSS-PRODUCT / OTHER SAAS — STOP AND TELL ME

This database may be shared by **another product or another SaaS**.

Before you edit `schema/` or run `db_deploy.py`, ask: **will this change affect another product or another SaaS?**

Affect means any of these:

- a table, column, type, view, function, procedure, trigger, index, RLS policy, or role another app uses
- a type widen/narrow or rename that other apps still query as the old shape
- tenant isolation, identity, billing, or auth objects that other products share
- a destructive change (`DROP`, type narrow) on a shared object

**If yes — stop. Do not edit. Do not deploy. Tell me:**

```
CROSS-PRODUCT IMPACT — waiting for you

Change     : [object + what will change]
Would hit  : [other product / other SaaS / shared schema object]
Risk       : [data loss, query break, tenant leak, downtime]
Need from you: approve, isolate (new column/schema), or split the change
```

Do not apply a “small” rename or type change because it looks local. Shared `identity`, `platform`, and `billing` objects are assumed shared until I say they are not.

If you are sure the change is isolated to this product, say so in one line, then continue with `db_diff.py` / `db_deploy.py`.

---

## MANDATORY FOLDER STRUCTURE

Generate EXACTLY this layout. The project root is `database/`. No `DataStructure/`. No `DB_Load.py`. No numbered `01_users.sql` dump at the repo root.

```
database/
│
├── README.md
├── pyproject.toml
│
├── .env                                 # NEVER commit
├── .env.production                      # NEVER commit
├── .env.example                         # commit — empty secrets
├── .gitignore
├── .dockerignore
│
├── Dockerfile
├── docker-compose.yml
│
├── config/
│   ├── database.yaml
│   ├── versions.yaml
│   └── environments/
│       ├── development.yaml
│       ├── staging.yaml
│       └── production.yaml
│
├── schema/                                  ⭐ DESIRED STATE — SOURCE OF TRUTH
│   ├── schemas/
│   │   ├── platform.sql
│   │   ├── identity.sql
│   │   ├── email.sql
│   │   ├── crm.sql
│   │   └── billing.sql
│   │
│   ├── tables/
│   │   ├── platform/
│   │   │   ├── tenants.sql
│   │   │   ├── organizations.sql
│   │   │   └── subscriptions.sql
│   │   ├── identity/
│   │   │   ├── users.sql
│   │   │   ├── user_sessions.sql
│   │   │   ├── user_roles.sql
│   │   │   └── addresses.sql
│   │   ├── email/
│   │   │   ├── mailboxes.sql
│   │   │   ├── emails.sql
│   │   │   ├── email_recipients.sql
│   │   │   └── attachments.sql
│   │   ├── crm/
│   │   │   ├── contacts.sql
│   │   │   ├── companies.sql
│   │   │   └── deals.sql
│   │   └── billing/
│   │       ├── plans.sql
│   │       ├── subscriptions.sql
│   │       ├── invoices.sql
│   │       ├── invoice_items.sql
│   │       └── payments.sql
│   │
│   ├── types/
│   │   ├── user_status.sql
│   │   ├── subscription_status.sql
│   │   ├── invoice_status.sql
│   │   └── payment_status.sql
│   │
│   ├── enums/
│   │   ├── user_role.sql
│   │   ├── payment_method.sql
│   │   └── email_status.sql
│   │
│   ├── constraints/
│   │   ├── identity/
│   │   ├── email/
│   │   ├── crm/
│   │   └── billing/
│   │
│   ├── indexes/
│   │   ├── platform/
│   │   ├── identity/
│   │   ├── email/
│   │   ├── crm/
│   │   └── billing/
│   │
│   ├── views/
│   │   ├── platform/
│   │   │   └── tenant_summary.sql
│   │   ├── identity/
│   │   │   ├── user_profile.sql
│   │   │   └── user_permissions.sql
│   │   ├── email/
│   │   │   └── mailbox_dashboard.sql
│   │   └── billing/
│   │       └── invoice_summary.sql
│   │
│   ├── materialized_views/
│   │   ├── dashboard/
│   │   └── reports/
│   │
│   ├── functions/
│   │   ├── common/
│   │   │   ├── update_timestamp.sql
│   │   │   └── generate_uuid.sql
│   │   ├── identity/
│   │   │   └── get_user_permissions.sql
│   │   ├── email/
│   │   │   └── update_email_search.sql
│   │   └── billing/
│   │       └── calculate_tax.sql
│   │
│   ├── procedures/
│   │   ├── billing/
│   │   │   └── close_billing_period.sql
│   │   └── maintenance/
│   │       └── cleanup_expired_sessions.sql
│   │
│   ├── triggers/
│   │   ├── common/
│   │   │   └── updated_at.sql
│   │   ├── audit/
│   │   │   ├── user_audit.sql
│   │   │   └── invoice_audit.sql
│   │   └── email/
│   │       └── email_search.sql
│   │
│   ├── rls/
│   │   ├── platform/
│   │   │   └── tenants.sql
│   │   ├── identity/
│   │   │   └── users.sql
│   │   └── email/
│   │       └── emails.sql
│   │
│   ├── roles/
│   │   ├── admin.sql
│   │   ├── application.sql
│   │   ├── readonly.sql
│   │   └── migration.sql
│   │
│   ├── permissions/
│   │   ├── admin.sql
│   │   ├── application.sql
│   │   └── readonly.sql
│   │
│   ├── extensions/
│   │   ├── pgcrypto.sql
│   │   ├── pg_trgm.sql
│   │   └── unaccent.sql
│   │
│   └── seeds/
│       ├── development/
│       ├── staging/
│       └── production/
│
├── migrations/                              ⭐ APPEND-ONLY APPLY HISTORY
│   ├── 0001_initial_schema.sql
│   └── ...
│
├── engine/
│   ├── __init__.py
│   ├── connection.py
│   ├── inspector.py
│   ├── comparator.py
│   ├── dependency.py
│   ├── planner.py
│   ├── executor.py
│   ├── transaction.py
│   ├── verifier.py
│   └── rollback.py
│
├── commands/
│   ├── __init__.py
│   ├── init.py
│   ├── check.py
│   ├── diff.py
│   ├── deploy.py
│   ├── verify.py
│   ├── status.py
│   └── repair.py
│
├── reports/
│   ├── __init__.py
│   ├── models.py
│   ├── formatter.py
│   ├── console.py
│   └── json.py
│
├── scripts/
│   ├── db_init.py
│   ├── db_check.py
│   ├── db_diff.py
│   ├── db_deploy.py
│   └── db_seed.py
│
├── tests/
│   ├── schema/
│   │   ├── tables/
│   │   ├── views/
│   │   ├── functions/
│   │   └── triggers/
│   ├── engine/
│   │   ├── test_inspector.py
│   │   ├── test_comparator.py
│   │   ├── test_planner.py
│   │   └── test_verifier.py
│   ├── migrations/
│   ├── integration/
│   └── fixtures/
│
└── docs/
    ├── architecture.md
    ├── database-design.md
    ├── migration-guide.md
    ├── deployment.md
    └── disaster-recovery.md
```

---

## DEPLOY PIPELINE — THE ONLY WAY THE LIVE DB IS CHANGED

`python scripts/db_deploy.py` (or `python -m commands.deploy`) is the only write path against a running database.

```
python scripts/db_init.py       # empty database: create DB + roles, then deploy
python scripts/db_diff.py       # inspect + compare — print plan — NO writes
python scripts/db_check.py      # inspect + compare — exit 0 only if already in sync
python scripts/db_deploy.py     # full 6-step pipeline + report
python scripts/db_seed.py       # environment seeds only — never in the schema diff
```

### Mandatory console output

`reports/console.py` MUST print this shape. Same box width (52 inner chars). Same step labels. Same section headers. Same `+` / `~` / `✓` marks. Do not invent a different dashboard.

```
╔════════════════════════════════════════════════════╗
║             DATABASE DEPLOYMENT                    ║
╚════════════════════════════════════════════════════╝

Environment : production
Database    : mail_platform
Host        : postgres.internal
Version     : 42
Time        : 2026-08-29 11:42:18

[1/6] Connecting............................ OK
[2/6] Inspecting current database.......... OK
[3/6] Comparing schema..................... OK

Changes detected:
─────────────────────────────────────────────────────

TABLES
  + users.status
  ~ users.email VARCHAR(100) → VARCHAR(255)
  ~ users.id INTEGER → BIGINT

INDEXES
  + ix_users_email

VIEWS
  ~ user_profile

FUNCTIONS
  + calculate_tax()

PROCEDURES
  + close_billing_period()

TRIGGERS
  + trg_user_audit

RLS
  + users_tenant_isolation

─────────────────────────────────────────────────────

Applying changes...

  ✓ users.status
  ✓ users.email
  ✓ users.id
  ✓ ix_users_email
  ✓ user_profile
  ✓ calculate_tax()
  ✓ close_billing_period()
  ✓ trg_user_audit
  ✓ users_tenant_isolation

[5/6] Re-checking database................ OK
[6/6] Verification........................ OK


╔════════════════════════════════════════════════════╗
║                 FINAL DATABASE                     ║
╚════════════════════════════════════════════════════╝

Tables       : 42
Views        : 18
Functions    : 12
Procedures   : 4
Triggers     : 27
Indexes      : 76
RLS Policies : 19
Roles        : 5
Extensions   : 3


CHANGES THIS RUN
─────────────────────────────────────────────────────

Tables       : 3
Views        : 1
Functions    : 1
Procedures   : 1
Triggers     : 1
Indexes      : 1
RLS Policies : 1

Total changes: 9

STATUS: ✓ DATABASE IS IN SYNC
```

**Report rules:**

- `+` = object/column will be created
- `~` = object/column exists but definition differs (show old → new for types)
- `-` = extra object on live DB (printed only when `--allow-destructive`; otherwise listed under `Skipped destructive` and NOT applied)
- After apply, every applied item is printed again with `✓`
- `CHANGES THIS RUN` counts **applied** changes only, grouped by object kind
- A table that gained a column AND changed a type counts as **2** table changes
- If there is no drift after step 3, skip "Applying changes", still print FINAL DATABASE, `Total changes: 0`, `STATUS: ✓ DATABASE IS IN SYNC`
- Failed step prints `FAIL` instead of `OK` and stops
- Never print passwords, connection query strings, or role passwords

---

## CONFIG

```yaml
# config/versions.yaml
schema_version: 42
```

`schema_version` is what the report prints as `Version`. Bump it in the **same change** that edits `schema/`.

```yaml
# config/database.yaml
search_path: "platform, identity, email, crm, billing, public"
managed_schemas:
  - platform
  - identity
  - email
  - crm
  - billing
apply_order:
  - extensions
  - roles
  - schemas
  - types
  - enums
  - tables
  - constraints
  - indexes
  - functions
  - procedures
  - triggers
  - views
  - materialized_views
  - rls
  - permissions
```

```yaml
# config/environments/production.yaml
environment: production
allow_destructive: false
require_ssl: true
```

```yaml
# config/environments/development.yaml
environment: development
allow_destructive: false
require_ssl: false
```

```bash
# .env.example
APP_ENV=development
DATABASE_URL=postgres://appuser:password@127.0.0.1:5432/mail_platform
DATABASE_NAME=mail_platform
DATABASE_HOST=127.0.0.1
```

**RULES:**

- Connection comes from `DATABASE_URL` in `.env` / `.env.production`
- `APP_ENV` selects `config/environments/{APP_ENV}.yaml`
- NEVER use `os.getenv` scattered through engine files — load once in `engine/connection.py`

---

## SCHEMA SQL STANDARDS

### File header — every `.sql` file in `schema/`

```sql
-- =============================================================================
-- schema/tables/identity/users.sql
-- Schema      : identity
-- Object      : users
-- Description : Application user accounts
-- Depends on  : schema/schemas/identity.sql, schema/enums/user_role.sql
-- Created     : 2026-08-29
-- Modified    : 2026-08-29
-- =============================================================================
```

### Apply order inside `schema/` (never change)

```
1. extensions/
2. roles/
3. schemas/
4. types/ then enums/
5. tables/          (FK order via engine/dependency.py)
6. constraints/
7. indexes/
8. functions/
9. procedures/
10. triggers/
11. views/
12. materialized_views/
13. rls/
14. permissions/
15. seeds/          (only via db_seed.py — never part of schema compare)
```

### `schema/schemas/` — PostgreSQL namespaces

```sql
-- schema/schemas/identity.sql
CREATE SCHEMA IF NOT EXISTS identity;
COMMENT ON SCHEMA identity IS 'Users, sessions, roles, addresses';
```

### `schema/extensions/`

```sql
-- schema/extensions/pgcrypto.sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

Install extensions as a superuser / migration role. The application role MUST NOT be a superuser.

### `schema/enums/` and `schema/types/`

```sql
-- schema/enums/user_role.sql
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE identity.user_role AS ENUM ('admin', 'manager', 'staff', 'viewer');
    END IF;
END
$$;
```

The engine adds missing enum labels with `ALTER TYPE ... ADD VALUE`. Removing a label is destructive.

### `schema/tables/` — one table per file

```sql
-- =============================================================================
-- schema/tables/identity/users.sql
-- Schema      : identity
-- Object      : users
-- Description : Application user accounts
-- Depends on  : schema/schemas/identity.sql, schema/tables/platform/tenants.sql
-- Created     : 2026-08-29
-- Modified    : 2026-08-29
-- =============================================================================

CREATE TABLE IF NOT EXISTS identity.users (
    id               UUID          NOT NULL DEFAULT gen_random_uuid(),
    tenant_id        UUID          NOT NULL,
    email            VARCHAR(255)  NOT NULL,
    hashed_password  VARCHAR(255)  NOT NULL,
    full_name        VARCHAR(255),
    status           VARCHAR(32)   NOT NULL DEFAULT 'active',
    is_active        BOOLEAN       NOT NULL DEFAULT true,
    is_superuser     BOOLEAN       NOT NULL DEFAULT false,
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_users            PRIMARY KEY (id),
    CONSTRAINT fk_users_tenant     FOREIGN KEY (tenant_id)
                                   REFERENCES platform.tenants (id)
                                   ON DELETE RESTRICT
                                   ON UPDATE CASCADE,
    CONSTRAINT uq_users_email      UNIQUE (email),
    CONSTRAINT chk_users_email     CHECK (email ~* '^[^@]+@[^@]+\.[^@]+$')
);

COMMENT ON TABLE  identity.users                 IS 'Application user accounts';
COMMENT ON COLUMN identity.users.id              IS 'UUID primary key — auto-generated';
COMMENT ON COLUMN identity.users.tenant_id       IS 'FK to platform.tenants — tenant isolation';
COMMENT ON COLUMN identity.users.email           IS 'Unique login email';
COMMENT ON COLUMN identity.users.hashed_password IS 'bcrypt hash — never plain text';
COMMENT ON COLUMN identity.users.full_name       IS 'Display name — optional';
COMMENT ON COLUMN identity.users.status          IS 'Lifecycle status';
COMMENT ON COLUMN identity.users.is_active       IS 'Soft-disable without deleting the account';
COMMENT ON COLUMN identity.users.is_superuser    IS 'Platform-level admin';
COMMENT ON COLUMN identity.users.created_at      IS 'Row creation timestamp (UTC)';
COMMENT ON COLUMN identity.users.updated_at      IS 'Last update timestamp — trigger-managed';
```

**Table rules:**

- ALWAYS schema-qualify: `identity.users`, never bare `users`
- ALWAYS `UUID` PK with `DEFAULT gen_random_uuid()` — NEVER `SERIAL` / `BIGSERIAL`
- ALWAYS `created_at` and `updated_at` `TIMESTAMPTZ`
- ALWAYS named constraints: `pk_`, `fk_`, `uq_`, `chk_`
- ALWAYS `COMMENT ON TABLE` and `COMMENT ON COLUMN` for every column
- Foreign key columns end in `_id`
- `ON DELETE CASCADE` for owned data, `ON DELETE RESTRICT` for referenced data
- The file is the **desired** table. The engine emits `ALTER TABLE` for live drift. Do not hand-write `ALTER TABLE` in `tables/` files.

### `schema/indexes/` — one file per table

```sql
-- schema/indexes/identity/users.sql
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email_lower
    ON identity.users (LOWER(email));

CREATE INDEX IF NOT EXISTS ix_users_tenant_id
    ON identity.users (tenant_id);

CREATE INDEX IF NOT EXISTS ix_users_status
    ON identity.users (status)
    WHERE is_active = true;

COMMENT ON INDEX identity.ix_users_email_lower IS 'Case-insensitive unique email';
COMMENT ON INDEX identity.ix_users_tenant_id   IS 'Tenant isolation lookup';
COMMENT ON INDEX identity.ix_users_status      IS 'Partial index: active users by status';
```

Index names: `ix_{table}_{columns}`. Every FK column MUST have an index.

### `schema/functions/`

```sql
-- schema/functions/common/update_timestamp.sql
CREATE OR REPLACE FUNCTION platform.update_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION platform.update_timestamp() IS
    'Sets updated_at = NOW() on every UPDATE. Attach to any table with updated_at.';
```

- ALWAYS `CREATE OR REPLACE FUNCTION`
- ALWAYS `LANGUAGE plpgsql` or `LANGUAGE sql`
- Read-only functions: `STABLE` or `IMMUTABLE`
- Parameters `p_`, locals `v_`
- `SECURITY DEFINER` only when documented

### `schema/procedures/`

```sql
-- schema/procedures/billing/close_billing_period.sql
CREATE OR REPLACE PROCEDURE billing.close_billing_period(p_period DATE)
LANGUAGE plpgsql
AS $$
BEGIN
    -- close open invoices for the period
    NULL;
END;
$$;
```

### `schema/triggers/`

```sql
-- schema/triggers/common/updated_at.sql
DROP TRIGGER IF EXISTS trg_users_updated_at ON identity.users;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON identity.users
    FOR EACH ROW
    EXECUTE FUNCTION platform.update_timestamp();
```

Names: `trg_{table}_{purpose}`. ALWAYS `DROP TRIGGER IF EXISTS` then `CREATE TRIGGER`.

### `schema/views/`

```sql
-- schema/views/identity/user_profile.sql
CREATE OR REPLACE VIEW identity.user_profile AS
SELECT
    u.id,
    u.email,
    u.full_name,
    u.status,
    u.tenant_id,
    u.created_at
FROM identity.users u
WHERE u.is_active = true;

COMMENT ON VIEW identity.user_profile IS 'Active user profile projection';
```

- ALWAYS `CREATE OR REPLACE VIEW`
- NEVER `SELECT *`
- Views are read-only

### `schema/rls/`

```sql
-- schema/rls/identity/users.sql
ALTER TABLE identity.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.users FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS users_tenant_isolation ON identity.users;

CREATE POLICY users_tenant_isolation
    ON identity.users
    AS PERMISSIVE
    FOR ALL
    TO application
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
```

### `schema/roles/` and `schema/permissions/`

```sql
-- schema/roles/application.sql
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'application') THEN
        CREATE ROLE application LOGIN;
    END IF;
END
$$;
```

```sql
-- schema/permissions/application.sql
GRANT USAGE ON SCHEMA identity TO application;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA identity TO application;
```

The application role gets DML on tables. It does NOT get `CREATE`, `DROP`, or extension rights. The migration role is what `db_deploy.py` uses.

### `schema/seeds/`

Seeds are **not** compared by the engine. `db_seed.py` loads `schema/seeds/{APP_ENV}/` only. Production seeds are reference data only (plans, not fake users).

### `migrations/`

After a successful deploy that applied SQL, append:

```
migrations/{NNNN}_{slug}.sql
```

`NNNN` is the next four-digit number. The file contains the exact statements the executor ran, plus a header with environment, version, timestamp, and change count.
NEVER edit a migration that has already been written. NEVER use `migrations/` as the desired-state source.

---

## ENGINE — LAYER RULES

### Catalog model — `reports/models.py`

```python
# reports/models.py
from dataclasses import dataclass, field
from typing import Literal

ChangeKind = Literal["add", "modify", "drop"]
ObjectKind = Literal[
    "tables", "indexes", "views", "materialized_views",
    "functions", "procedures", "triggers", "rls",
    "roles", "extensions", "constraints", "types",
]


@dataclass
class Column:
    name: str
    data_type: str
    nullable: bool
    default: str | None = None


@dataclass
class Table:
    schema: str
    name: str
    columns: dict[str, Column]


@dataclass
class DbObject:
    kind: ObjectKind
    schema: str
    name: str
    identity: str          # display: users.status  or  calculate_tax()
    definition: str = ""


@dataclass
class Change:
    kind: ChangeKind       # add / modify / drop
    object_kind: ObjectKind
    identity: str
    sql: str
    detail: str = ""       # "VARCHAR(100) → VARCHAR(255)"
    destructive: bool = False


@dataclass
class Inventory:
    tables: int = 0
    views: int = 0
    functions: int = 0
    procedures: int = 0
    triggers: int = 0
    indexes: int = 0
    rls_policies: int = 0
    roles: int = 0
    extensions: int = 0


@dataclass
class Catalog:
    tables: dict[str, Table] = field(default_factory=dict)
    objects: list[DbObject] = field(default_factory=list)
    inventory: Inventory = field(default_factory=Inventory)
```

### `engine/connection.py`

```python
# engine/connection.py
from pathlib import Path

import psycopg
import yaml
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ROOT / ".env"), extra="ignore")

    APP_ENV: str = "development"
    DATABASE_URL: str
    DATABASE_NAME: str
    DATABASE_HOST: str


settings = Settings()


def load_yaml(rel: str) -> dict:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8")) or {}


def env_config() -> dict:
    return load_yaml(f"config/environments/{settings.APP_ENV}.yaml")


def schema_version() -> int:
    return int(load_yaml("config/versions.yaml")["schema_version"])


def connect() -> psycopg.Connection:
    cfg = env_config()
    kwargs: dict = {"autocommit": False}
    if cfg.get("require_ssl"):
        kwargs["sslmode"] = "require"
    return psycopg.connect(settings.DATABASE_URL, **kwargs)
```

**RULES:**

- `connect()` is the only place a live connection is opened
- Deploy uses the **migration** role, never the application role
- `autocommit=False` — the whole apply + re-check is one transaction until verification passes

### `engine/inspector.py`

Read the **live** catalog. Managed schemas only (`config/database.yaml` → `managed_schemas`). Ignore `pg_*` and `information_schema`.

Inspect at least:

| Kind | Source |
| --- | --- |
| Tables + columns + types | `information_schema.columns` |
| Indexes | `pg_indexes` |
| Views | `pg_views` |
| Materialized views | `pg_matviews` |
| Functions / procedures | `pg_proc` + `pg_namespace` |
| Triggers | `information_schema.triggers` |
| RLS policies | `pg_policies` |
| Roles | `pg_roles` (only roles named in `schema/roles/`) |
| Extensions | `pg_extension` |

Normalize types before compare:

```
character varying(n) → VARCHAR(n)
timestamp with time zone → TIMESTAMPTZ
integer → INTEGER
bigint → BIGINT
boolean → BOOLEAN
uuid → UUID
```

### `engine/comparator.py`

Build the desired catalog by parsing every file under `schema/` except `seeds/`.
Compare to the inspected catalog.

```
missing in live     → Change(kind="add")
present, different  → Change(kind="modify")   # type, nullability, view body, function body
present only in live→ Change(kind="drop", destructive=True)
```

Column type changes:

- Widening is safe: `VARCHAR(100)` → `VARCHAR(255)`, `INTEGER` → `BIGINT`
- Narrowing is destructive: `VARCHAR(255)` → `VARCHAR(100)`, `BIGINT` → `INTEGER`
- `UUID` ↔ `INTEGER` is destructive

### `engine/dependency.py`

Sort new tables so referenced tables are created first. Use `Depends on` headers plus `REFERENCES` in the SQL. Cyclic FKs: create tables without those FKs, then apply `constraints/`.

### `engine/planner.py`

Turn each `Change` into SQL. Examples the planner MUST be able to emit:

```sql
ALTER TABLE identity.users ADD COLUMN IF NOT EXISTS status VARCHAR(32) NOT NULL DEFAULT 'active';
ALTER TABLE identity.users ALTER COLUMN email TYPE VARCHAR(255);
ALTER TABLE identity.users ALTER COLUMN id TYPE BIGINT;   -- only if not destructive / allowed
CREATE INDEX IF NOT EXISTS ix_users_email ON identity.users (email);
CREATE OR REPLACE VIEW identity.user_profile AS ...;
CREATE OR REPLACE FUNCTION billing.calculate_tax(...) ...;
CREATE OR REPLACE PROCEDURE billing.close_billing_period(...) ...;
-- trigger: DROP IF EXISTS + CREATE
-- rls: ENABLE + DROP POLICY IF EXISTS + CREATE POLICY
```

New table: run the original `schema/tables/{schema}/{name}.sql` file body.
Changed view/function/procedure: `CREATE OR REPLACE` from the file body.

### `engine/executor.py` + `engine/transaction.py`

- Apply the plan in `apply_order`
- One transaction for apply + re-check + verify
- On success: `COMMIT`, then write `migrations/{NNNN}_{slug}.sql`
- On failure: `ROLLBACK` (`engine/rollback.py`)
- Print `  ✓ {identity}` after each statement succeeds
- Print `  ✗ {identity}` and abort on the first error

### `engine/verifier.py`

```python
# engine/verifier.py
def recheck(conn, desired) -> list:
    """Inspect live DB again. Return remaining changes. Called exactly once after apply."""
    from engine.comparator import compare
    from engine.inspector import inspect

    current = inspect(conn)
    return compare(desired, current)
```

**RULES:**

- Re-check runs **exactly once** after the apply (or after one repair pass)
- Verification OK only when the remaining change list is empty
- Inventory counts come from the **post-verify** inspect, not from file counts

---

## COMMANDS

### `commands/deploy.py` — the 6-step run

```python
# commands/deploy.py
from datetime import datetime, timezone

from engine.comparator import compare, load_desired
from engine.connection import connect, env_config, schema_version, settings
from engine.executor import apply_changes
from engine.inspector import inspect
from engine.planner import plan
from engine.transaction import atomic
from engine.verifier import recheck
from reports.console import print_header, print_step, render_changes, render_final
from reports.models import Change


def run(*, allow_destructive_cli: bool = False) -> int:
    cfg = env_config()
    destructive_enabled = bool(cfg.get("allow_destructive", False)) and allow_destructive_cli
    started = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print_header(
        environment=cfg["environment"],
        database=settings.DATABASE_NAME,
        host=settings.DATABASE_HOST,
        version=schema_version(),
        time=started,
    )

    print_step(1, "Connecting", "...")
    conn = connect()
    print_step(1, "Connecting", "OK")

    print_step(2, "Inspecting current database", "...")
    current = inspect(conn)
    print_step(2, "Inspecting current database", "OK")

    print_step(3, "Comparing schema", "...")
    desired = load_desired()
    changes = compare(desired, current)
    print_step(3, "Comparing schema", "OK")

    applied: list[Change] = []
    if changes:
        render_changes(changes)
        print("\nApplying changes...\n")
        try:
            with atomic(conn):
                applied = apply_changes(conn, plan(changes, allow_destructive=destructive_enabled))
                remaining = recheck(conn, desired)
                if remaining:
                    applied.extend(
                        apply_changes(conn, plan(remaining, allow_destructive=destructive_enabled))
                    )
                    remaining = recheck(conn, desired)
                if remaining:
                    print_step(5, "Re-checking database", "FAIL")
                    print_step(6, "Verification", "FAIL")
                    raise RuntimeError("Database still drifting after one repair pass")
                print_step(5, "Re-checking database", "OK")
                print_step(6, "Verification", "OK")
        except Exception:
            print("\nSTATUS: ✗ DATABASE NOT IN SYNC\n")
            return 1
    else:
        print("\nNo changes detected.\n")
        print_step(5, "Re-checking database", "OK")
        print_step(6, "Verification", "OK")

    final = inspect(conn)
    render_final(final.inventory, applied)
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
```

### Other commands

| Command | Behavior |
| --- | --- |
| `commands/diff.py` | Steps 1–3 only. Print `Changes detected`. Exit 0 if empty, 2 if drift. No writes. |
| `commands/check.py` | Same as diff, quieter. Exit 0 if in sync, 1 if drift. |
| `commands/verify.py` | Inspect + compare after an external change. Print FINAL DATABASE. |
| `commands/status.py` | Print inventory only (no desired compare). |
| `commands/init.py` | Create database if missing, then call deploy. |
| `commands/repair.py` | Deploy with the one repair pass made explicit (same engine). |

### `scripts/db_deploy.py`

```python
# scripts/db_deploy.py
import argparse

from commands.deploy import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-destructive", action="store_true")
    args = parser.parse_args()
    raise SystemExit(run(allow_destructive_cli=args.allow_destructive))
```

Every file in `scripts/` is a thin wrapper. Logic lives in `commands/` + `engine/`.

The executor must persist the exact executed SQL and checksums in a database audit table inside the same transaction. After commit, write the immutable `migrations/` artifact from that audit record. If artifact creation fails, exit non-zero and report the audit ID; never pretend the migration history is complete.

---

## REPORTS — `reports/console.py`

Implement the exact boxes. Do not use Rich tables as a replacement for this layout.

```python
# reports/console.py
from collections import Counter

from reports.models import Change, Inventory

BOX_TOP = "╔════════════════════════════════════════════════════╗"
BOX_BOT = "╚════════════════════════════════════════════════════╝"
RULE = "─────────────────────────────────────────────────────"
KINDS = [
    ("tables", "TABLES"),
    ("indexes", "INDEXES"),
    ("views", "VIEWS"),
    ("functions", "FUNCTIONS"),
    ("procedures", "PROCEDURES"),
    ("triggers", "TRIGGERS"),
    ("rls", "RLS"),
]


def print_header(*, environment: str, database: str, host: str, version: int, time: str) -> None:
    print()
    print(BOX_TOP)
    print("║             DATABASE DEPLOYMENT                    ║")
    print(BOX_BOT)
    print()
    print(f"Environment : {environment}")
    print(f"Database    : {database}")
    print(f"Host        : {host}")
    print(f"Version     : {version}")
    print(f"Time        : {time}")
    print()


def print_step(n: int, label: str, status: str) -> None:
    dots = "." * max(2, 40 - len(label))
    print(f"[{n}/6] {label}{dots} {status}")


def _mark(change: Change) -> str:
    return {"add": "+", "modify": "~", "drop": "-"}[change.kind]


def render_changes(changes: list[Change]) -> None:
    print()
    print("Changes detected:")
    print(RULE)
    print()
    by_kind: dict[str, list[Change]] = {}
    for change in changes:
        by_kind.setdefault(change.object_kind, []).append(change)
    for key, title in KINDS:
        items = by_kind.get(key, [])
        if not items:
            continue
        print(title)
        for change in items:
            extra = f" {change.detail}" if change.detail else ""
            print(f"  {_mark(change)} {change.identity}{extra}")
        print()
    print(RULE)


def render_final(inventory: Inventory, applied: list[Change]) -> None:
    counts = Counter(c.object_kind for c in applied)
    print()
    print(BOX_TOP)
    print("║                 FINAL DATABASE                     ║")
    print(BOX_BOT)
    print()
    print(f"Tables       : {inventory.tables}")
    print(f"Views        : {inventory.views}")
    print(f"Functions    : {inventory.functions}")
    print(f"Procedures   : {inventory.procedures}")
    print(f"Triggers     : {inventory.triggers}")
    print(f"Indexes      : {inventory.indexes}")
    print(f"RLS Policies : {inventory.rls_policies}")
    print(f"Roles        : {inventory.roles}")
    print(f"Extensions   : {inventory.extensions}")
    print()
    print()
    print("CHANGES THIS RUN")
    print(RULE)
    print()
    print(f"Tables       : {counts['tables']}")
    print(f"Views        : {counts['views']}")
    print(f"Functions    : {counts['functions']}")
    print(f"Procedures   : {counts['procedures']}")
    print(f"Triggers     : {counts['triggers']}")
    print(f"Indexes      : {counts['indexes']}")
    print(f"RLS Policies : {counts['rls']}")
    print()
    print(f"Total changes: {len(applied)}")
    print()
    print("STATUS: ✓ DATABASE IS IN SYNC")
    print()
```

`reports/json.py` writes the same data as JSON for CI. It does not replace the console report.

---

## DESTRUCTIVE CHANGES

Blocked unless `allow_destructive: true` **and** `--allow-destructive` is passed:

```
DROP TABLE / DROP COLUMN
Narrowing a type
Dropping a view, function, procedure, index, trigger, or policy that is not in schema/
UUID ↔ integer identity changes
```

In production, `allow_destructive` MUST stay `false`.
Skipped destructive items are printed, not applied, remain drift, and cause a non-zero exit with `STATUS: ✗ DATABASE NOT IN SYNC (DESTRUCTIVE APPROVAL REQUIRED)`. Never print the green in-sync status while any desired/current drift remains.

---

## NAMING CONVENTIONS

| Object | Convention | Example |
| --- | --- | --- |
| PostgreSQL schema | `snake_case` domain | `identity`, `billing` |
| Table | `snake_case` plural | `users`, `invoice_items` |
| Qualified table | `{schema}.{table}` | `identity.users` |
| Column | `snake_case` | `created_at`, `tenant_id` |
| Primary key | always `id` UUID | `id` |
| Foreign key | `{singular}_id` | `tenant_id`, `user_id` |
| Boolean | `is_` / `has_` | `is_active` |
| Timestamp | `_at` + `TIMESTAMPTZ` | `created_at` |
| Constraint | `{pk\|fk\|uq\|chk}_{table}_{col}` | `pk_users`, `fk_users_tenant` |
| Index | `ix_{table}_{col}` | `ix_users_email` |
| Trigger | `trg_{table}_{purpose}` | `trg_users_updated_at` |
| Function / procedure | `snake_case` verb | `calculate_tax()`, `close_billing_period()` |
| View | purpose name, no required suffix | `user_profile` |
| RLS policy | `{table}_{purpose}` | `users_tenant_isolation` |
| SQL file | `{object}.sql` inside the domain folder | `tables/identity/users.sql` |
| Migration file | `{NNNN}_{slug}.sql` | `0007_add_user_status.sql` |

---

## WHEN ADDING A NEW TABLE

```
STEP 1  schema/schemas/{domain}.sql              (if the schema is new)
STEP 2  schema/tables/{domain}/{name}.sql
STEP 3  schema/indexes/{domain}/{name}.sql       (every FK + query paths)
STEP 4  schema/triggers/common/updated_at.sql    (attach update_timestamp)
STEP 5  schema/rls/{domain}/{name}.sql           (if tenant-owned)
STEP 6  config/versions.yaml                     bump schema_version
STEP 7  python scripts/db_diff.py                review the plan
STEP 8  python scripts/db_deploy.py              inspect → apply → re-check → report
STEP 9  Confirm STATUS: ✓ DATABASE IS IN SYNC
STEP 10 Update backend models to match — after the DB is in sync
```

Adding a column: edit the existing `tables/` file (desired state), bump `schema_version`, `db_diff.py`, then `db_deploy.py`. The engine emits `ALTER TABLE ... ADD COLUMN`.

Changing a type: edit the column type in the same `tables/` file. The report must show `~ table.col OLD → NEW`.

---

## TESTS

| Path | What it proves |
| --- | --- |
| `tests/engine/test_inspector.py` | Catalog counts match a fixture database |
| `tests/engine/test_comparator.py` | Missing column → add; VARCHAR widen → modify |
| `tests/engine/test_planner.py` | Emits `ADD COLUMN` / `ALTER COLUMN TYPE` |
| `tests/engine/test_verifier.py` | Second diff empty after apply; non-empty fails |
| `tests/schema/tables/` | Each table file parses and is schema-qualified |
| `tests/integration/` | Deploy against ephemeral Postgres, assert report counts |

A deploy that changes types MUST have a comparator + planner test.

---

## ABSOLUTE PROHIBITIONS

```
✗  DataStructure/ or DB_Load.py — this project replaced them
✗  Blind CREATE IF NOT EXISTS as the deploy strategy
✗  Applying schema files without inspect → compare first
✗  Skipping the one-time re-check
✗  Declaring success while the second diff is non-empty
✗  SERIAL / BIGSERIAL primary keys — UUID + gen_random_uuid()
✗  Unnamed constraints
✗  Tables without created_at / updated_at TIMESTAMPTZ
✗  Tables without COMMENT ON TABLE / COMMENT ON COLUMN
✗  SELECT * in views
✗  Bare table names — always schema-qualify
✗  TIMESTAMP without time zone
✗  Plain-text passwords in any column
✗  Application role running db_deploy.py
✗  DROP / type-narrow in production without --allow-destructive
✗  Editing an already-written migrations/ file
✗  Seeds applied by db_deploy.py
✗  os.getenv outside engine/connection.py
✗  Printing DATABASE_URL or passwords in the report
✗  Backend migrations as the schema source of truth
✗  Deploying a change that affects another product or SaaS without telling me first
```

---

## PRE-COMPLETION CHECKLIST

```
[ ] Change lives in schema/ (desired state), not only in a migration file
[ ] schema_version bumped in config/versions.yaml
[ ] New table is schema-qualified and has comments, UUID pk, timestamps
[ ] New table has indexes/ file covering every FK
[ ] Tenant-owned table has rls/ policy
[ ] python scripts/db_diff.py reviewed
[ ] python scripts/db_deploy.py printed the 6 steps
[ ] Re-check ran once and verification is OK
[ ] FINAL DATABASE inventory printed
[ ] CHANGES THIS RUN counts match the applied list
[ ] STATUS: ✓ DATABASE IS IN SYNC
[ ] migrations/{NNNN}_{slug}.sql appended with the SQL that ran
[ ] Backend models updated only AFTER deploy succeeded
[ ] No destructive SQL in production
[ ] If another product or SaaS could be affected — I stopped and told you
```

---

## QUICK REFERENCE — DAILY CHANGE

```
1. Edit schema/tables|views|functions|...   ← desired state
2. Bump config/versions.yaml
3. python scripts/db_diff.py                ← see + and ~ , no writes
4. python scripts/db_deploy.py              ← live inspect, apply, re-check, report
5. Read CHANGES THIS RUN + STATUS
6. Update backend to match the live schema
```

```
Push order:  database/  →  backend/  →  frontend/
Never push backend schema changes that are not already in schema/ and deployed.
```

---

_Stack baseline (verified 2026-10-14): PostgreSQL 18 · Python 3.15 · psycopg 3 · PyYAML · python-dotenv · uv | v3.1_

---

## Copyright

© 2026 **Udhayaboopathi V**. Released under the repository's MIT License.

- Author: Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub: [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
