-- this migration perform the following fixes:
-- 1.Invalid array column definitions
--      academic_units ARRAY and required_skills ARRAY are not valid Postgres syntax.
--      Should be typed, e.g. text[] (or better: normalized relation tables).
-- 2. Missing NOT NULL on critical FKs
--      jobs.employer_id, applications.job_id, applications.job_seeker_id should likely be NOT NULL.
-- 3. Weak status modeling
--      status text for jobs and applications should be constrained (CHECK or enum) to prevent invalid values.
-- 4. UUID default function
--      uuid_generate_v4() requires uuid-ossp extension.
--      In Supabase, gen_random_uuid() is usually preferred (pgcrypto).
-- 5. No uniqueness protections
--      applications should probably prevent duplicate applies: UNIQUE(job_id, job_seeker_id).
--      matches should likely have UNIQUE(job_id, job_seeker_id) too.
-- 6. No indexes for common queries
--      Add indexes on applications(job_seeker_id, status), applications(job_id, status), matches(job_id, score DESC), etc.
-- 7. No RLS policies shown
--      For Supabase production/minimal-secure setup, RLS is essential.

-- 1) Ensure UUID generation function exists
create extension if not exists pgcrypto;

-- 2) Fix array column types (if currently untyped/invalid)
-- Use text[] for MVP. Skip if already correct.
alter table public.job_seekers
  alter column academic_units type text[] using coalesce(academic_units, '{}'::text[]);

alter table public.jobs
  alter column required_skills type text[] using coalesce(required_skills, '{}'::text[]);

alter table public.job_seekers
  alter column academic_units set default '{}'::text[];

alter table public.jobs
  alter column required_skills set default '{}'::text[];

-- 3) Enforce NOT NULL on critical foreign keys
alter table public.jobs
  alter column employer_id set not null;

alter table public.applications
  alter column job_id set not null,
  alter column job_seeker_id set not null;

alter table public.matches
  alter column job_id set not null,
  alter column job_seeker_id set not null;

-- 4) Add status constraints (MVP-safe)
alter table public.jobs
  alter column status set default 'draft',
  add constraint jobs_status_check
    check (status in ('draft', 'published', 'closed'));

alter table public.applications
  alter column status set default 'applied',
  add constraint applications_status_check
    check (status in ('applied', 'shortlisted', 'interview', 'offered', 'rejected', 'withdrawn'));

-- 5) Prevent duplicates
alter table public.applications
  add constraint applications_job_seeker_unique unique (job_id, job_seeker_id);

alter table public.matches
  add constraint matches_job_seeker_unique unique (job_id, job_seeker_id);

-- 6) Add useful indexes
create index if not exists jobs_employer_status_idx
  on public.jobs (employer_id, status);

create index if not exists applications_job_status_idx
  on public.applications (job_id, status);

create index if not exists applications_seeker_status_idx
  on public.applications (job_seeker_id, status);

create index if not exists matches_job_score_idx
  on public.matches (job_id, score desc);

create index if not exists matches_seeker_score_idx
  on public.matches (job_seeker_id, score desc);

-- 7) Enable RLS (if not enabled yet)
alter table public.employers enable row level security;
alter table public.job_seekers enable row level security;
alter table public.resumes enable row level security;
alter table public.jobs enable row level security;
alter table public.applications enable row level security;
alter table public.matches enable row level security;

-- 8) Minimal baseline policies (create only if missing)
do $$
begin
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public' and tablename = 'jobs' and policyname = 'jobs_public_published_select'
  ) then
    create policy jobs_public_published_select on public.jobs
      for select using (status = 'published');
  end if;

  if not exists (
    select 1 from pg_policies
    where schemaname = 'public' and tablename = 'jobs' and policyname = 'jobs_owner_all'
  ) then
    create policy jobs_owner_all on public.jobs
      for all using (auth.uid() = employer_id) with check (auth.uid() = employer_id);
  end if;

  if not exists (
    select 1 from pg_policies
    where schemaname = 'public' and tablename = 'applications' and policyname = 'applications_seeker_insert'
  ) then
    create policy applications_seeker_insert on public.applications
      for insert with check (auth.uid() = job_seeker_id);
  end if;

  if not exists (
    select 1 from pg_policies
    where schemaname = 'public' and tablename = 'applications' and policyname = 'applications_seeker_select'
  ) then
    create policy applications_seeker_select on public.applications
      for select using (auth.uid() = job_seeker_id);
  end if;
end $$;