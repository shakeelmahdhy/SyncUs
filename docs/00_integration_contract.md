# SyncUs Integration Contract

Phase 0 source of truth for backend, frontend, and data work. If an implementation disagrees with this file, update the implementation or change this contract first.

## Database ownership

Canonical user identity is the Supabase Auth JWT `sub`. Store it as a UUID and treat it as the owner id for user-owned rows.

| Table | Primary id | Owner / identity rule | Notes |
| --- | --- | --- | --- |
| `auth.users` | `id` | Supabase Auth source of truth | JWT `sub` must match this UUID. |
| `job_seekers` | `id` | `id = auth.users.id = JWT sub` | Job seeker profile row. |
| `employers` | `id` | `id = auth.users.id = JWT sub` | Employer profile row. |
| `jobs` | `id` | `employer_id = employers.id = employer JWT sub` | Job owner scope for employer-only reads/writes. |
| `applications` | `id` | `job_seeker_id = job_seekers.id = seeker JWT sub` | Unique per `(job_id, job_seeker_id)`. |
| `resumes` | `id` | `job_seeker_id = seeker JWT sub` | At most one primary resume per seeker. |
| `matches` | `id` | References `jobs.id` and `job_seekers.id` | Derived matching result, not a user identity table. |
| `skills` | `id` | Global lookup | `name` is unique. |
| `job_seeker_skills` | `(job_seeker_id, skill_id)` | `job_seeker_id = seeker JWT sub` | Join table. |

## Auth standard

`backend/app/core/auth.py` is canonical for FastAPI authentication.

| Rule | Standard |
| --- | --- |
| Bearer token | `Authorization: Bearer <supabase_access_jwt>` |
| Verified user id | `CurrentUserIdDep`, derived from JWT `sub` |
| Full user object | `CurrentUserDep` |
| Token verification | `SUPABASE_JWT_SECRET`, HS256, audience `authenticated` |
| Authorization | Services/repositories scope every query by the verified `sub` |

`backend/app/core/dependencies.py` is legacy. Do not import it in new routes. Existing users should be retired in this order:

1. Replace `get_current_user`, `get_current_employer`, and `get_optional_user` with dependencies from `app.core.auth`.
2. Move role/profile checks into module services using rows scoped by `CurrentUserIdDep`.
3. Replace direct Supabase client creation with `app.core.supabase_client`.
4. Delete `app.core.dependencies` after no imports remain.

## Environment standard

Only these backend env vars are canonical:

| Variable | Used by | Purpose |
| --- | --- | --- |
| `SUPABASE_URL` | Backend Supabase clients | Project URL. |
| `SUPABASE_PUBLISHABLE_KEY` | Publishable/anon client | Client-safe Supabase API key. |
| `SUPABASE_SECRET_KEY` | Service client | Server-only key for FastAPI data access. |
| `SUPABASE_JWT_SECRET` | Auth dependency | Verifies Supabase access JWTs. |

`backend/.env.example` must not document alternate aliases such as `SUPABASE_KEY`, `SUPABASE_ANON_KEY`, or dev-only identity variables.

## Route map

FastAPI docs are available at `/api/docs`. The app mounts module routers once, at the public prefixes below.

| Area | Method | Path |
| --- | --- | --- |
| System | GET | `/` |
| System | GET | `/health` |
| Accounts | POST | `/accounts/profile` |
| Accounts | GET | `/accounts/profile/{user_id}` |
| Accounts | PATCH | `/accounts/profile/{user_id}` |
| Accounts | GET | `/accounts/profile/{user_id}/parse` |
| Accounts | POST | `/accounts/profile/{user_id}/resume` |
| Accounts | POST | `/accounts/profile/{user_id}/resume/upload` |
| Accounts | POST | `/accounts/auth/register` |
| Accounts | POST | `/accounts/auth/login` |
| Jobs | POST | `/jobs` |
| Jobs | GET | `/jobs` |
| Jobs | GET | `/jobs/{job_id}` |
| Jobs | PATCH | `/jobs/{job_id}` |
| Jobs | DELETE | `/jobs/{job_id}` |
| Jobs | POST | `/jobs/{job_id}/publish` |
| Jobs | POST | `/jobs/{job_id}/close` |
| Jobs | GET | `/jobs/employer/my-jobs` |
| Jobs | GET | `/jobs/stats/overview` |
| Matching | GET | `/matching/recommendations` |
| Matching | GET | `/matching/jobs/{job_id}/candidates` |
| Matching | GET | `/matching/explanations/{match_id}` |
| Matching | POST | `/matching/recompute` |
| Tracking | POST | `/tracking/applications` |
| Tracking | GET | `/tracking/applications` |
| Tracking | GET | `/tracking/applications/{application_id}` |
| Tracking | PATCH | `/tracking/applications/{application_id}/status` |
| Tracking | GET | `/tracking/jobs/{job_id}/pipeline` |
| Search | GET | `/search/jobs` |
| Search | GET | `/search/candidates` |

Do not add router-level version strings such as `/skill-sync/v1` or `/sync-us/v1` inside module routers. Versioning belongs at a single API gateway or top-level router boundary if the project adds it later.
