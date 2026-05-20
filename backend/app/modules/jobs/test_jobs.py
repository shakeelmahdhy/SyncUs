"""
Unit Tests for Jobs Module
Test suite for job posting functionality
"""

import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch

from .models import (
    JobCreate,
    JobUpdate,
    JobStatus,
    WorkMode,
    EducationLevel,
    ExperienceLevel,
    JobSearchFilters
)
from .service import JobService
from fastapi import HTTPException


def _jobs_row(**overrides):
    """Minimal ``public.jobs`` row for service tests."""
    base = {
        "id": str(uuid4()),
        "employer_id": str(uuid4()),
        "title": "Test Job",
        "description": "A" * 100,
        "required_skills": ["python"],
        "location": "Sydney",
        "work_mode": "remote",
        "experience_required": 0,
        "status": "draft",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    base.update(overrides)
    return base


def _configure_supabase_tables(
    mock_supabase, jobs_table: Mock, company_name: str = "Test Company"
):
    """Route ``table('jobs')`` and ``table('employers')`` for service tests."""
    emp_table = Mock()
    emp_response = Mock()
    emp_response.data = [{"company_name": company_name}]
    emp_table.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
        emp_response
    )

    def table_side_effect(name):
        if name == "jobs":
            return jobs_table
        if name == "employers":
            return emp_table
        raise ValueError(f"unexpected table: {name}")

    mock_supabase.table.side_effect = table_side_effect


@pytest.fixture
def mock_supabase():
    """Mock Supabase client"""
    return Mock()


@pytest.fixture
def job_service(mock_supabase):
    """JobService instance with mocked Supabase"""
    return JobService(mock_supabase)


@pytest.fixture
def sample_job_data():
    """Sample job creation data"""
    return JobCreate(
        title="Senior Full Stack Developer",
        company_name="Tech Innovations Ltd",
        description="We are looking for an experienced full stack developer with strong skills in React and Python. The ideal candidate will have 5+ years of experience building scalable web applications.",
        required_skills=["React", "Python", "FastAPI", "PostgreSQL"],
        location="Sydney, NSW",
        work_mode=WorkMode.HYBRID,
        education_level=EducationLevel.BACHELOR,
        experience_level=ExperienceLevel.SENIOR,
        min_years_experience=5,
        max_years_experience=10,
        salary_min=120000,
        salary_max=160000,
        contact_email="careers@techinnovations.com.au",
        website="https://techinnovations.com.au"
    )


@pytest.fixture
def sample_employer_id():
    """Sample employer UUID"""
    return uuid4()


class TestJobModels:
    """Test Pydantic models for validation"""

    def test_job_create_valid(self, sample_job_data):
        """Test valid job creation data"""
        assert sample_job_data.title == "Senior Full Stack Developer"
        assert len(sample_job_data.required_skills) == 4
        assert sample_job_data.work_mode == WorkMode.HYBRID

    def test_job_create_invalid_email(self):
        """Test job creation with invalid email"""
        with pytest.raises(ValueError):
            JobCreate(
                title="Developer",
                company_name="Company",
                description="A" * 100,  # Valid length
                required_skills=["Python"],
                location="Sydney",
                work_mode=WorkMode.REMOTE,
                contact_email="invalid-email"  # Invalid format
            )

    def test_job_create_short_description(self):
        """Test job creation with too short description"""
        with pytest.raises(ValueError):
            JobCreate(
                title="Developer",
                company_name="Company",
                description="Too short",  # Less than 50 chars
                required_skills=["Python"],
                location="Sydney",
                work_mode=WorkMode.REMOTE,
                contact_email="test@example.com"
            )

    def test_job_create_no_skills(self):
        """Test job creation without required skills"""
        with pytest.raises(ValueError):
            JobCreate(
                title="Developer",
                company_name="Company",
                description="A" * 100,
                required_skills=[],  # Empty skills list
                location="Sydney",
                work_mode=WorkMode.REMOTE,
                contact_email="test@example.com"
            )

    def test_skills_normalization(self, sample_job_data):
        """Test that skills are normalized to lowercase"""
        job_data = JobCreate(
            title="Developer",
            company_name="Company",
            description="A" * 100,
            required_skills=["Python", "REACT", "FastAPI"],
            location="Sydney",
            work_mode=WorkMode.REMOTE,
            contact_email="test@example.com"
        )
        # Skills should be lowercase
        assert all(skill.islower() for skill in job_data.required_skills)

    def test_experience_range_validation(self):
        """Test that max experience must be >= min experience"""
        with pytest.raises(ValueError):
            JobCreate(
                title="Developer",
                company_name="Company",
                description="A" * 100,
                required_skills=["Python"],
                location="Sydney",
                work_mode=WorkMode.REMOTE,
                contact_email="test@example.com",
                min_years_experience=10,
                max_years_experience=5  # Invalid: max < min
            )

    def test_salary_range_validation(self):
        """Test that max salary must be >= min salary"""
        with pytest.raises(ValueError):
            JobCreate(
                title="Developer",
                company_name="Company",
                description="A" * 100,
                required_skills=["Python"],
                location="Sydney",
                work_mode=WorkMode.REMOTE,
                contact_email="test@example.com",
                salary_min=150000,
                salary_max=100000  # Invalid: max < min
            )


