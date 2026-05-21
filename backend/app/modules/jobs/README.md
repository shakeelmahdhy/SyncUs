# Jobs Module

## Overview
The Jobs module handles all job posting functionality in the SyncUs Intelligent Job Matching Platform. This module enables employers to create, manage, publish, and close job postings, while allowing job seekers to search and filter available opportunities.

## Features

### Employer Features
- ✅ Create job postings (initially in DRAFT status)
- ✅ Update job postings (only if not closed)
- ✅ Publish job postings (make visible to candidates)
- ✅ Close job postings (stop accepting applications)
- ✅ Delete draft job postings
- ✅ View all their job postings with filtering by status
- ✅ View job posting statistics (views, applications, status counts)

### Job Seeker Features
- ✅ Search jobs by keyword (title, description)
- ✅ Filter jobs by:
  - Location
  - Work mode (remote/onsite/hybrid)
  - Education level
  - Experience level
  - Required skills
  - Salary range
- ✅ View published job details
- ✅ Browse public job feed

### System Features
- ✅ Automatic view count tracking
- ✅ Skills normalization (lowercase, deduplication)
- ✅ Row-Level Security (RLS) for data privacy
- ✅ Pagination support for all list endpoints
- ✅ Input validation and sanitization
- ✅ Status workflow management (draft → published → closed)

## API Endpoints

### Job Management

#### Create Job
```http
POST /jobs
Authorization: Bearer <employer_token>
Content-Type: application/json

{
  "title": "Senior Full Stack Developer",
  "company_name": "Tech Innovations Ltd",
  "description": "We are looking for an experienced full stack developer...",
  "required_skills": ["React", "Python", "FastAPI", "PostgreSQL"],
  "location": "Sydney, NSW",
  "work_mode": "hybrid",
  "education_level": "bachelor",
  "experience_level": "senior",
  "min_years_experience": 5,
  "max_years_experience": 10,
  "salary_min": 120000,
  "salary_max": 160000,
  "contact_email": "careers@techinnovations.com.au",
  "website": "https://techinnovations.com.au"
}
```

**Response:** `201 Created`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "employer_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Senior Full Stack Developer",
  "status": "draft",
  "views_count": 0,
  "applications_count": 0,
  "created_at": "2026-04-30T10:30:00Z",
  ...
}
```

#### Get Job Details
```http
GET /jobs/{job_id}
```

**Response:** `200 OK`

#### Update Job
```http
PATCH /jobs/{job_id}
Authorization: Bearer <employer_token>
Content-Type: application/json

{
  "description": "Updated job description...",
  "salary_max": 170000
}
```

**Response:** `200 OK`

#### Publish Job
```http
POST /jobs/{job_id}/publish
Authorization: Bearer <employer_token>
```

**Response:** `200 OK`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "published",
  "published_at": "2026-04-30T11:00:00Z",
  "message": "Job posting published successfully"
}
```

#### Close Job
```http
POST /jobs/{job_id}/close
Authorization: Bearer <employer_token>
```

**Response:** `200 OK`

#### Delete Job (Draft Only)
```http
DELETE /jobs/{job_id}
Authorization: Bearer <employer_token>
```

**Response:** `200 OK`

### Job Search & Discovery

#### Search Jobs
```http
GET /jobs?keyword=developer&location=sydney&work_mode=remote&skills=react,python&page=1&page_size=10
```

**Query Parameters:**
- `keyword`: Search in title and description
- `location`: Filter by location
- `work_mode`: remote, onsite, or hybrid
- `education_level`: Minimum education required
- `experience_level`: Experience level filter
- `skills`: Comma-separated skill list
- `min_salary`: Minimum salary threshold
- `max_salary`: Maximum salary threshold
- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 10, max: 100)

**Response:** `200 OK`
```json
{
  "jobs": [...],
  "total": 45,
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```

#### Get My Jobs (Employer)
```http
GET /jobs/employer/my-jobs?status_filter=published&page=1&page_size=10
Authorization: Bearer <employer_token>
```

**Response:** `200 OK`

#### Get Job Statistics (Employer)
```http
GET /jobs/stats/overview
Authorization: Bearer <employer_token>
```

**Response:** `200 OK`
```json
{
  "total_jobs": 15,
  "draft_count": 3,
  "published_count": 10,
  "closed_count": 2,
  "total_views": 1250,
  "total_applications": 87
}
```

## Data Models

### Job Status Workflow
```
DRAFT → PUBLISHED → CLOSED
  ↓
DELETE (only drafts)
```

### Work Modes
- `remote`: Fully remote work
- `onsite`: Office-based work
- `hybrid`: Combination of remote and onsite

### Education Levels
- `high_school`
- `associate`
- `bachelor`
- `master`
- `phd`
- `any`

