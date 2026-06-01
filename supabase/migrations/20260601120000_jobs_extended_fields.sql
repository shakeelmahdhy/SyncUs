-- Persist full job posting fields used by the Jobs API (PostJobPage / JobCreate).

alter table public.jobs
  add column if not exists education_level text default 'any',
  add column if not exists experience_level text default 'any',
  add column if not exists max_years_experience integer,
  add column if not exists salary_min integer,
  add column if not exists salary_max integer,
  add column if not exists contact_email text,
  add column if not exists website text;

comment on column public.jobs.education_level is 'Minimum education: high_school, associate, bachelor, master, phd, any';
comment on column public.jobs.experience_level is 'Seniority band: entry, junior, mid, senior, lead, any';
comment on column public.jobs.max_years_experience is 'Maximum years of experience (min stored in experience_required)';
comment on column public.jobs.salary_min is 'Minimum salary in job currency units';
comment on column public.jobs.salary_max is 'Maximum salary in job currency units';
comment on column public.jobs.contact_email is 'Application contact email for this posting';
comment on column public.jobs.website is 'Optional company or role website URL';
