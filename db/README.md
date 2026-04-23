# Database

## Canonical DDL (single file)

**`mvp1_schema.sql`** is the **only** file you need for a **new** PostgreSQL database. It creates schema **`ryunova`**, all **`ryunova.ryunova_*`** tables, indexes, enum type, comments, **product comments**, **listing channels** (marketplace registry + seed rows), **listing readiness**, and the **product × channel** matrix.

```bash
psql -U ryunova -d ryunova -v ON_ERROR_STOP=1 -f db/mvp1_schema.sql
```

- **Bootstrap / ops** (platform user, org membership): see **`docs/MULTI_TENANT.md`** and the commented optional section at the end of **`mvp1_schema.sql`**.
- **Public code format** (10‑char `public_code`): optional **`backend/scripts/backfill_public_codes.py`** if you need to rewrite legacy values.

## Production / EC2 (GitHub Actions)

**Deploy does not run SQL.** The workflow pulls **`/opt/apps/app_ryunova`** and starts Docker only. Schema changes are assumed to be applied already on shared PostgreSQL.

**New environment** (empty DB or new cluster):

1. Create the database and app role (or use **`scripts/run_ryunova_migrations.sh`**, which can create the DB, ensure the role, apply **`db/mvp1_schema.sql`** via **`db/migrations/order.txt`**, and grant DML to the app user — run **once** on a host that can reach Postgres).
2. Or run **`psql`** against **`db/mvp1_schema.sql`** with a superuser / owner account, then grant the app role as needed (see script for grant pattern).

FinText can continue to use schema **`fintext`** in the same **`latrobe_apps_db`** when shared.

### Future schema changes

Extend **`mvp1_schema.sql`** (idempotent `IF NOT EXISTS` / `ADD COLUMN` where possible) **or** add a new SQL file and document it here. **Deploy will not apply it automatically** unless you reintroduce that in CI.

---

### Media path migration (one-time)

If you deployed **before** the **`orgs/<organisation_id>/...`** layout, use **`backend/scripts/migrate_media_paths.py`** (see script comments and **`docs/DEPLOYMENT_EC2_ALB.md`**). Do **not** run blind SQL updates without moving files.

---

## Local database reset

If you have a **stale** dev DB, **drop and recreate** the database and run **`mvp1_schema.sql`** once, or diff against **`docs/DATABASE_SCHEMA.md`** and write your own `ALTER` scripts.
