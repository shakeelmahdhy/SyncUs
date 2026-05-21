# Option A — implementation guide (SyncUs)

Follow after [04_fastapi_supabase_architecture.md](04_fastapi_supabase_architecture.md) auth lock. **Goal:** Bearer Supabase access JWT → verified **`sub`** → service-role Supabase client → every query scoped in code.

---

## Phase 1 — Prerequisites (done)

- Auth model **Option A** is locked in doc `04`.
- You know which HTTP routes must carry user context (table in `04`).

---

## Phase 2 — Configuration and Supabase client

1. **`.env.example` and local `.env`**
   - `SUPABASE_URL`
   - `SUPABASE_PUBLISHABLE_KEY` — publishable Supabase API key.
   - `SUPABASE_SECRET_KEY` — backend only; used to build the server `Client`.
   - `SUPABASE_JWT_SECRET` — value from Supabase **Project Settings → API → JWT Secret** (for default HS256 access tokens). If the project uses asymmetric JWTs, follow Supabase docs and verify with JWKS instead of a single secret.

2. **Align code with variable names**
   - Replace ambiguous names such as `SUPABASE_KEY` with **`SUPABASE_SECRET_KEY`** wherever `create_client` is called for **FastAPI** data access.
   - Fail fast at startup if service role or JWT secret is missing in environments where protected routes run.

3. **Optional:** `python-dotenv` loading from `backend/.env` in `main` or a small `settings` module so local runs match production’s explicit env injection.

**Exit criteria:** Starting the app with valid env creates a service-role Supabase client; no privileged key is referenced from frontend code.

---

## Phase 3 — JWT verification dependency

1. **Dependency** (e.g. `app/core/auth.py` or `app/modules/auth/deps.py`):
   - Read `Authorization: Bearer <token>` (FastAPI `HTTPBearer` or equivalent).
   - **Verify** the JWT with your project’s secret (or JWKS): signature, `exp`, and any `iss`/`aud` your tokens set.
   - Parse **`sub`**; normalize to `UUID` if the rest of the stack uses UUID.
   - On any failure → **401** with a stable error shape (do not log the full token).

2. **Types:** Small immutable object or `TypedDict` holding at least `sub: UUID`.

3. **Dependencies:** Typically `PyJWT` for HS256; pin versions in `requirements.txt`.

**Exit criteria:** A unit test or manual call proves valid project token returns `sub`, invalid/expired token returns 401.

---

## Phase 4 — Attach auth to routers

1. For each route listed under **Routes that must use `sub`** in `04`, add the dependency as a route parameter.
2. **`GET /`** stays public unless you later protect it.
3. **Matching:** Change the API shape so the caller is not authorizing via a raw path `user_id` alone — e.g. `GET /matching` with identity from the dependency only, or keep a path param only if it must equal **`sub`** and you validate equality.

**Exit criteria:** No scoped route runs without going through the dependency (mechanical check: grep router files for the dependency name).

---

## Phase 5 — Services and repositories

1. **Signatures:** Pass `user_id: UUID` (from dependency) into `service` → `repository` for every user-owned operation.
2. **Queries:** Every select/update/delete includes a filter tied to **`sub`** (or a join through a profile keyed by `sub`). Inserts set owner columns from **`sub`**, not from unverified client fields.
3. **Errors:** If a row does not exist **for that user**, return **404** or **403** consistently (pick one policy per resource type and document it).

**Exit criteria:** Code review can answer “where is `sub` in this query?” for each new endpoint.

---

## Phase 6 — RLS for client → Supabase

1. List tables the **mobile/web app** hits with **anon + user JWT** (not through FastAPI).
2. Ensure **RLS** policies use `auth.uid()` (or your product’s equivalent) so those paths remain safe. Service-role BFF queries **do not** get this protection.

**Exit criteria:** Direct PostgREST access cannot read another user’s rows in a smoke test.

---

## Phase 7 — Tests and hardening

- Automated or manual: missing header → 401; malformed token → 401; valid token but wrong resource → 403/404 per policy.
- Logging: never print Bearer tokens or service role values.

---

## Phase 8 — Rollout

1. Configure staging with real-shaped secrets (not production keys if policy forbids).
2. Smoke-test with a real access token from Supabase Auth (sign-in flow or dashboard).
3. Deploy; monitor 401 rate for client header bugs.

---

## Quick order checklist

| Order | Phase |
|------:|--------|
| 1 | Locked decision (`04`) — done |
| 2 | Env + service-role client naming |
| 3 | JWT verify dependency → `sub` |
| 4 | Wire dependency on scoped routes + matching URL fix |
| 5 | Repository query scoping |
| 6 | RLS for direct Supabase |
| 7 | Tests + log hygiene |
| 8 | Staging → production |

---

## References

- FastAPI [Security](https://fastapi.tiangolo.com/tutorial/security/first-steps/) and [Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- Supabase [JWT overview](https://supabase.com/docs/guides/auth/jwts) and Python [create_client](https://supabase.com/docs/reference/python/initializing)
