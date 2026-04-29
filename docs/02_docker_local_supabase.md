# Docker and local Supabase CLI

Docker is required when you run Supabase CLI commands that start local containers, for example:
- `supabase start`
- `supabase db reset`
- `supabase db push` (local targeting)

If Docker is not running/installed, commands like `supabase db reset` will fail with port conflicts or Docker daemon connection errors.

Official Docker prerequisite:
- https://docs.docker.com/desktop/

Supabase local development overview:
- https://supabase.com/docs/guides/local-development

