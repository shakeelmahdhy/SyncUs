CREATE TYPE work_mode AS ENUM ('remote', 'onsite', 'hybrid');
CREATE TYPE job_status AS ENUM ('draft', 'published', 'closed');
CREATE TYPE education_level AS ENUM ('high_school', 'associate', 'bachelor', 'master', 'phd', 'any');
CREATE TYPE experience_level AS ENUM ('entry', 'junior', 'mid', 'senior', 'lead', 'any');

<<<<<<< HEAD
-- Create jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
=======
-- Create job_postings table
CREATE TABLE IF NOT EXISTS job_postings (
    job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
>>>>>>> 28d9068 (Clean matching module branch for push)
    employer_id UUID NOT NULL REFERENCES employer_profiles(id) ON DELETE CASCADE,

    -- Basic job information
    title VARCHAR(200) NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL CHECK (char_length(description) >= 50 AND char_length(description) <= 5000),

    -- Job requirements
    required_skills TEXT[] NOT NULL CHECK (array_length(required_skills, 1) >= 1),
    location VARCHAR(200) NOT NULL,
    work_mode work_mode NOT NULL,
    education_level education_level DEFAULT 'any',
<<<<<<< HEAD
    experience_required INTEGER DEFAULT 0,
=======
>>>>>>> 28d9068 (Clean matching module branch for push)
    experience_level experience_level DEFAULT 'any',
    min_years_experience INTEGER CHECK (min_years_experience >= 0 AND min_years_experience <= 50),
    max_years_experience INTEGER CHECK (max_years_experience >= 0 AND max_years_experience <= 50),

    -- Salary information
    salary_min INTEGER CHECK (salary_min >= 0),
    salary_max INTEGER CHECK (salary_max >= 0),

    -- Contact information
    contact_email VARCHAR(255) NOT NULL,
    website VARCHAR(500),

    -- Status and metadata
    status job_status DEFAULT 'draft' NOT NULL,
    views_count INTEGER DEFAULT 0 NOT NULL,
    applications_count INTEGER DEFAULT 0 NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT valid_experience_range CHECK (
        max_years_experience IS NULL OR
        min_years_experience IS NULL OR
        max_years_experience >= min_years_experience
    ),
    CONSTRAINT valid_salary_range CHECK (
        salary_max IS NULL OR
        salary_min IS NULL OR
        salary_max >= salary_min
    ),
    CONSTRAINT valid_status_timestamps CHECK (
        (status = 'published' AND published_at IS NOT NULL) OR
        (status != 'published')
    )
);

