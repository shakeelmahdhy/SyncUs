"""Tests for jobs API mapping."""

from uuid import UUID

from app.modules.jobs.mapping import row_to_job


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
            "status": "published",
            "created_at": "2025-03-01T10:00:00+00:00",
        },
        company_name="SyncUs",
        applications_count=3,
    )

    assert job.job_id == UUID("11111111-1111-1111-1111-111111111111")
    assert job.company_name == "SyncUs"
    assert job.applications_count == 3
