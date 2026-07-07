# AGENT INSTRUCTIONS — Database Structure & Schema Management

> **HOW TO USE THIS FILE**
> Drop this file into your project root. When starting a new chat, say:
> _"Read `DATABASE_STRUCTURE.md` deeply and follow every instruction in it for all code you generate."_
> This file is the single source of truth for all database objects. No exceptions.

---

## YOUR IDENTITY

You are a senior PostgreSQL database engineer.
Every SQL file, schema document, and database utility script you generate MUST follow the exact structure, naming rules, and standards in this document.
When any migration changes the database schema, ALL relevant files in `DataStructure/` MUST be updated in the same change.

---

## MANDATORY FOLDER STRUCTURE

```
DataStructure/
│
├── Tables/                          # CREATE TABLE statements — one file per table
│   ├── 01_users.sql
│   ├── 02_items.sql
│   ├── 03_categories.sql
│   └── ...                          # numbered in dependency order
│
├── Functions/                       # CREATE OR REPLACE FUNCTION — one per file
│   ├── 01_update_timestamp.sql      # shared trigger function (usually first)
│   ├── 02_get_user_stats.sql
│   └── ...
│
├── Triggers/                        # CREATE TRIGGER — one per file
│   ├── 01_users_updated_at.sql
│   ├── 02_items_updated_at.sql
│   └── ...
│
├── Indexing/                        # CREATE INDEX — one per file
│   ├── 01_users_indexes.sql
│   ├── 02_items_indexes.sql
│   └── ...
│
├── Procedures/                      # CREATE OR REPLACE PROCEDURE — one per file
│   └── 01_archive_old_records.sql   # long-running batch operations
│
├── Views/                           # CREATE OR REPLACE VIEW — one per file
│   ├── 01_active_users_view.sql
│   ├── 02_item_summary_view.sql
│   └── ...
│
├── schema.sql                       # Auto-assembled: ALL files combined in load order
├── schema.md                        # Human-readable schema documentation
├── DB_Load.py                       # Executes all SQL files in correct order
└── readme.md                        # Setup instructions and environment config
```

---

## NUMBERING RULES

```
Format:  {NN}_{object_name}.sql
         NN = two-digit zero-padded number (01, 02, ... 99)

Within each folder, numbers define EXECUTION ORDER.
Lower number = no dependency on higher-numbered files in the same folder.

Cross-folder execution order (always):
  1. Tables/      first  (everything depends on tables)
  2. Functions/   second (may reference tables)
  3. Triggers/    third  (depend on tables + functions)
  4. Indexing/    fourth (depend on tables)
  5. Views/       fifth  (may reference tables + functions)
  6. Procedures/  sixth  (may reference any of the above)

When adding a new file:
  - Use the next available number in that folder
  - NEVER reuse a number that has been used before (even if the file was deleted)
  - NEVER renumber existing files — it breaks the history
```

---

## SQL FILE STANDARDS

### Every SQL file MUST follow this format:

```sql
-- =============================================================================
-- {FOLDER}/{NN}_{object_name}.sql
-- Description : One clear sentence describing what this object does
-- Depends on  : List files this depends on (or "None")
-- Created     : YYYY-MM-DD
-- Modified    : YYYY-MM-DD
-- =============================================================================
```

---

## TABLES/ — File Standards

Each file creates exactly ONE table.

```sql
-- =============================================================================
-- Tables/01_users.sql
-- Description : Stores all application user accounts
-- Depends on  : None
-- Created     : 2026-07-07
-- Modified    : 2026-07-07
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (

    -- ── Primary Key ────────────────────────────────────────────────────
    id               UUID          NOT NULL DEFAULT gen_random_uuid(),

    -- ── Core fields ────────────────────────────────────────────────────
    email            VARCHAR(255)  NOT NULL,
    hashed_password  VARCHAR(255)  NOT NULL,
    full_name        VARCHAR(255),
    is_active        BOOLEAN       NOT NULL DEFAULT true,
    role             VARCHAR(50)   NOT NULL DEFAULT 'staff'
                                   CHECK (role IN ('admin','manager','staff','viewer')),

    -- ── Audit timestamps ───────────────────────────────────────────────
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    -- ── Constraints ────────────────────────────────────────────────────
    CONSTRAINT pk_users           PRIMARY KEY (id),
    CONSTRAINT uq_users_email     UNIQUE      (email),
    CONSTRAINT chk_users_email    CHECK       (email ~* '^[^@]+@[^@]+\.[^@]+$')
);

-- ── Column Comments ────────────────────────────────────────────────────────
COMMENT ON TABLE  users                    IS 'Application user accounts';
COMMENT ON COLUMN users.id                 IS 'UUID primary key — auto-generated';
COMMENT ON COLUMN users.email              IS 'Unique user email — used for login';
COMMENT ON COLUMN users.hashed_password    IS 'bcrypt hashed password — never plain text';
COMMENT ON COLUMN users.full_name          IS 'Display name — optional';
COMMENT ON COLUMN users.is_active          IS 'Soft-disable without deleting the account';
COMMENT ON COLUMN users.role               IS 'Access role: admin | manager | staff | viewer';
COMMENT ON COLUMN users.created_at         IS 'Row creation timestamp (UTC)';
COMMENT ON COLUMN users.updated_at         IS 'Last update timestamp — managed by trigger';
```

