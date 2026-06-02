from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.core.auth import (
    CurrentUser,
    get_current_candidate,
    get_current_employer,
    get_current_user,
    get_current_user_id,
    get_optional_user,
)
from app.main import app
from app.modules.jobs.models import Job, JobListResponse
from app.modules.jobs.router import get_job_service
from app.modules.search.router import get_search_service


EMPLOYER_ID = UUID("11111111-1111-1111-1111-111111111111")
CANDIDATE_ID = UUID("22222222-2222-2222-2222-222222222222")
JOB_ID = UUID("33333333-3333-3333-3333-333333333333")
APPLICATION_ID = UUID("44444444-4444-4444-4444-444444444444")
RESUME_ID = UUID("55555555-5555-5555-5555-555555555555")
MATCH_ID = UUID("66666666-6666-6666-6666-666666666666")
NOW = "2026-06-02T04:00:00+00:00"


@pytest.fixture
def client():
    app.dependency_overrides.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def auth_as_candidate() -> None:
    user = CurrentUser(sub=CANDIDATE_ID, email="candidate@example.com", role="job_seeker")
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_current_user_id] = lambda: CANDIDATE_ID
    app.dependency_overrides[get_current_candidate] = lambda: user
    app.dependency_overrides[get_optional_user] = lambda: user


def auth_as_employer() -> None:
    user = CurrentUser(sub=EMPLOYER_ID, email="employer@example.com", role="employer")
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_current_user_id] = lambda: EMPLOYER_ID
    app.dependency_overrides[get_current_employer] = lambda: user
    app.dependency_overrides[get_optional_user] = lambda: user


def job_payload() -> dict:
    return {
        "title": "Backend Engineer",
        "company_name": "SyncUs",
        "description": "Build and maintain SyncUs backend services with reliable API integrations.",
        "required_skills": ["python", "fastapi"],
        "location": "Sydney, NSW",
        "work_mode": "hybrid",
        "education_level": "any",
        "experience_level": "mid",
        "min_years_experience": 1,
        "max_years_experience": 5,
        "salary_min": 90000,
        "salary_max": 130000,
        "contact_email": "jobs@syncus.test",
        "website": "https://syncus.test",
    }


def job_response(status: str = "draft") -> dict:
    return {
        **job_payload(),
        "job_id": str(JOB_ID),
        "employer_id": str(EMPLOYER_ID),
        "status": status,
        "views_count": 3,
        "applications_count": 1,
        "created_at": NOW,
        "updated_at": NOW,
        "published_at": NOW if status == "published" else None,
        "closed_at": NOW if status == "closed" else None,
    }


def application_response(status: str = "applied") -> dict:
    return {
        "id": str(APPLICATION_ID),
        "job_id": str(JOB_ID),
        "job_seeker_id": str(CANDIDATE_ID),
        "resume_id": str(RESUME_ID),
        "status": status,
        "created_at": NOW,
    }


def profile_response() -> dict:
    return {
        "id": str(CANDIDATE_ID),
        "user_id": str(CANDIDATE_ID),
        "first_name": "Ava",
        "last_name": "Singh",
        "email": "candidate@example.com",
        "phone": "0400000000",
        "education": "Bachelor",
        "skills": ["Python"],
        "title": "Software Engineer",
        "experience": "2",
        "academic_units": [],
    }


def profile_create_payload() -> dict:
    return {
        "user_id": str(CANDIDATE_ID),
        "first_name": "Ava",
        "last_name": "Singh",
        "email": "candidate@example.com",
        "phone": "0400000000",
        "location": "Sydney, NSW",
        "bio": "Backend-focused candidate",
    }


def job_list_response(status: str = "draft", page: int = 1, page_size: int = 10) -> JobListResponse:
    return JobListResponse(
        jobs=[Job(**job_response(status))],
        total=1,
        page=page,
        page_size=page_size,
        total_pages=1,
    )