### Experience Levels
- `entry`
- `junior`
- `mid`
- `senior`
- `lead`
- `any`

## Database Schema

The jobs module uses the `job_postings` table with the following structure:

### Core Fields
- `job_id` (UUID, PK): Unique identifier
- `employer_id` (UUID, FK): Reference to employer profile
- `title` (VARCHAR): Job title
- `company_name` (VARCHAR): Company name
- `description` (TEXT): Detailed job description
- `required_skills` (TEXT[]): Array of required skills

### Requirements
- `location` (VARCHAR): Job location
- `work_mode` (ENUM): remote/onsite/hybrid
- `education_level` (ENUM): Minimum education
- `experience_level` (ENUM): Experience level
- `min_years_experience` (INTEGER): Minimum years
- `max_years_experience` (INTEGER): Maximum years
- `salary_min` (INTEGER): Minimum salary
- `salary_max` (INTEGER): Maximum salary

### Contact & Metadata
- `contact_email` (VARCHAR): Contact email
- `website` (VARCHAR): Company website
- `status` (ENUM): draft/published/closed
- `views_count` (INTEGER): View counter
- `applications_count` (INTEGER): Application counter

### Timestamps
- `created_at` (TIMESTAMP): Creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp
- `published_at` (TIMESTAMP): Publication timestamp
- `closed_at` (TIMESTAMP): Closure timestamp

### Indexes
- Employer ID, status, location, work mode
- Full-text search on title + description (GIN)
- Array search on required_skills (GIN)
- Composite indexes for common queries

## Security

### Row-Level Security (RLS) Policies

1. **Public Read Access**: Anyone can view published jobs
2. **Employer Ownership**: Employers can only access their own jobs
3. **Status-Based Deletion**: Only draft jobs can be deleted
4. **Authorization**: All mutations require employer authentication

### Data Validation

- Email format validation
- Skill normalization (lowercase, deduplication)
- Salary range validation
- Experience range validation
- Description length validation (50-5000 chars)
- At least 1 skill required

## Usage Examples

### Creating and Publishing a Job

```python
from jobs import JobCreate, JobService

# Create job data
job_data = JobCreate(
    title="Python Backend Developer",
    company_name="Startup Inc",
    description="We are seeking a talented Python developer...",
    required_skills=["Python", "FastAPI", "PostgreSQL"],
    location="Melbourne, VIC",
    work_mode="remote",
    contact_email="jobs@startup.com"
)

# Create job (status: DRAFT)
job = await job_service.create_job(job_data, employer_id)

# Publish job (status: PUBLISHED)
result = await job_service.publish_job(job.job_id, employer_id)
```

### Searching for Jobs

```python
from jobs import JobSearchFilters

# Create search filters
filters = JobSearchFilters(
    keyword="developer",
    location="sydney",
    work_mode="remote",
    skills=["react", "typescript"],
    min_salary=100000,
    page=1,
    page_size=20
)

# Execute search
results = await job_service.search_jobs(filters)

print(f"Found {results.total} jobs")
for job in results.jobs:
    print(f"- {job.title} at {job.company_name}")
```

## Testing

### Unit Tests
Run unit tests for the jobs module:
```bash
pytest tests/modules/jobs/test_service.py
pytest tests/modules/jobs/test_models.py
```

### Integration Tests
Run integration tests with Supabase:
```bash
pytest tests/modules/jobs/test_integration.py
```

### Test Coverage
Ensure ≥80% test coverage as per Definition of Done:
```bash
pytest --cov=app/modules/jobs tests/modules/jobs/
```

## Performance Considerations

1. **Pagination**: Always use pagination for list endpoints to avoid large result sets
2. **Indexes**: Database indexes optimize common queries (status, location, skills)
3. **View Counting**: View count updates are fire-and-forget to avoid blocking reads
4. **Skills Search**: GIN indexes enable efficient array searches

## Future Enhancements

- [ ] Job templates for repeat postings
- [ ] Bulk job import from CSV
- [ ] Job posting analytics dashboard
- [ ] Automated job expiration
- [ ] Job posting drafts collaboration
- [ ] Rich text description editor
- [ ] Custom screening questions
- [ ] Application tracking integration

## Dependencies

- **FastAPI**: Web framework
- **Pydantic**: Data validation
- **Supabase**: Database and authentication
- **PostgreSQL**: Relational database

## Module Structure

```
modules/jobs/
├── __init__.py           # Module exports
├── models.py             # Pydantic models
├── service.py            # Business logic
├── router.py             # API endpoints
├── schema.sql            # Database schema
└── README.md             # This file
```

## Support

For issues or questions about the jobs module, please:
1. Check the API documentation
2. Review the database schema
3. Check existing test cases
4. Contact the development team

## License

Part of the SyncUs platform - University of Wollongong CSIT314 Project