```sql
-- =============================================================================
-- Tables/02_items.sql
-- Description : Stores items owned by users
-- Depends on  : Tables/01_users.sql
-- Created     : 2026-07-07
-- Modified    : 2026-07-07
-- =============================================================================

CREATE TABLE IF NOT EXISTS items (

    id           UUID          NOT NULL DEFAULT gen_random_uuid(),
    title        VARCHAR(255)  NOT NULL,
    description  TEXT,
    owner_id     UUID          NOT NULL,
    is_archived  BOOLEAN       NOT NULL DEFAULT false,
    created_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_items         PRIMARY KEY (id),
    CONSTRAINT fk_items_owner   FOREIGN KEY (owner_id)
                                REFERENCES  users(id)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE
);

COMMENT ON TABLE  items            IS 'Items owned by users';
COMMENT ON COLUMN items.id         IS 'UUID primary key';
COMMENT ON COLUMN items.title      IS 'Item title — required, max 255 chars';
COMMENT ON COLUMN items.description IS 'Optional long-form description';
COMMENT ON COLUMN items.owner_id   IS 'FK to users.id — CASCADE delete';
COMMENT ON COLUMN items.is_archived IS 'Soft archive — hidden from default queries';
COMMENT ON COLUMN items.created_at IS 'Row creation timestamp (UTC)';
COMMENT ON COLUMN items.updated_at IS 'Last update timestamp — managed by trigger';
```

**Table Rules:**
- ALWAYS use `CREATE TABLE IF NOT EXISTS`
- ALWAYS use `UUID` primary key with `DEFAULT gen_random_uuid()`
- ALWAYS include `created_at` and `updated_at` TIMESTAMPTZ columns
- ALWAYS name constraints explicitly: `pk_`, `fk_`, `uq_`, `chk_`
- ALWAYS add `COMMENT ON TABLE` and `COMMENT ON COLUMN` for every column
- NEVER use `SERIAL` or `BIGSERIAL` — use `UUID` primary keys
- Foreign key column names ALWAYS end in `_id`
- `ON DELETE CASCADE` for owned data, `ON DELETE RESTRICT` for referenced data

---

```sql
-- =============================================================================
-- Tables/03_audit_logs.sql
-- Description : Immutable audit trail — records every create/update/delete action
-- Depends on  : Tables/01_users.sql
-- Created     : 2026-07-07
-- Modified    : 2026-07-07
-- =============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (

    id           UUID          NOT NULL DEFAULT gen_random_uuid(),
    table_name   VARCHAR(100)  NOT NULL,
    record_id    UUID          NOT NULL,
    action       VARCHAR(20)   NOT NULL CHECK (action IN ('CREATE','UPDATE','DELETE')),
    old_values   JSONB,
    new_values   JSONB,
    performed_by UUID,            -- NULL for system actions
    ip_address   INET,
    user_agent   TEXT,
    created_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_audit_logs            PRIMARY KEY (id),
    CONSTRAINT fk_audit_logs_performer  FOREIGN KEY (performed_by)
                                        REFERENCES users(id) ON DELETE SET NULL
);

COMMENT ON TABLE  audit_logs              IS 'Immutable audit trail — never UPDATE or DELETE rows here';
COMMENT ON COLUMN audit_logs.table_name   IS 'Which table was affected';
COMMENT ON COLUMN audit_logs.record_id    IS 'PK of the affected row';
COMMENT ON COLUMN audit_logs.action       IS 'CREATE | UPDATE | DELETE';
COMMENT ON COLUMN audit_logs.old_values   IS 'Row state before change (NULL for CREATE)';
COMMENT ON COLUMN audit_logs.new_values   IS 'Row state after change (NULL for DELETE)';
COMMENT ON COLUMN audit_logs.performed_by IS 'User who performed the action';
COMMENT ON COLUMN audit_logs.ip_address   IS 'Client IP from X-Real-IP header';
```

