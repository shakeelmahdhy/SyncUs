# FastAPI + Supabase-first implementation strategy

## Layering rule (keep modules independent)

- `router.py`: HTTP endpoints, response_model/request body validation
- `schema.py`: Pydantic request/response contracts (OpenAPI source of truth)
- `service.py`: business logic and workflow transitions (MVP rules)
- `repository.py` (recommended): Supabase query calls (data access details)
- `model.py` (optional): ORM model only if you use SQLAlchemy

Official FastAPI docs:
- Request bodies: https://fastapi.tiangolo.com/tutorial/body/
- Response model: https://fastapi.tiangolo.com/tutorial/response-model/
- Path params: https://fastapi.tiangolo.com/tutorial/path-params/
- Bigger apps / routers: https://fastapi.tiangolo.com/tutorial/bigger-applications/
- Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/

Supabase Python docs:
- Python client intro: https://supabase.com/docs/reference/python/introduction
- Python initializing: https://supabase.com/docs/reference/python/initializing
- Auth - get user: https://supabase.com/docs/reference/python/auth-getuser
- Auth - set session: https://supabase.com/docs/reference/python/auth-setsession
- RLS overview: https://supabase.com/docs/guides/database/postgres/row-level-security

---

## Canonical job table

All backend job CRUD and search use **`public.jobs`** (`id`, `employer_id`, `title`, `description`, `required_skills`, `location`, `work_mode`, `experience_required`, `status`, `created_at`). API field `job_id` maps to column `id`. The legacy `job_postings` name is not used.

---

## Auth approach inside FastAPI (choose one)

Option A (fast MVP, code-enforced authorization):
- Use Supabase service-role key in backend
- Verify “current user” and enforce permissions in code

Option B (RLS-driven):
- Verify JWT from `Authorization: Bearer <token>`
- Set session in the Supabase client using access token + refresh token
- Let RLS policies enforce `auth.uid()`-based access

For RLS-driven, you typically use:
- `supabase.auth.set_session(access_token, refresh_token)`
  - https://supabase.com/docs/reference/python/auth-setsession

