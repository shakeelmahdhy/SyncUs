"""Regression tests for enhanced job search relevance and filters."""

from __future__ import annotations

import asyncio

from app.modules.search.models import CandidateFilterRequest, JobSearchRequest, SortOrder
from app.modules.search.service import SearchService


class _Response:
    def __init__(self, data, count=None):
        self.data = data
        self.count = len(data) if count is None else count


class _Query:
    def __init__(self, client: "_FakeClient", table_name: str):
        self.client = client
        self.table_name = table_name
        self.filters: list[tuple[str, str]] = []
        self.in_filters: list[tuple[str, set[str]]] = []
        self.limit_count: int | None = None

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, column: str, value):
        self.filters.append((column, str(value)))
        return self

    def in_(self, column: str, values):
        self.in_filters.append((column, {str(value) for value in values}))
        return self

    def limit(self, count: int):
        self.limit_count = count
        return self

    def execute(self):
        rows = list(self.client.tables.get(self.table_name, []))
        for column, value in self.filters:
            rows = [row for row in rows if str(row.get(column)) == value]
        for column, values in self.in_filters:
            rows = [row for row in rows if str(row.get(column)) in values]
        if self.limit_count is not None:
            rows = rows[: self.limit_count]
        return _Response(rows)


class _FakeClient:
    def __init__(self, tables):
        self.tables = tables

    def table(self, table_name: str):
        return _Query(self, table_name)


def _job(
    job_id: str,
    title: str,
    *,
    description: str,
    skills: list[str],
    location: str,
    work_mode: str,
    experience_level: str,
    employer_id: str = "employer-1",
    created_at: str = "2026-01-01T00:00:00+00:00",
):
    return {
        "id": job_id,
        "employer_id": employer_id,
        "title": title,
        "description": description,
        "required_skills": skills,
        "location": location,
        "work_mode": work_mode,
        "experience_required": 0 if experience_level == "entry" else 2,
        "experience_level": experience_level,
        "education_level": "any",
        "salary_min": 90000,
        "salary_max": 130000,
        "status": "published",
        "created_at": created_at,
        "views_count": 0,
        "applications_count": 0,
    }


def _service():
    return SearchService(
        _FakeClient(
            {
                "employers": [
                    {
                        "id": "employer-1",
                        "company_name": "PlatformWorks",
                        "company_description": "Builds developer tooling and cloud software.",
                        "industry": "Technology",
                    },
                    {
                        "id": "employer-2",
                        "company_name": "InsightLab",
                        "company_description": "Data analytics consulting.",
                        "industry": "Analytics",
                    },
                ],
                "jobs": [
                    _job(
                        "job-software",
                        "Software Engineer",
                        description="Build backend APIs and web applications with Python and React.",
                        skills=["Python", "React", "APIs"],
                        location="Sydney, NSW",
                        work_mode="hybrid",
                        experience_level="mid",
                        employer_id="employer-1",
                        created_at="2026-02-01T00:00:00+00:00",
                    ),
                    _job(
                        "job-data-remote-entry",
                        "Data Analyst",
                        description="Entry-level analytics role using SQL dashboards and reporting.",
                        skills=["SQL", "Tableau", "Analytics"],
                        location="Melbourne, VIC",
                        work_mode="remote",
                        experience_level="entry",
                        employer_id="employer-2",
                        created_at="2026-03-01T00:00:00+00:00",
                    ),
                    _job(
                        "job-data-onsite-senior",
                        "Senior Data Analyst",
                        description="Lead analytics projects for enterprise clients.",
                        skills=["SQL", "Python", "Statistics"],
                        location="Sydney, NSW",
                        work_mode="onsite",
                        experience_level="senior",
                        employer_id="employer-2",
                        created_at="2026-04-01T00:00:00+00:00",
                    ),
                    _job(
                        "job-designer",
                        "Product Designer",
                        description="Design research and product workflows.",
                        skills=["Figma", "Research"],
                        location="Sydney, NSW",
                        work_mode="remote",
                        experience_level="entry",
                        employer_id="employer-1",
                        created_at="2026-05-01T00:00:00+00:00",
                    ),
                ],
                "job_seekers": [
                    {
                        "id": "candidate-1",
                        "first_name": "Ava",
                        "last_name": "Singh",
                        "education": "Bachelor",
                        "major": "Software Engineering",
                        "years_of_experience": 2,
                        "academic_units": ["Algorithms", "Cloud Computing"],
                        "location": "Sydney, NSW",
                        "work_mode": "remote",
                    },
                    {
                        "id": "candidate-2",
                        "first_name": "Mia",
                        "last_name": "Torres",
                        "education": "Bachelor",
                        "major": "Visual Design",
                        "years_of_experience": 3,
                        "academic_units": ["Research"],
                        "location": "Melbourne, VIC",
                        "work_mode": "hybrid",
                    },
                ],
                "job_seeker_skills": [
                    {"job_seeker_id": "candidate-1", "skill_id": "skill-python"},
                    {"job_seeker_id": "candidate-1", "skill_id": "skill-react"},
                    {"job_seeker_id": "candidate-2", "skill_id": "skill-figma"},
                ],
                "skills": [
                    {"id": "skill-python", "name": "Python"},
                    {"id": "skill-react", "name": "React"},
                    {"id": "skill-figma", "name": "Figma"},
                ],
            }
        )
    )


def _search(**kwargs):
    request = JobSearchRequest(page_size=20, sort_by=SortOrder.RELEVANCE, **kwargs)
    return asyncio.run(_service().search_jobs(request))


def _ids(response):
    return [result.job_id for result in response.results]


def test_exact_keyword_search_returns_software_engineer_first():
    response = _search(keyword="Software Engineer")

    assert _ids(response)[0] == "job-software"


def test_location_filter_search_limits_results():
    response = _search(location="Sydney")

    assert set(_ids(response)) == {"job-software", "job-data-onsite-senior", "job-designer"}


def test_work_mode_and_employment_type_filter_search():
    response = _search(work_mode="Remote", employment_type="Full-time")

    assert set(_ids(response)) == {"job-data-remote-entry", "job-designer"}


def test_keyword_and_filters_are_combined():
    response = _search(keyword="Data Analyst", work_mode="Remote", experience_level="Entry-Level")

    assert _ids(response) == ["job-data-remote-entry"]


def test_fuzzy_typo_search_returns_software_engineer():
    response = _search(keyword="sofware enginer")

    assert _ids(response)[0] == "job-software"


def test_related_terms_return_software_engineering_jobs():
    programmer = _search(keyword="programmer")
    coder = _search(keyword="coder")

    assert _ids(programmer)[0] == "job-software"
    assert _ids(coder)[0] == "job-software"


def test_candidate_keyword_search_checks_profile_skills_and_preferences():
    response = asyncio.run(
        _service().filter_candidates(
            request=CandidateFilterRequest(
                keyword="coder",
                location="Sydney",
                available_for="remote",
                page_size=20,
            )
        )
    )

    assert [candidate.candidate_id for candidate in response.results] == ["candidate-1"]