---

## FUNCTIONS/ — File Standards

```sql
-- =============================================================================
-- Functions/01_update_timestamp.sql
-- Description : Trigger function that sets updated_at = NOW() before every UPDATE
-- Depends on  : None
-- Created     : 2026-07-07
-- Modified    : 2026-07-07
-- =============================================================================

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION update_timestamp() IS
    'Generic trigger function: sets updated_at = NOW() on every UPDATE. '
    'Attach to any table that has an updated_at column.';
```

```sql
-- =============================================================================
-- Functions/02_get_active_user_count.sql
-- Description : Returns the count of active users, optionally filtered by role
-- Depends on  : Tables/01_users.sql
-- Created     : 2026-07-07
-- Modified    : 2026-07-07
-- =============================================================================

CREATE OR REPLACE FUNCTION get_active_user_count(
    p_role VARCHAR DEFAULT NULL
)
RETURNS INTEGER
LANGUAGE plpgsql
STABLE                          -- does not modify the database
SECURITY DEFINER                -- runs with owner privileges
AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO   v_count
    FROM   users
    WHERE  is_active = true
    AND    (p_role IS NULL OR role = p_role);

    RETURN v_count;
END;
$$;

COMMENT ON FUNCTION get_active_user_count(VARCHAR) IS
    'Returns count of active users. Pass p_role to filter by role, NULL for all.';
```

**Function Rules:**
- ALWAYS use `CREATE OR REPLACE FUNCTION`
- ALWAYS specify `LANGUAGE plpgsql` or `LANGUAGE sql`
- ALWAYS mark read-only functions as `STABLE` or `IMMUTABLE`
- ALWAYS add `COMMENT ON FUNCTION`
- Use `SECURITY DEFINER` only when explicitly needed — document why
- Parameters prefixed with `p_`, local variables with `v_`

---

## TRIGGERS/ — File Standards

```sql
-- =============================================================================
-- Triggers/01_users_updated_at.sql
-- Description : Auto-updates users.updated_at before every row update
-- Depends on  : Tables/01_users.sql, Functions/01_update_timestamp.sql
-- Created     : 2026-07-07
-- Modified    : 2026-07-07
-- =============================================================================

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE
    ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

COMMENT ON TRIGGER trg_users_updated_at ON users IS
    'Calls update_timestamp() before each UPDATE to keep updated_at current.';
```

```sql
-- =============================================================================
-- Triggers/02_items_updated_at.sql
-- Description : Auto-updates items.updated_at before every row update
-- Depends on  : Tables/02_items.sql, Functions/01_update_timestamp.sql
-- Created     : 2026-07-07
-- Modified    : 2026-07-07
-- =============================================================================

DROP TRIGGER IF EXISTS trg_items_updated_at ON items;

CREATE TRIGGER trg_items_updated_at
    BEFORE UPDATE
    ON items
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

COMMENT ON TRIGGER trg_items_updated_at ON items IS
    'Calls update_timestamp() before each UPDATE to keep updated_at current.';
```

**Trigger Rules:**
- ALWAYS `DROP TRIGGER IF EXISTS` before `CREATE TRIGGER` — idempotent
- ALWAYS name triggers: `trg_{table}_{purpose}`
- ALWAYS add `COMMENT ON TRIGGER`
- BEFORE triggers for data modification (timestamps, validation)
- AFTER triggers for side-effects (audit logs, notifications)

---

## INDEXING/ — File Standards

One file per table's indexes. Group ALL indexes for a table in one file.

