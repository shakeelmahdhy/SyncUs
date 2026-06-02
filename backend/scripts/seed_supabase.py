r"""Seed Supabase with SyncUs sample data.

Run from ``backend``:

    .\venv\Scripts\python .\scripts\seed_supabase.py

Optional reset of the sample rows only:

    .\venv\Scripts\python .\scripts\seed_supabase.py --reset

The script uses backend/.env and requires SUPABASE_URL plus SUPABASE_SECRET_KEY.
Sample emails intentionally use generic local parts such as user1/employer1.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(BACKEND_ROOT / ".env")

from app.core.supabase_client import create_supabase_service_client  # noqa: E402


SEED_DOMAIN = "syncus-seed.test"
PASSWORD = "Password123!"
NOW = datetime.now(timezone.utc)


EMPLOYERS = [
    {
        "key": "employer1",
        "email": f"employer1@{SEED_DOMAIN}",
        "company_name": "SyncUs Labs",
        "company_description": "Sample employer account for testing SyncUs hiring flows.",
        "industry": "Software",
        "first_name": "Employer",
        "last_name": "One",
    },
    {
        "key": "employer2",
        "email": f"employer2@{SEED_DOMAIN}",
        "company_name": "Northstar Digital",
        "company_description": "Sample employer account for testing analytics and applicant review.",
        "industry": "Technology Consulting",
        "first_name": "Employer",
        "last_name": "Two",
    },
]

USERS = [
    {
        "key": "user1",
        "email": f"user1@{SEED_DOMAIN}",
        "first_name": "User",
        "last_name": "One",
        "phone": "+61 400 000 001",
        "education": "Bachelor",
        "major": "Software Engineering",
        "years_of_experience": 3,
        "academic_units": ["Cloud Computing", "Database Systems", "Web Development"],
        "skills": ["python", "fastapi", "react", "typescript", "sql"],
    },
    {
        "key": "user2",
        "email": f"user2@{SEED_DOMAIN}",
        "first_name": "User",
        "last_name": "Two",
        "phone": "+61 400 000 002",
        "education": "Master",
        "major": "UX Design",
        "years_of_experience": 2,
        "academic_units": ["Human Computer Interaction", "Product Design"],
        "skills": ["figma", "user research", "product strategy", "react"],
    },
    {
        "key": "user3",
        "email": f"user3@{SEED_DOMAIN}",
        "first_name": "User",
        "last_name": "Three",
        "phone": "+61 400 000 003",
        "education": "Bachelor",
        "major": "Data Analytics",
        "years_of_experience": 4,
        "academic_units": ["Machine Learning", "Statistics", "Data Visualisation"],
        "skills": ["python", "sql", "machine learning", "analytics"],
    },
]

JOBS = [
    {
        "key": "job1",
        "employer_key": "employer1",
        "title": "Backend Platform Engineer",
        "description": (
            "Build and maintain FastAPI services for a job matching platform. "
            "This role works across authentication, tracking, search, and integrations "
            "with Supabase while keeping APIs reliable and easy for frontend teams to use."
        ),
        "required_skills": ["python", "fastapi", "sql", "supabase"],
        "location": "Sydney, NSW",
        "work_mode": "hybrid",
        "education_level": "bachelor",
        "experience_level": "mid",
        "experience_required": 2,
        "max_years_experience": 6,
        "salary_min": 95000,
        "salary_max": 130000,
        "status": "published",
    },
    {
        "key": "job2",
        "employer_key": "employer1",
        "title": "Frontend Product Engineer",
        "description": (
            "Create polished React interfaces for job seekers and employers. "
            "You will wire live backend data into dashboards, job search, application "
            "tracking, and profile flows using TypeScript and thoughtful UI patterns."
        ),
        "required_skills": ["react", "typescript", "figma", "api integration"],
        "location": "Melbourne, VIC",
        "work_mode": "remote",
        "education_level": "any",
        "experience_level": "junior",
        "experience_required": 1,
        "max_years_experience": 4,
        "salary_min": 85000,
        "salary_max": 115000,
        "status": "published",
    },
    {
        "key": "job3",
        "employer_key": "employer2",
        "title": "Data Insights Analyst",
        "description": (
            "Analyse hiring, candidate, and product usage data to identify trends. "
            "The role suits someone comfortable with SQL, Python, dashboards, and "
            "turning ambiguous business questions into clear reporting."
        ),
        "required_skills": ["sql", "python", "analytics", "data visualisation"],
        "location": "Brisbane, QLD",
        "work_mode": "hybrid",
        "education_level": "bachelor",
        "experience_level": "mid",
        "experience_required": 3,
        "max_years_experience": 7,
        "salary_min": 90000,
        "salary_max": 125000,
        "status": "published",
    },
    {
        "key": "job4",
        "employer_key": "employer2",
        "title": "Draft UX Researcher",
        "description": (
            "Plan discovery research for employer workflows, candidate journeys, "
            "and product onboarding. This draft role is seeded so the employer "
            "dashboard can show unpublished jobs and publish actions."
        ),
        "required_skills": ["user research", "figma", "product strategy"],
        "location": "Sydney, NSW",
        "work_mode": "onsite",
        "education_level": "any",
        "experience_level": "mid",
        "experience_required": 2,
        "max_years_experience": 5,
        "salary_min": 80000,
        "salary_max": 105000,
        "status": "draft",
    },
]

APPLICATIONS = [
    {"user_key": "user1", "job_key": "job1", "status": "applied"},
    {"user_key": "user1", "job_key": "job2", "status": "shortlisted"},
    {"user_key": "user2", "job_key": "job2", "status": "interview"},
    {"user_key": "user3", "job_key": "job3", "status": "offered"},
]

MATCHES = [
    {
        "user_key": "user1",
        "job_key": "job1",
        "score": 0.91,
        "breakdown_json": {"skill": 0.95, "profile": 0.86, "experience": 1.0, "location": 1.0, "work_mode": 1.0},
    },
    {
        "user_key": "user2",
        "job_key": "job2",
        "score": 0.88,
        "breakdown_json": {"skill": 0.9, "profile": 0.82, "experience": 1.0, "location": 0.7, "work_mode": 1.0},
    },
    {
        "user_key": "user3",
        "job_key": "job3",
        "score": 0.93,
        "breakdown_json": {"skill": 1.0, "profile": 0.88, "experience": 1.0, "location": 0.8, "work_mode": 1.0},
    },
]


def iso(days_ago: int = 0) -> str:
    return (NOW - timedelta(days=days_ago)).isoformat()


def response_rows(response: Any) -> list[dict[str, Any]]:
    return list(getattr(response, "data", None) or [])


def table_has_column(client: Any, table: str, column: str) -> bool:
    try:
        client.table(table).select(column).limit(1).execute()
        return True
    except Exception:
        return False


def upsert_by_id(client: Any, table: str, row: dict[str, Any]) -> dict[str, Any]:
    existing = (
        client.table(table)
        .select("id")
        .eq("id", row["id"])
        .limit(1)
        .execute()
    )
    if response_rows(existing):
        response = client.table(table).update(row).eq("id", row["id"]).execute()
    else:
        response = client.table(table).insert(row).execute()

    rows = response_rows(response)
    return rows[0] if rows else row


def delete_where_in(client: Any, table: str, column: str, values: list[str]) -> None:
    if values:
        client.table(table).delete().in_(column, values).execute()


def auth_users_page(client: Any, page: int, per_page: int) -> list[Any]:
    result = client.auth.admin.list_users(page=page, per_page=per_page)
    users = getattr(result, "users", None)
    if users is not None:
        return list(users)
    if isinstance(result, list):
        return result
    return []


def find_auth_user_by_email(client: Any, email: str) -> Any | None:
    page = 1
    per_page = 100
    target = email.lower()

    while True:
        users = auth_users_page(client, page, per_page)
        for user in users:
            if str(getattr(user, "email", "")).lower() == target:
                return user
        if len(users) < per_page:
            return None
        page += 1


def ensure_auth_user(client: Any, account: dict[str, Any], account_type: str) -> str:
    existing = find_auth_user_by_email(client, account["email"])
    if existing is not None:
        user_id = getattr(existing, "id", None)
        if user_id:
            return str(user_id)

    response = client.auth.admin.create_user(
        {
            "email": account["email"],
            "password": PASSWORD,
            "email_confirm": True,
            "user_metadata": {
                "account_type": account_type,
                "seeded": True,
                "seed_key": account["key"],
            },
        }
    )
    user = getattr(response, "user", None)
    user_id = getattr(user, "id", None)
    if not user_id:
        raise RuntimeError(f"Auth user creation returned no id for {account['email']}")
    return str(user_id)


def seed_employers(client: Any) -> dict[str, str]:
    ids: dict[str, str] = {}
    for employer in EMPLOYERS:
        user_id = ensure_auth_user(client, employer, "employer")
        row = {
            "id": user_id,
            "company_name": employer["company_name"],
            "company_description": employer["company_description"],
            "industry": employer["industry"],
            "is_verified": True,
            "email": employer["email"],
            "first_name": employer["first_name"],
            "last_name": employer["last_name"],
            "membership": True,
        }
        upsert_by_id(client, "employers", row)
        ids[employer["key"]] = user_id
    return ids


def seed_skills(client: Any, skill_names: list[str]) -> dict[str, str]:
    skill_ids: dict[str, str] = {}
    for name in sorted({skill.strip().lower() for skill in skill_names if skill.strip()}):
        existing = client.table("skills").select("id, name").eq("name", name).limit(1).execute()
        rows = response_rows(existing)
        if rows:
            skill_ids[name] = rows[0]["id"]
            continue

        inserted = client.table("skills").insert({"name": name}).execute()
        rows = response_rows(inserted)
        if not rows:
            raise RuntimeError(f"Skill insert returned no row for {name}")
        skill_ids[name] = rows[0]["id"]
    return skill_ids


def seed_job_seekers(client: Any, skill_ids: dict[str, str]) -> dict[str, str]:
    ids: dict[str, str] = {}
    for user in USERS:
        user_id = ensure_auth_user(client, user, "job_seeker")
        row: dict[str, Any] = {
            "id": user_id,
            "user_id": user_id,
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "education": user["education"],
            "major": user["major"],
            "years_of_experience": user["years_of_experience"],
            "academic_units": user["academic_units"],
            "phone": user["phone"],
            "email": user["email"],
            "location": "Sydney, NSW",
            "bio": "Sample profile used to test SyncUs job matching and application flows.",
            "work_experience": f"{user['years_of_experience']} years of project experience.",
            "skills": user["skills"],
            "preferred_working_mode": "hybrid",
            "preferred_location": "Sydney, NSW",
            "is_active": True,
            "membership": True,
        }

        upsert_by_id(client, "job_seekers", row)
        ids[user["key"]] = user_id

        client.table("job_seeker_skills").delete().eq("job_seeker_id", user_id).execute()
        links = [
            {"job_seeker_id": user_id, "skill_id": skill_ids[skill.lower()]}
            for skill in user["skills"]
            if skill.lower() in skill_ids
        ]
        if links:
            client.table("job_seeker_skills").insert(links).execute()

    return ids


def seed_jobs(client: Any, employer_ids: dict[str, str]) -> dict[str, str]:
    ids: dict[str, str] = {}
    created_at_by_index = [iso(8), iso(6), iso(4), iso(2)]

    for index, job in enumerate(JOBS):
        existing = (
            client.table("jobs")
            .select("id")
            .eq("title", job["title"])
            .eq("employer_id", employer_ids[job["employer_key"]])
            .limit(1)
            .execute()
        )
        existing_rows = response_rows(existing)
        job_id = existing_rows[0]["id"] if existing_rows else None

        row: dict[str, Any] = {
            "employer_id": employer_ids[job["employer_key"]],
            "title": job["title"],
            "description": job["description"],
            "required_skills": job["required_skills"],
            "location": job["location"],
            "work_mode": job["work_mode"],
            "experience_required": job["experience_required"],
            "max_years_experience": job["max_years_experience"],
            "education_level": job["education_level"],
            "experience_level": job["experience_level"],
            "salary_min": job["salary_min"],
            "salary_max": job["salary_max"],
            "contact_email": f"{job['employer_key']}@{SEED_DOMAIN}",
            "website": "https://syncus.example/jobs",
            "status": job["status"],
            "created_at": created_at_by_index[index],
        }

        if job_id:
            row["id"] = job_id
            response = client.table("jobs").update(row).eq("id", job_id).execute()
        else:
            response = client.table("jobs").insert(row).execute()

        rows = response_rows(response)
        if not rows:
            raise RuntimeError(f"Job insert/update returned no row for {job['title']}")
        ids[job["key"]] = rows[0]["id"]

    return ids


def seed_resumes(client: Any, user_ids: dict[str, str]) -> dict[str, str]:
    resume_ids: dict[str, str] = {}
    for user in USERS:
        user_id = user_ids[user["key"]]
        resume_name = f"{user['key']}-resume.pdf"
        existing = (
            client.table("resumes")
            .select("id")
            .eq("job_seeker_id", user_id)
            .eq("resume_name", resume_name)
            .limit(1)
            .execute()
        )
        rows = response_rows(existing)
        row = {
            "job_seeker_id": user_id,
            "resume_name": resume_name,
            "file_url": f"https://example.com/syncus-seed/{resume_name}",
            "is_primary": True,
        }
        if rows:
            resume_id = rows[0]["id"]
            client.table("resumes").update(row).eq("id", resume_id).execute()
        else:
            inserted = client.table("resumes").insert(row).execute()
            inserted_rows = response_rows(inserted)
            if not inserted_rows:
                raise RuntimeError(f"Resume insert returned no row for {resume_name}")
            resume_id = inserted_rows[0]["id"]
        resume_ids[user["key"]] = resume_id
    return resume_ids


def seed_applications(
    client: Any,
    user_ids: dict[str, str],
    job_ids: dict[str, str],
    resume_ids: dict[str, str],
) -> None:
    for item in APPLICATIONS:
        user_id = user_ids[item["user_key"]]
        job_id = job_ids[item["job_key"]]
        existing = (
            client.table("applications")
            .select("id")
            .eq("job_seeker_id", user_id)
            .eq("job_id", job_id)
            .limit(1)
            .execute()
        )
        rows = response_rows(existing)
        row = {
            "job_id": job_id,
            "job_seeker_id": user_id,
            "resume_id": resume_ids.get(item["user_key"]),
            "status": item["status"],
        }
        if rows:
            client.table("applications").update(row).eq("id", rows[0]["id"]).execute()
        else:
            client.table("applications").insert(row).execute()


def seed_matches(client: Any, user_ids: dict[str, str], job_ids: dict[str, str]) -> None:
    for item in MATCHES:
        user_id = user_ids[item["user_key"]]
        job_id = job_ids[item["job_key"]]
        existing = (
            client.table("matches")
            .select("id")
            .eq("job_seeker_id", user_id)
            .eq("job_id", job_id)
            .limit(1)
            .execute()
        )
        rows = response_rows(existing)
        row = {
            "job_id": job_id,
            "job_seeker_id": user_id,
            "score": item["score"],
            "breakdown_json": item["breakdown_json"],
        }
        if rows:
            client.table("matches").update(row).eq("id", rows[0]["id"]).execute()
        else:
            client.table("matches").insert(row).execute()


def reset_seed_rows(client: Any) -> None:
    seed_emails = [account["email"] for account in [*EMPLOYERS, *USERS]]
    auth_ids = []
    for email in seed_emails:
        user = find_auth_user_by_email(client, email)
        if user is not None and getattr(user, "id", None):
            auth_ids.append(str(user.id))

    job_rows = (
        client.table("jobs")
        .select("id")
        .in_("title", [job["title"] for job in JOBS])
        .execute()
    )
    job_ids = [row["id"] for row in response_rows(job_rows)]

    delete_where_in(client, "applications", "job_id", job_ids)
    delete_where_in(client, "matches", "job_id", job_ids)
    delete_where_in(client, "resumes", "job_seeker_id", auth_ids)
    delete_where_in(client, "job_seeker_skills", "job_seeker_id", auth_ids)
    delete_where_in(client, "jobs", "id", job_ids)
    delete_where_in(client, "job_seekers", "id", auth_ids)
    delete_where_in(client, "employers", "id", auth_ids)

    for auth_id in auth_ids:
        try:
            client.auth.admin.delete_user(auth_id)
        except Exception as exc:
            print(f"Skipped deleting auth user {auth_id}: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed SyncUs Supabase sample data.")
    parser.add_argument("--reset", action="store_true", help="Delete existing sample rows before seeding.")
    args = parser.parse_args()

    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_SECRET_KEY"):
        raise RuntimeError("SUPABASE_URL and SUPABASE_SECRET_KEY must be set in backend/.env")

    client = create_supabase_service_client()

    if args.reset:
        print("Resetting existing SyncUs sample rows...")
        reset_seed_rows(client)

    all_skills = [
        skill
        for collection in (
            [skill for user in USERS for skill in user["skills"]],
            [skill for job in JOBS for skill in job["required_skills"]],
        )
        for skill in collection
    ]

    employer_ids = seed_employers(client)
    skill_ids = seed_skills(client, all_skills)
    user_ids = seed_job_seekers(client, skill_ids)
    job_ids = seed_jobs(client, employer_ids)
    resume_ids = seed_resumes(client, user_ids)
    seed_applications(client, user_ids, job_ids, resume_ids)
    seed_matches(client, user_ids, job_ids)

    print("Seed complete.")
    print(f"Created/updated {len(EMPLOYERS)} employers, {len(USERS)} users, {len(JOBS)} jobs.")
    print("Sample login password for all seeded accounts:", PASSWORD)
    print("Employer emails:", ", ".join(employer["email"] for employer in EMPLOYERS))
    print("User emails:", ", ".join(user["email"] for user in USERS))


if __name__ == "__main__":
    main()
