# Branch + migrations + Supabase project linking

## Branch and migration ownership

Rules:
1. Backend/API changes live in feature branches.
2. Database changes must be delivered via `supabase/migrations/*.sql`.
3. Keep migration order deterministic using timestamped filenames:
   - `YYYYMMDDHHMMSS_description.sql`
4. Before changing DB schema, agree which migration author owns:
   - schema baseline
   - constraint/RLS hardening

## Linking the correct Supabase project (avoid pushing to the wrong one)

Always run commands from the repository root (the folder that contains `supabase/`).

Recommended checks:
1. `supabase status`
2. Read the linked project ref:
   - `supabase/.temp/project-ref`
3. If needed, relink explicitly:
   - `supabase link --project-ref <PROJECT_REF>`

If multiple repos exist on your machine, this prevents migration pushes to the wrong Supabase project.

## Migration workflow (safe pattern)

### 1) If you already created tables in Supabase Dashboard
Do NOT re-initialize. Instead, generate a baseline migration from the current remote schema:
1. Ensure correct project is linked (see above)
2. Run:
   - `supabase db pull`
3. This generates a baseline migration that creates the existing tables locally.
4. Add future changes as incremental migrations.

Official migrations guidance:
- https://supabase.com/docs/guides/deployment/database-migrations

### 2) Handling migration history mismatches
If you see errors like “remote migration history does not match local files”, reconcile metadata:
1. `supabase migration list`
2. If CLI suggests it, run a repair (example):
   - `supabase migration repair --status reverted <VERSION>`
3. Re-run:
   - `supabase db pull`

## Applying migrations vs dashboard SQL editor

Preferred: commit migrations under `supabase/migrations/` and apply via CLI.

Dashboard SQL Editor is acceptable for quick experiments, but team-safe practice:
1. Run experiment in Dashboard SQL Editor if needed
2. Copy the final SQL into a migration file
3. Apply via CLI afterward