```sql
-- =============================================================================
-- Indexing/01_users_indexes.sql
-- Description : All indexes for the users table
-- Depends on  : Tables/01_users.sql
-- Created     : 2026-07-07
-- Modified    : 2026-07-07
-- =============================================================================

-- ── Unique indexes ─────────────────────────────────────────────────────────
-- Already created via UNIQUE constraint in table definition (users.email)
-- Explicit index for partial/conditional uniqueness:
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_lower
    ON users (LOWER(email));        -- case-insensitive unique email

-- ── Performance indexes ────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_users_role
    ON users (role)
    WHERE is_active = true;         -- partial index — only active users

CREATE INDEX IF NOT EXISTS idx_users_is_active
    ON users (is_active);

CREATE INDEX IF NOT EXISTS idx_users_created_at
    ON users (created_at DESC);     -- for list queries sorted by newest

-- ── Index Comments ─────────────────────────────────────────────────────────
COMMENT ON INDEX idx_users_email_lower IS 'Case-insensitive email lookup';
COMMENT ON INDEX idx_users_role        IS 'Partial index: active users by role';
COMMENT ON INDEX idx_users_is_active   IS 'Filter active/inactive users';
COMMENT ON INDEX idx_users_created_at  IS 'Sort by newest user (DESC)';
```

```sql
-- =============================================================================
-- Indexing/02_items_indexes.sql
-- Description : All indexes for the items table
-- Depends on  : Tables/02_items.sql
-- Created     : 2026-07-07
-- Modified    : 2026-07-07
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_items_owner_id
    ON items (owner_id);

CREATE INDEX IF NOT EXISTS idx_items_title
    ON items USING gin (to_tsvector('english', title));  -- full-text search

CREATE INDEX IF NOT EXISTS idx_items_created_at
    ON items (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_items_active
    ON items (owner_id, created_at DESC)
    WHERE is_archived = false;      -- most common query pattern

COMMENT ON INDEX idx_items_owner_id  IS 'FK lookup — items by owner';
COMMENT ON INDEX idx_items_title     IS 'Full-text search on item title';
COMMENT ON INDEX idx_items_created_at IS 'Sort by newest item';
COMMENT ON INDEX idx_items_active    IS 'Composite: active items per owner, sorted newest';
```

**Index Rules:**
- ALWAYS use `CREATE INDEX IF NOT EXISTS`
- ALWAYS name indexes: `idx_{table}_{columns}`
- Use **partial indexes** (`WHERE ...`) for frequently filtered subsets
- Use `USING gin` for full-text search columns
- ALWAYS add `COMMENT ON INDEX`
- NEVER create duplicate indexes — check existing before adding
- ALWAYS create index on every foreign key column

---

## VIEWS/ — File Standards

```sql
-- =============================================================================
-- Views/01_active_users_view.sql
-- Description : Active users with their item count — used by dashboard
-- Depends on  : Tables/01_users.sql, Tables/02_items.sql
-- Created     : 2026-07-07
-- Modified    : 2026-07-07
-- =============================================================================

CREATE OR REPLACE VIEW active_users_view AS
SELECT
    u.id,
    u.email,
    u.full_name,
    u.role,
    u.created_at,
    COUNT(i.id)  AS item_count,
    MAX(i.created_at) AS last_item_at
FROM
    users u
    LEFT JOIN items i ON i.owner_id = u.id AND i.is_archived = false
WHERE
    u.is_active = true
GROUP BY
    u.id, u.email, u.full_name, u.role, u.created_at;

COMMENT ON VIEW active_users_view IS
    'Active users with their active item count. Used by dashboard stats endpoints.';
```

**View Rules:**
- ALWAYS use `CREATE OR REPLACE VIEW`
- ALWAYS add `COMMENT ON VIEW`
- Name views: `{purpose}_view` (always `_view` suffix)
- Views are READ-ONLY — never `INSERT`/`UPDATE` through views
- NEVER use `SELECT *` in views — always name columns explicitly

---

## `schema.sql` — Combined Full Schema

This file is AUTO-ASSEMBLED by `DB_Load.py`. Never edit it manually.
It is the complete runnable schema in dependency order.