-- Create indexes for performance
<<<<<<< HEAD
CREATE INDEX idx_jobs_employer ON jobs(employer_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_work_mode ON jobs(work_mode);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX idx_jobs_published_at ON jobs(published_at DESC) WHERE status = 'published';

-- GIN index for full-text search on title and description
CREATE INDEX idx_jobs_search ON jobs USING GIN (
=======
CREATE INDEX idx_job_postings_employer ON job_postings(employer_id);
CREATE INDEX idx_job_postings_status ON job_postings(status);
CREATE INDEX idx_job_postings_location ON job_postings(location);
CREATE INDEX idx_job_postings_work_mode ON job_postings(work_mode);
CREATE INDEX idx_job_postings_created_at ON job_postings(created_at DESC);
CREATE INDEX idx_job_postings_published_at ON job_postings(published_at DESC) WHERE status = 'published';

-- GIN index for full-text search on title and description
CREATE INDEX idx_job_postings_search ON job_postings USING GIN (
>>>>>>> 28d9068 (Clean matching module branch for push)
    to_tsvector('english', title || ' ' || description)
);

-- GIN index for array search on required_skills
<<<<<<< HEAD
CREATE INDEX idx_jobs_skills ON jobs USING GIN (required_skills);

-- Composite index for common queries
CREATE INDEX idx_jobs_status_created ON jobs(status, created_at DESC);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_jobs_updated_at()
=======
CREATE INDEX idx_job_postings_skills ON job_postings USING GIN (required_skills);

-- Composite index for common queries
CREATE INDEX idx_job_postings_status_created ON job_postings(status, created_at DESC);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_job_postings_updated_at()
>>>>>>> 28d9068 (Clean matching module branch for push)
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
<<<<<<< HEAD
CREATE TRIGGER trigger_jobs_updated_at
    BEFORE UPDATE ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_jobs_updated_at();
=======
CREATE TRIGGER trigger_job_postings_updated_at
    BEFORE UPDATE ON job_postings
    FOR EACH ROW
    EXECUTE FUNCTION update_job_postings_updated_at();
>>>>>>> 28d9068 (Clean matching module branch for push)

-- Row Level Security (RLS) Policies for Supabase

-- Enable RLS
<<<<<<< HEAD
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;

-- Policy: Anyone can view published jobs
CREATE POLICY "Public can view published jobs"
    ON jobs
=======
ALTER TABLE job_postings ENABLE ROW LEVEL SECURITY;

-- Policy: Anyone can view published jobs
CREATE POLICY "Public can view published jobs"
    ON job_postings
>>>>>>> 28d9068 (Clean matching module branch for push)
    FOR SELECT
    USING (status = 'published');

-- Policy: Employers can view their own jobs (all statuses)
CREATE POLICY "Employers can view their own jobs"
<<<<<<< HEAD
    ON jobs
=======
    ON job_postings
>>>>>>> 28d9068 (Clean matching module branch for push)
    FOR SELECT
    USING (auth.uid() = employer_id);

-- Policy: Employers can create jobs
CREATE POLICY "Employers can create jobs"
<<<<<<< HEAD
    ON jobs
=======
    ON job_postings
>>>>>>> 28d9068 (Clean matching module branch for push)
    FOR INSERT
    WITH CHECK (auth.uid() = employer_id);

-- Policy: Employers can update their own jobs
CREATE POLICY "Employers can update their own jobs"
<<<<<<< HEAD
    ON jobs
=======
    ON job_postings
>>>>>>> 28d9068 (Clean matching module branch for push)
    FOR UPDATE
    USING (auth.uid() = employer_id)
    WITH CHECK (auth.uid() = employer_id);

-- Policy: Employers can delete their own draft jobs
CREATE POLICY "Employers can delete their own draft jobs"
<<<<<<< HEAD
    ON jobs
=======
    ON job_postings
>>>>>>> 28d9068 (Clean matching module branch for push)
    FOR DELETE
    USING (auth.uid() = employer_id AND status = 'draft');

-- Function to validate job posting before publish
<<<<<<< HEAD
CREATE OR REPLACE FUNCTION increment_job_views(job_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE jobs SET views_count = views_count + 1 WHERE id = job_id;
END;
$$ LANGUAGE plpgsql;

=======
>>>>>>> 28d9068 (Clean matching module branch for push)
CREATE OR REPLACE FUNCTION validate_job_before_publish()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'published' AND OLD.status != 'published' THEN
        -- Ensure all required fields are filled
        IF NEW.title IS NULL OR
           NEW.description IS NULL OR
           NEW.required_skills IS NULL OR
           NEW.location IS NULL OR
           NEW.contact_email IS NULL THEN
            RAISE EXCEPTION 'All required fields must be filled before publishing';
        END IF;

        -- Set published_at timestamp if not set
        IF NEW.published_at IS NULL THEN
            NEW.published_at = CURRENT_TIMESTAMP;
        END IF;
    END IF;

    IF NEW.status = 'closed' AND OLD.status != 'closed' THEN
        -- Set closed_at timestamp if not set
        IF NEW.closed_at IS NULL THEN
            NEW.closed_at = CURRENT_TIMESTAMP;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to validate job before status change
CREATE TRIGGER trigger_validate_job_publish
<<<<<<< HEAD
    BEFORE UPDATE ON jobs
=======
    BEFORE UPDATE ON job_postings
>>>>>>> 28d9068 (Clean matching module branch for push)
    FOR EACH ROW
    WHEN (NEW.status IS DISTINCT FROM OLD.status)
    EXECUTE FUNCTION validate_job_before_publish();

-- Function to normalize skills (convert to lowercase, remove duplicates)
CREATE OR REPLACE FUNCTION normalize_job_skills()
RETURNS TRIGGER AS $$
BEGIN
    -- Convert all skills to lowercase and remove duplicates
    NEW.required_skills = ARRAY(
        SELECT DISTINCT LOWER(TRIM(skill))
        FROM unnest(NEW.required_skills) AS skill
        WHERE TRIM(skill) != ''
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to normalize skills before insert/update
CREATE TRIGGER trigger_normalize_job_skills
<<<<<<< HEAD
    BEFORE INSERT OR UPDATE ON jobs
=======
    BEFORE INSERT OR UPDATE ON job_postings
>>>>>>> 28d9068 (Clean matching module branch for push)
    FOR EACH ROW
    EXECUTE FUNCTION normalize_job_skills();

-- View for public job feed (only published jobs with essential info)
CREATE OR REPLACE VIEW public_job_feed AS
SELECT
    job_id,
    title,
    company_name,
    SUBSTRING(description, 1, 200) || '...' AS short_description,
    required_skills,
    location,
    work_mode,
    education_level,
    experience_level,
    min_years_experience,
    max_years_experience,
    salary_min,
    salary_max,
    published_at,
    views_count,
    applications_count
<<<<<<< HEAD
FROM jobs
=======
FROM job_postings
>>>>>>> 28d9068 (Clean matching module branch for push)
WHERE status = 'published'
ORDER BY published_at DESC;

-- Grant permissions for the view
GRANT SELECT ON public_job_feed TO anon, authenticated;

<<<<<<< HEAD
COMMENT ON TABLE jobs IS 'Job postings created by employers in the SyncUs platform';
COMMENT ON COLUMN jobs.required_skills IS 'Array of lowercase skill keywords required for the job';
COMMENT ON COLUMN jobs.views_count IS 'Number of times this job posting has been viewed';
COMMENT ON COLUMN jobs.applications_count IS 'Number of applications received';
=======

COMMENT ON TABLE job_postings IS 'Job postings created by employers in the SyncUs platform';
COMMENT ON COLUMN job_postings.required_skills IS 'Array of lowercase skill keywords required for the job';
COMMENT ON COLUMN job_postings.views_count IS 'Number of times this job posting has been viewed by candidates';
COMMENT ON COLUMN job_postings.applications_count IS 'Number of applications received for this job posting';
COMMENT ON COLUMN job_postings.status IS 'Current status: draft (not visible), published (visible), closed (no longer accepting applications)';
>>>>>>> 28d9068 (Clean matching module branch for push)