class FakeJobService:
    async def create_job(self, job_data, employer_id, *, publish=False):
        assert employer_id == EMPLOYER_ID
        return job_response("published" if publish else "draft")

    async def get_employer_jobs(self, employer_id, status_filter=None, page=1, page_size=10):
        assert employer_id == EMPLOYER_ID
        return job_list_response(status_filter.value if status_filter else "draft", page, page_size)

    async def get_job_by_id(self, job_id, employer_id=None):
        assert job_id == JOB_ID
        return job_response("published")

    async def search_jobs(self, filters):
        return job_list_response("published", filters.page, filters.page_size)

    async def update_job(self, job_id, job_data, employer_id):
        assert job_id == JOB_ID
        assert employer_id == EMPLOYER_ID
        return {**job_response("draft"), "title": job_data.title or "Backend Engineer"}

    async def publish_job(self, job_id, employer_id):
        assert job_id == JOB_ID
        assert employer_id == EMPLOYER_ID
        return {
            "job_id": str(job_id),
            "status": "published",
            "published_at": NOW,
            "message": "Job posting published successfully",
        }

    async def close_job(self, job_id, employer_id):
        assert job_id == JOB_ID
        assert employer_id == EMPLOYER_ID
        return {
            "job_id": str(job_id),
            "status": "closed",
            "closed_at": NOW,
            "message": "Job posting closed successfully",
        }

    async def delete_job(self, job_id, employer_id):
        assert job_id == JOB_ID
        assert employer_id == EMPLOYER_ID
        return {"message": "Job posting deleted successfully", "job_id": str(job_id)}


class FakeSearchService:
    async def search_jobs(self, request):
        return {
            "results": [
                {
                    "job_id": str(JOB_ID),
                    "title": "Backend Engineer",
                    "company_name": "SyncUs",
                    "location": "Sydney, NSW",
                    "work_mode": "hybrid",
                    "required_skills": ["python"],
                    "education_level": "any",
                    "experience_level": "mid",
                    "salary_min": 90000,
                    "salary_max": 130000,
                    "published_at": NOW,
                    "views_count": 3,
                    "applications_count": 1,
                }
            ],
            "total": 1,
            "page": request.page,
            "page_size": request.page_size,
            "total_pages": 1,
            "keyword_used": request.keyword,
        }

    async def filter_candidates(self, request):
        return {
            "results": [
                {
                    "candidate_id": str(CANDIDATE_ID),
                    "full_name": "Ava Singh",
                    "major": "Computer Science",
                    "education_level": "bachelor",
                    "skills": ["python"],
                    "location": "Sydney, NSW",
                    "gpa": 3.7,
                    "profile_completeness": 95,
                    "has_github": True,
                    "available_for": "full-time",
                }
            ],
            "total": 1,
            "page": request.page,
            "page_size": request.page_size,
            "total_pages": 1,
            "filters_applied": request.skill_tags or [],
        }


@dataclass
class FakeMatchingService:
    def get_job_recommendations(self, user_id):
        assert user_id == CANDIDATE_ID
        return [{"job_id": str(JOB_ID), "title": "Backend Engineer", "score": 0.9}]

    def get_candidate_recommendations(self, job_id, user_id):
        assert job_id == JOB_ID
        assert user_id == EMPLOYER_ID
        return [{"candidate_id": str(CANDIDATE_ID), "name": "Ava Singh", "score": 0.91}]

    def get_match_explanation(self, match_id, user_id):
        assert match_id == MATCH_ID
        return {"match_id": str(match_id), "score": 0.91, "breakdown": {"skill": 1.0}}

    def recompute_matches(self, user_id, job_id=None):
        return {"status": "recomputed", "matches_updated": 1, "job_id": str(job_id) if job_id else None}


def test_system_endpoints(client: TestClient) -> None:
    assert client.get("/health").json()["status"] == "healthy"
    assert client.get("/").json()["docs"] == "/docs"