```sql
-- =============================================================================
-- schema.sql
-- AUTO-GENERATED by DB_Load.py — DO NOT EDIT MANUALLY
-- Generated   : 2026-07-07 10:00:00 UTC
-- Description : Complete database schema assembled from DataStructure/
-- Load order  : Tables → Functions → Triggers → Indexing → Views
-- =============================================================================

-- ── EXTENSIONS ───────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";    -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pg_trgm";     -- fuzzy text search
CREATE EXTENSION IF NOT EXISTS "unaccent";    -- accent-insensitive search

-- ── TABLES ───────────────────────────────────────────────────────────────────
-- [Contents of Tables/01_users.sql]
-- [Contents of Tables/02_items.sql]
-- ... etc

-- ── FUNCTIONS ────────────────────────────────────────────────────────────────
-- [Contents of Functions/01_update_timestamp.sql]
-- ... etc

-- ── TRIGGERS ─────────────────────────────────────────────────────────────────
-- [Contents of Triggers/01_users_updated_at.sql]
-- ... etc

-- ── INDEXING ─────────────────────────────────────────────────────────────────
-- [Contents of Indexing/01_users_indexes.sql]
-- ... etc

-- ── VIEWS ────────────────────────────────────────────────────────────────────
-- [Contents of Views/01_active_users_view.sql]
-- ... etc
```

---

## `DB_Load.py` — Database Loader Script

```python
#!/usr/bin/env python3
"""
DB_Load.py
──────────
Loads all SQL files from DataStructure/ into PostgreSQL in the correct order,
then assembles schema.sql and updates schema.md.

Usage:
  python DB_Load.py                        # apply all SQL to DB
  python DB_Load.py --dry-run              # print SQL without executing
  python DB_Load.py --schema-only          # only regenerate schema.sql + schema.md
  python DB_Load.py --folder Tables        # only run files in one folder
  python DB_Load.py --file Tables/01_users.sql  # run a single file
"""

import argparse
import os
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv()

BASE_DIR    = Path(__file__).parent
LOG_FORMAT  = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
log = logging.getLogger("DB_Load")

# Execution order — NEVER change this order
LOAD_ORDER = ["Tables", "Functions", "Triggers", "Indexing", "Views", "Procedures"]

EXTENSIONS_HEADER = """\
-- ── EXTENSIONS ────────────────────────────────────────────────────────────────
-- NOTE: CREATE EXTENSION requires SUPERUSER privilege.
-- Install extensions once via: psql -U postgres -d mydb < extensions.sql
-- The application DB user should NOT be a superuser.
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";
"""


# ── Database Connection ───────────────────────────────────────────────────────

def get_db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise EnvironmentError(
            "DATABASE_URL not set.\n"
            "Set it in .env: DATABASE_URL=postgres://user:pass@127.0.0.1:5432/dbname"
        )
    return url


# ── File Collection ───────────────────────────────────────────────────────────

def collect_sql_files(folder: str | None = None) -> list[Path]:
    """
    Returns SQL files in correct execution order.
    Files within each folder are sorted numerically by their NN_ prefix.
    """
    folders = [folder] if folder else LOAD_ORDER
    files: list[Path] = []

    for folder_name in folders:
        folder_path = BASE_DIR / folder_name
        if not folder_path.exists():
            log.warning("Folder not found, skipping: %s", folder_path)
            continue

        sql_files = sorted(folder_path.glob("*.sql"))
        if not sql_files:
            log.warning("No .sql files found in %s", folder_path)
            continue

        files.extend(sql_files)
        log.info("  %s — found %d file(s)", folder_name, len(sql_files))

    return files


# ── SQL Execution ─────────────────────────────────────────────────────────────

def execute_file(conn, file_path: Path, dry_run: bool = False) -> None:
    sql = file_path.read_text(encoding="utf-8")
    relative = file_path.relative_to(BASE_DIR)

    if dry_run:
        log.info("[DRY RUN] Would execute: %s (%d chars)", relative, len(sql))
        return

    log.info("Executing: %s", relative)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        log.info("  ✓ Success: %s", relative)
    except Exception as e:
        conn.rollback()
        log.error("  ✗ FAILED: %s\n  Error: %s", relative, e)
        raise


def run_all(
    files:   list[Path],
    dry_run: bool = False
) -> None:
    if dry_run:
        log.info("DRY RUN MODE — no changes will be made to the database")
        for f in files:
            log.info("  Would execute: %s", f.relative_to(BASE_DIR))
        return

    db_url = get_db_url()
    log.info("Connecting to database...")

    with psycopg.connect(db_url, autocommit=False) as conn:
        # Enable pgcrypto before tables
        with conn.cursor() as cur:
            cur.execute(EXTENSIONS_HEADER)
        conn.commit()
        log.info("Extensions installed.")

        for file_path in files:
            execute_file(conn, file_path, dry_run=False)

    log.info("All SQL files executed successfully.")


# ── Schema Assembly ───────────────────────────────────────────────────────────

def build_schema_sql(files: list[Path]) -> str:
    """Assembles all SQL files into one schema.sql file."""
    now  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    parts = [
        f"-- {'=' * 77}\n"
        f"-- schema.sql\n"
        f"-- AUTO-GENERATED by DB_Load.py — DO NOT EDIT MANUALLY\n"
        f"-- Generated   : {now}\n"
        f"-- Description : Complete database schema\n"
        f"-- Load order  : Tables → Functions → Triggers → Indexing → Views\n"
        f"-- {'=' * 77}\n\n",
        EXTENSIONS_HEADER + "\n",
    ]

    current_folder = None
    for file_path in files:
        folder_name = file_path.parent.name
        if folder_name != current_folder:
            current_folder = folder_name
            parts.append(f"\n-- {'─' * 77}\n-- {folder_name.upper()}\n-- {'─' * 77}\n\n")

        content = file_path.read_text(encoding="utf-8").strip()
        relative = file_path.relative_to(BASE_DIR)
        parts.append(f"-- Source: {relative}\n{content}\n\n")

    return "".join(parts)


def build_schema_md(files: list[Path]) -> str:
    """Generates a human-readable Markdown schema reference."""
    now   = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Database Schema Reference\n",
        f"> Auto-generated by `DB_Load.py` on {now}  \n",
        "> Do not edit manually — regenerate with `python DB_Load.py --schema-only`\n\n",
        "---\n\n",
        "## Table of Contents\n\n",
    ]

    # ToC
    for folder_name in LOAD_ORDER:
        folder_path = BASE_DIR / folder_name
        if not folder_path.exists():
            continue
        sql_files = sorted(folder_path.glob("*.sql"))
        if sql_files:
            lines.append(f"- [{folder_name}](#{folder_name.lower()})\n")

    lines.append("\n---\n\n")

    # Sections per folder
    for folder_name in LOAD_ORDER:
        folder_path = BASE_DIR / folder_name
        if not folder_path.exists():
            continue
        sql_files = sorted(folder_path.glob("*.sql"))
        if not sql_files:
            continue

        lines.append(f"## {folder_name}\n\n")

        for file_path in sql_files:
            content  = file_path.read_text(encoding="utf-8")
            relative = str(file_path.relative_to(BASE_DIR))

            # Extract header fields from the SQL comment block
            desc    = _extract_header_field(content, "Description")
            depends = _extract_header_field(content, "Depends on")
            created = _extract_header_field(content, "Created")
            modified= _extract_header_field(content, "Modified")

            lines.append(f"### `{relative}`\n\n")
            if desc:    lines.append(f"**Description:** {desc}  \n")
            if depends: lines.append(f"**Depends on:** `{depends}`  \n")
            if created: lines.append(f"**Created:** {created}  \n")
            if modified:lines.append(f"**Modified:** {modified}  \n")
            lines.append("\n```sql\n")
            lines.append(content.strip())
            lines.append("\n```\n\n")

    return "".join(lines)


