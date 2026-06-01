"""Tests for jobs API mapping."""

from uuid import UUID

from app.modules.jobs.mapping import job_create_to_row, row_to_job
from app.modules.jobs.models import (
    EducationLevel,
    ExperienceLevel,
    JobCreate,
    WorkMode,
)


def test_row_to_job_uses_tracking_application_count() -> None:
    job = row_to_job(
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "employer_id": "22222222-2222-2222-2222-222222222222",
            "title": "Product Designer",
            "description": "Design accessible workflows for a job matching product.",
            "required_skills": ["figma"],
            "location": "Sydney",
            "work_mode": "hybrid",
            "experience_required": 2,
            "education_level": "bachelor",
            "experience_level": "mid",
            "max_years_experience": 5,
            "salary_min": 90000,
            "salary_max": 120000,
            "contact_email": "careers@syncus.test",
            "website": "https://syncus.test",
            "status": "published",
            "created_at": "2025-03-01T10:00:00+00:00",
        },
        company_name="SyncUs",
        applications_count=3,
    )

    assert job.job_id == UUID("11111111-1111-1111-1111-111111111111")
    assert job.company_name == "SyncUs"
    assert job.applications_count == 3
    assert job.education_level == EducationLevel.BACHELOR
    assert job.experience_level == ExperienceLevel.MID
    assert job.max_years_experience == 5
    assert job.salary_min == 90000
    assert job.salary_max == 120000
    assert job.contact_email == "careers@syncus.test"
    assert job.website == "https://syncus.test"


def test_job_create_to_row_persists_extended_fields() -> None:
    employer_id = UUID("22222222-2222-2222-2222-222222222222")
    payload = JobCreate(
        title="Backend Engineer",
        company_name="SyncUs",
        description="Build APIs for an intelligent job matching platform with FastAPI.",
        required_skills=["python", "fastapi"],
        location="Sydney",
        work_mode=WorkMode.HYBRID,
        education_level=EducationLevel.MASTER,
        experience_level=ExperienceLevel.SENIOR,
        min_years_experience=3,
        max_years_experience=8,
        salary_min=110000,
        salary_max=140000,
        contact_email="hiring@syncus.test",
        website="https://syncus.test/jobs",
    )
    row = job_create_to_row(payload, employer_id)

    assert row["education_level"] == "master"
    assert row["experience_level"] == "senior"
    assert row["max_years_experience"] == 8
    assert row["salary_min"] == 110000
    assert row["salary_max"] == 140000
    assert row["contact_email"] == "hiring@syncus.test"
    assert row["website"] == "https://syncus.test/jobs"