def test_accounts_auth_endpoints(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.modules.accounts.router.register_user",
        lambda payload: {
            "access_token": "token",
            "user": {
                "id": str(CANDIDATE_ID),
                "email": payload.email,
                "account_type": payload.account_type,
            },
            "profile": profile_response(),
        },
    )
    monkeypatch.setattr(
        "app.modules.accounts.router.login_user",
        lambda payload: {
            "access_token": "token",
            "user": {
                "id": str(CANDIDATE_ID),
                "email": payload.email,
                "account_type": "job_seeker",
            },
        },
    )

    register = client.post(
        "/accounts/auth/register",
        json={
            "first_name": "Ava",
            "last_name": "Singh",
            "email": "candidate@example.com",
            "password": "password123",
            "account_type": "job_seeker",
        },
    )
    assert register.status_code == 200
    assert register.json()["access_token"] == "token"

    login = client.post(
        "/accounts/auth/login",
        json={"email": "candidate@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    assert login.json()["user"]["account_type"] == "job_seeker"


def test_account_profile_and_resume_endpoints(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    auth_as_candidate()
    monkeypatch.setattr("app.modules.accounts.router.create_user", lambda payload: profile_response())
    monkeypatch.setattr("app.modules.accounts.router.get_user_profile", lambda user_id: profile_response())
    monkeypatch.setattr("app.modules.accounts.router.update_user_profile", lambda user_id, payload: profile_response())
    monkeypatch.setattr(
        "app.modules.accounts.router.parse_profile_data",
        lambda user_id: {"user_id": str(user_id), "profile_completeness": 100, "missing_fields": [], "profile": profile_response()},
    )
    monkeypatch.setattr(
        "app.modules.accounts.router.list_user_resumes",
        lambda user_id: [{
            "id": str(RESUME_ID),
            "job_seeker_id": str(user_id),
            "resume_name": "resume.pdf",
            "file_url": "https://example.test/resume.pdf",
            "is_primary": True,
            "created_at": NOW,
        }],
    )
    monkeypatch.setattr(
        "app.modules.accounts.router.add_resume",
        lambda user_id, payload: {
            "id": str(RESUME_ID),
            "job_seeker_id": str(user_id),
            "resume_name": payload.resume_name,
            "file_url": payload.file_url,
            "is_primary": False,
            "created_at": NOW,
        },
    )
    monkeypatch.setattr(
        "app.modules.accounts.router.upload_resume_to_storage",
        lambda user_id, file: {
            "id": str(RESUME_ID),
            "job_seeker_id": str(user_id),
            "resume_name": file.filename,
            "file_url": "https://example.test/uploaded.pdf",
            "is_primary": False,
            "created_at": NOW,
        },
    )

    assert client.post("/accounts/profile", json=profile_create_payload()).status_code == 200
    assert client.get(f"/accounts/profile/{CANDIDATE_ID}").json()["first_name"] == "Ava"
    assert client.get(f"/accounts/profile/{CANDIDATE_ID}/parse").json()["profile_completeness"] == 100
    assert client.patch(f"/accounts/profile/{CANDIDATE_ID}", json={"first_name": "Ava"}).status_code == 200
    assert client.get(f"/accounts/profile/{CANDIDATE_ID}/resumes").json()["total"] == 1
    assert client.post(
        f"/accounts/profile/{CANDIDATE_ID}/resume",
        json={"resume_name": "resume.pdf", "file_url": "https://example.test/resume.pdf"},
    ).status_code == 200
    upload = client.post(
        f"/accounts/profile/{CANDIDATE_ID}/resume/upload",
        files={"file": ("resume.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert upload.status_code == 200
    assert upload.json()["resume_name"] == "resume.pdf"


def test_account_profile_rejects_other_user(client: TestClient) -> None:
    auth_as_candidate()
    other_user = UUID("77777777-7777-7777-7777-777777777777")

    response = client.get(f"/accounts/profile/{other_user}")

    assert response.status_code == 403


def test_jobs_endpoints(client: TestClient) -> None:
    auth_as_employer()
    app.dependency_overrides[get_job_service] = lambda: FakeJobService()

    assert client.post("/jobs?publish=true", json=job_payload()).json()["status"] == "published"
    assert client.get("/jobs/employer/my-jobs").json()["total"] == 1
    assert client.get("/jobs/stats/overview").json()["total_jobs"] == 1
    assert client.get(f"/jobs/{JOB_ID}").json()["job_id"] == str(JOB_ID)
    assert client.get("/jobs?keyword=backend&page_size=5").json()["total"] == 1
    assert client.patch(f"/jobs/{JOB_ID}", json={"title": "Platform Engineer"}).json()["title"] == "Platform Engineer"
    assert client.post(f"/jobs/{JOB_ID}/publish").json()["status"] == "published"
    assert client.post(f"/jobs/{JOB_ID}/close").json()["status"] == "closed"
    assert client.delete(f"/jobs/{JOB_ID}").json()["job_id"] == str(JOB_ID)


def test_jobs_employer_routes_require_auth(client: TestClient) -> None:
    for method, path in [
        ("post", "/jobs"),
        ("get", "/jobs/employer/my-jobs"),
        ("get", "/jobs/stats/overview"),
        ("patch", f"/jobs/{JOB_ID}"),
        ("post", f"/jobs/{JOB_ID}/publish"),
        ("post", f"/jobs/{JOB_ID}/close"),
        ("delete", f"/jobs/{JOB_ID}"),
    ]:
        response = client.request(method.upper(), path, json=job_payload() if method in {"post", "patch"} else None)
        assert response.status_code == 401


def test_tracking_endpoints(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    auth_as_candidate()
    monkeypatch.setattr("app.modules.tracking.router.create_application", lambda user_id, payload: application_response())
    monkeypatch.setattr(
        "app.modules.tracking.router.list_applications",
        lambda user_id: {"items": [application_response()], "total": 1},
    )
    monkeypatch.setattr("app.modules.tracking.router.get_application", lambda user_id, application_id: application_response())
    monkeypatch.setattr(
        "app.modules.tracking.router.update_application_status",
        lambda user_id, application_id, status: {
            "id": str(application_id),
            "status": status,
            "updated_at": datetime.now(UTC),
        },
    )
    monkeypatch.setattr(
        "app.modules.tracking.router.get_job_pipeline",
        lambda user_id, job_id: {"job_id": str(job_id), "applications": [application_response()]},
    )

    assert client.post("/tracking/applications", json={"job_id": str(JOB_ID), "resume_id": str(RESUME_ID)}).status_code == 200
    assert client.get("/tracking/applications").json()["total"] == 1
    assert client.get(f"/tracking/applications/{APPLICATION_ID}").json()["id"] == str(APPLICATION_ID)
    assert client.patch(f"/tracking/applications/{APPLICATION_ID}/status", json={"status": "withdrawn"}).json()["status"] == "withdrawn"
    assert client.get(f"/tracking/jobs/{JOB_ID}/pipeline").json()["job_id"] == str(JOB_ID)


def test_matching_endpoints(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    auth_as_candidate()
    monkeypatch.setattr("app.modules.matching.router._matching_service", lambda: FakeMatchingService())

    assert client.get("/matching/recommendations").json()[0]["score"] == 0.9
    assert client.get(f"/matching/explanations/{MATCH_ID}").json()["match_id"] == str(MATCH_ID)
    assert client.post("/matching/recompute").json()["status"] == "recomputed"

    auth_as_employer()
    assert client.get(f"/matching/jobs/{JOB_ID}/candidates").json()[0]["candidate_id"] == str(CANDIDATE_ID)
    assert client.post(f"/matching/recompute?job_id={JOB_ID}").json()["job_id"] == str(JOB_ID)


def test_search_endpoints(client: TestClient) -> None:
    auth_as_employer()
    app.dependency_overrides[get_search_service] = lambda: FakeSearchService()

    jobs = client.get("/search/jobs?keyword=backend&skills=python,fastapi")
    assert jobs.status_code == 200
    assert jobs.json()["results"][0]["job_id"] == str(JOB_ID)

    candidates = client.get("/search/candidates?skills=python")
    assert candidates.status_code == 200
    assert candidates.json()["results"][0]["candidate_id"] == str(CANDIDATE_ID)


def test_search_candidates_requires_employer(client: TestClient) -> None:
    response = client.get("/search/candidates")

    assert response.status_code == 401