class TestJobService:
    """Test JobService business logic"""

    @pytest.mark.asyncio
    async def test_create_job_success(self, job_service, mock_supabase, sample_job_data, sample_employer_id):
        """Test successful job creation"""
        jobs_table = Mock()
        mock_response = Mock()
        mock_response.data = [
            _jobs_row(
                employer_id=str(sample_employer_id),
                title=sample_job_data.title,
                status="draft",
            )
        ]
        jobs_table.insert.return_value.execute.return_value = mock_response
        _configure_supabase_tables(
            mock_supabase, jobs_table, sample_job_data.company_name
        )

        result = await job_service.create_job(sample_job_data, sample_employer_id)

        assert result.title == sample_job_data.title
        assert result.status == JobStatus.DRAFT
        assert result.views_count == 0
        assert result.applications_count == 0
        mock_supabase.table.assert_any_call("jobs")

    @pytest.mark.asyncio
    async def test_create_job_failure(self, job_service, mock_supabase, sample_job_data, sample_employer_id):
        """Test job creation failure"""
        # Mock Supabase response with no data (failure)
        mock_response = Mock()
        mock_response.data = None

        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await job_service.create_job(sample_job_data, sample_employer_id)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_get_job_by_id_success(self, job_service, mock_supabase):
        """Test successful job retrieval"""
        job_id = uuid4()
        employer_id = uuid4()
        jobs_table = Mock()
        mock_response = Mock()
        mock_response.data = [
            _jobs_row(
                id=str(job_id),
                employer_id=str(employer_id),
                status="published",
            )
        ]
        jobs_table.select.return_value.eq.return_value.execute.return_value = mock_response
        _configure_supabase_tables(mock_supabase, jobs_table)

        result = await job_service.get_job_by_id(job_id)

        assert result.job_id == job_id
        assert result.title == "Test Job"

    @pytest.mark.asyncio
    async def test_get_job_not_found(self, job_service, mock_supabase):
        """Test job retrieval when job doesn't exist"""
        job_id = uuid4()
        mock_response = Mock()
        mock_response.data = None

        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        # Should raise 404
        with pytest.raises(HTTPException) as exc_info:
            await job_service.get_job_by_id(job_id)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_publish_job_success(self, job_service, mock_supabase, sample_employer_id):
        """Test successful job publishing"""
        job_id = uuid4()
        draft_row = _jobs_row(
            id=str(job_id),
            employer_id=str(sample_employer_id),
            status="draft",
        )

        jobs_table = Mock()
        existing_job_response = Mock()
        existing_job_response.data = [draft_row]

        publish_response = Mock()
        published_row = {**draft_row, "status": "published"}
        publish_response.data = [published_row]

        jobs_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            existing_job_response
        )
        jobs_table.update.return_value.eq.return_value.eq.return_value.execute.return_value = (
            publish_response
        )
        _configure_supabase_tables(mock_supabase, jobs_table)

        result = await job_service.publish_job(job_id, sample_employer_id)

        assert result.job_id == job_id
        assert result.status == JobStatus.PUBLISHED
        assert result.published_at is not None

    @pytest.mark.asyncio
    async def test_publish_already_published_job(self, job_service, mock_supabase, sample_employer_id):
        """Test publishing an already published job"""
        job_id = uuid4()

        # Mock existing job (already published)
        existing_job_response = Mock()
        existing_job_response.data = [
            _jobs_row(
                id=str(job_id),
                employer_id=str(sample_employer_id),
                status="published",
            )
        ]

        jobs_table = Mock()
        jobs_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            existing_job_response
        )
        _configure_supabase_tables(mock_supabase, jobs_table)

        with pytest.raises(HTTPException) as exc_info:
            await job_service.publish_job(job_id, sample_employer_id)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_search_jobs_with_filters(self, job_service, mock_supabase):
        """Test job search with multiple filters"""
        filters = JobSearchFilters(
            keyword="developer",
            location="sydney",
            work_mode=WorkMode.REMOTE,
            skills=["python", "react"],
            page=1,
            page_size=10
        )

        # Mock search results
        mock_response = Mock()
        mock_response.data = []
        mock_response.count = 0

        # Setup mock chain
        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()
        mock_or = Mock()
        mock_ilike = Mock()
        mock_filter = Mock()
        mock_order = Mock()
        mock_range = Mock()

        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.or_.return_value = mock_or
        mock_or.ilike.return_value = mock_ilike
        mock_ilike.ilike.return_value = mock_ilike
        mock_ilike.eq.return_value = mock_eq
        mock_eq.filter.return_value = mock_filter
        mock_filter.order.return_value = mock_order
        mock_order.range.return_value = mock_range
        mock_range.execute.return_value = mock_response

        _configure_supabase_tables(mock_supabase, mock_table)

        result = await job_service.search_jobs(filters)

        assert result.total == 0
        assert result.page == 1
        assert result.page_size == 10
        mock_supabase.table.assert_any_call("jobs")


def test_job_search_filters_model():
    """Test JobSearchFilters model"""
    filters = JobSearchFilters(
        keyword="python developer",
        location="melbourne",
        work_mode=WorkMode.REMOTE,
        page=2,
        page_size=20
    )

    assert filters.keyword == "python developer"
    assert filters.location == "melbourne"
    assert filters.work_mode == WorkMode.REMOTE
    assert filters.page == 2
    assert filters.page_size == 20
    assert filters.status == JobStatus.PUBLISHED  # Default


def test_job_search_filters_defaults():
    """Test JobSearchFilters default values"""
    filters = JobSearchFilters()

    assert filters.page == 1
    assert filters.page_size == 10
    assert filters.status == JobStatus.PUBLISHED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