def _extract_header_field(content: str, field: str) -> str:
    """Extracts a value from the SQL file header comment block."""
    for line in content.splitlines():
        if f"-- {field}" in line and ":" in line:
            return line.split(":", 1)[1].strip()
    return ""


def write_generated_files(files: list[Path]) -> None:
    schema_sql = build_schema_sql(files)
    schema_md  = build_schema_md(files)

    (BASE_DIR / "schema.sql").write_text(schema_sql, encoding="utf-8")
    log.info("✓ schema.sql updated (%d chars)", len(schema_sql))

    (BASE_DIR / "schema.md").write_text(schema_md, encoding="utf-8")
    log.info("✓ schema.md updated (%d chars)", len(schema_md))


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load DataStructure/ SQL files into PostgreSQL."
    )
    parser.add_argument("--dry-run",     action="store_true",
                        help="Print files that would run — no DB changes")
    parser.add_argument("--schema-only", action="store_true",
                        help="Only regenerate schema.sql and schema.md — no DB changes")
    parser.add_argument("--folder",      type=str,
                        choices=LOAD_ORDER,
                        help="Only execute files from one folder")
    parser.add_argument("--file",        type=str,
                        help="Execute a single SQL file (relative path)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    log.info("DataStructure Loader starting...")
    log.info("Base directory: %s", BASE_DIR)

    # Single file mode
    if args.file:
        file_path = BASE_DIR / args.file
        if not file_path.exists():
            log.error("File not found: %s", file_path)
            sys.exit(1)
        files = [file_path]
    else:
        files = collect_sql_files(folder=args.folder)

    if not files:
        log.warning("No SQL files found. Nothing to do.")
        sys.exit(0)

    log.info("Found %d SQL file(s) to process.", len(files))

    # Always regenerate schema files (unless running a single file)
    if not args.file:
        all_files = collect_sql_files()  # full set for schema generation
        write_generated_files(all_files)

    # Execute SQL
    if not args.schema_only:
        run_all(files, dry_run=args.dry_run)
    else:
        log.info("--schema-only: skipping database execution.")

    log.info("Done.")


if __name__ == "__main__":
    main()
```

---

## `schema.md` — Format Reference

The `schema.md` is auto-generated by `DB_Load.py`. When manually adding sections, follow this format:

```markdown
# Database Schema Reference

> Auto-generated by `DB_Load.py` on 2026-07-07 10:00:00 UTC
> Do not edit manually.

---

## Tables

### `Tables/01_users.sql`

**Description:** Stores all application user accounts
**Depends on:** None
**Created:** 2026-07-07
**Modified:** 2026-07-07

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NOT NULL | gen_random_uuid() | UUID primary key |
| email | VARCHAR(255) | NOT NULL | — | Unique login email |
| hashed_password | VARCHAR(255) | NOT NULL | — | bcrypt hash — never plain |
| full_name | VARCHAR(255) | NULL | — | Display name |
| is_active | BOOLEAN | NOT NULL | true | Soft-disable flag |
| role | VARCHAR(50) | NOT NULL | 'staff' | Access role |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL | NOW() | Last update timestamp |

**Constraints:**
- `pk_users` — PRIMARY KEY on `id`
- `uq_users_email` — UNIQUE on `email`
- `chk_users_email` — email format validation
```

---

## `readme.md` — Setup Guide

```markdown
# DataStructure — Database Setup

## Requirements
- PostgreSQL 16+
- Python 3.12+
- psycopg 3.x (`pip install psycopg[binary]`)
- python-dotenv (`pip install python-dotenv`)

## Setup

### 1. Configure environment
cp .env.example .env
# Edit .env and set DATABASE_URL

### 2. First-time setup (fresh database)
python DB_Load.py

### 3. Regenerate schema docs only (no DB changes)
python DB_Load.py --schema-only

### 4. Dry run (preview what would run)
python DB_Load.py --dry-run

### 5. Run a specific folder only
python DB_Load.py --folder Tables

### 6. Run a single file
python DB_Load.py --file Tables/03_categories.sql

## Environment Variables
DATABASE_URL=postgres://user:password@127.0.0.1:5432/dbname
```

---

## MIGRATION RULES — WHEN SCHEMA CHANGES

Every time a migration changes the database schema, ALL of the following MUST be updated:

```
CHANGE TYPE               → FILES TO UPDATE
─────────────────────────────────────────────────────────────────────
Add new table             → Tables/{NN}_{name}.sql  (new file)
                          → Indexing/{NN}_{name}_indexes.sql  (new file)
                          → Triggers/{NN}_{name}_updated_at.sql  (new file)
                          → schema.sql  (run DB_Load.py --schema-only)
                          → schema.md   (run DB_Load.py --schema-only)

Add column to table       → Tables/{NN}_{name}.sql  (edit: add column + comment)
                          → schema.sql + schema.md  (regenerate)

Remove column             → Tables/{NN}_{name}.sql  (edit: remove column)
                          → Indexing file           (remove related index)
                          → Views file              (update if column was used)
                          → schema.sql + schema.md  (regenerate)

Add index                 → Indexing/{NN}_{table}_indexes.sql  (edit: add index)
                          → schema.sql + schema.md  (regenerate)

Add function              → Functions/{NN}_{name}.sql  (new file)
                          → schema.sql + schema.md  (regenerate)

Add trigger               → Triggers/{NN}_{name}.sql  (new file)
                          → schema.sql + schema.md  (regenerate)

Add view                  → Views/{NN}_{name}_view.sql  (new file)
                          → schema.sql + schema.md  (regenerate)

Rename column             → Tables/{NN}_{name}.sql  (edit column name + comment)
                          → All views that reference old name
                          → All functions that reference old name
                          → schema.sql + schema.md  (regenerate)
                          → Backend migration file  (Alembic/Flyway/EF Core)
```

---

## NAMING CONVENTIONS

| Object | Convention | Example |
|--------|-----------|---------|
| Table names | `snake_case` plural | `users`, `item_categories` |
| Column names | `snake_case` | `created_at`, `owner_id` |
| Primary key | always `id` | `id UUID` |
| Foreign keys | `{singular_table}_id` | `user_id`, `category_id` |
| Boolean columns | `is_` or `has_` prefix | `is_active`, `has_verified` |
| Timestamp columns | `_at` suffix | `created_at`, `deleted_at` |
| Constraint names | `{type}_{table}_{col}` | `pk_users`, `fk_items_owner`, `uq_users_email` |
| Index names | `idx_{table}_{col}` | `idx_users_email`, `idx_items_owner_id` |
| Trigger names | `trg_{table}_{purpose}` | `trg_users_updated_at` |
| Function names | `snake_case` verb | `update_timestamp()`, `get_user_stats()` |
| View names | `{purpose}_view` | `active_users_view` |
| SQL files | `{NN}_{object_name}.sql` | `01_users.sql`, `02_items.sql` |

---

## ABSOLUTE PROHIBITIONS

```
✗  SERIAL or BIGSERIAL primary keys — always UUID with gen_random_uuid()
✗  Unnamed constraints — always pk_, fk_, uq_, chk_ prefix
✗  Tables without created_at and updated_at columns
✗  Tables without COMMENT ON TABLE and COMMENT ON COLUMN for every column
✗  SELECT * in views — always name columns explicitly
✗  Editing schema.sql manually — always regenerate with DB_Load.py
✗  Deleting or renumbering existing SQL files — only add new ones
✗  Functions without CREATE OR REPLACE
✗  Triggers without DROP TRIGGER IF EXISTS before CREATE TRIGGER
✗  Indexes without IF NOT EXISTS
✗  Foreign key columns without an index in Indexing/
✗  Migration changes without updating the corresponding DataStructure/ file
✗  Plain text passwords stored in any column — always hashed
✗  Using TIMESTAMP without timezone — always TIMESTAMPTZ
✗  Storing IDs as VARCHAR or INTEGER — always UUID
```

---

## PRE-COMPLETION CHECKLIST

```
[ ] Every new table has a corresponding Indexing/ file
[ ] Every new table has a corresponding Trigger/ file for updated_at
[ ] All columns have COMMENT ON COLUMN
[ ] All tables have COMMENT ON TABLE
[ ] All constraints are named explicitly (pk_, fk_, uq_, chk_)
[ ] All FK columns have an index in Indexing/
[ ] File numbered correctly (next available NN_ in folder)
[ ] Header comment filled in (Description, Depends on, Created, Modified)
[ ] schema.sql and schema.md regenerated: python DB_Load.py --schema-only
[ ] Backend migration file also updated (Alembic/Flyway/EF Core)
[ ] Dry run passes: python DB_Load.py --dry-run
[ ] No TIMESTAMP without TZ — always TIMESTAMPTZ
[ ] No SERIAL/BIGSERIAL — always UUID
```

---

## QUICK REFERENCE — ADDING A NEW TABLE

```
1. Create  DataStructure/Tables/{NN}_{name}.sql
           → standard header + CREATE TABLE IF NOT EXISTS + COMMENT ON ...

2. Create  DataStructure/Indexing/{NN}_{name}_indexes.sql
           → indexes for all FK columns + frequently queried columns

3. Create  DataStructure/Triggers/{NN}_{name}_updated_at.sql
           → attach update_timestamp() to the new table

4. Run     python DB_Load.py --schema-only
           → regenerates schema.sql and schema.md

5. Run     python DB_Load.py --dry-run
           → verify the files execute without errors

6. Run     python DB_Load.py --file Tables/{NN}_{name}.sql
           → apply just the new table
   Run     python DB_Load.py --file Indexing/{NN}_{name}_indexes.sql
   Run     python DB_Load.py --file Triggers/{NN}_{name}_updated_at.sql

7. Update  backend migration (Alembic/Flyway/EF Core) to match
```

---

*Stack: PostgreSQL 16 · Python 3.12 · psycopg 3 · python-dotenv*

---

## Copyright

© 2026 **Udhayaboopathi V**. All rights reserved.

- Author:  Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub:  [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
