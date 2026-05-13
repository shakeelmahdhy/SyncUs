const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface AccountProfile {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  location: string;
  title: string;
  experience: string;
  bio: string;
  linkedin: string;
  portfolio: string;
  education: string;
  company: string;
  skills: string[];
}

export type AccountProfileUpdate = Omit<AccountProfile, "id">;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function getAccountProfile() {
  return request<AccountProfile>("/skill-sync/v1/accounts/me");
}

export function updateAccountProfile(profile: AccountProfileUpdate) {
  return request<AccountProfile>("/skill-sync/v1/accounts/me", {
    method: "PUT",
    body: JSON.stringify(profile),
  });
}

export type WorkMode = "remote" | "onsite" | "hybrid";
export type JobStatus = "draft" | "published" | "closed";

export interface BackendJob {
  job_id: string;
  employer_id: string;
  title: string;
  company_name: string;
  description: string;
  required_skills: string[];
  location: string;
  work_mode: WorkMode;
  education_level: string;
  experience_level: string;
  min_years_experience: number | null;
  max_years_experience: number | null;
  salary_min: number | null;
  salary_max: number | null;
  contact_email: string;
  website: string | null;
  status: JobStatus;
  views_count: number;
  applications_count: number;
  created_at: string;
  updated_at: string;
  published_at: string | null;
  closed_at: string | null;
}

export interface JobListResponse {
  jobs: BackendJob[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface JobSearchParams {
  keyword?: string;
  location?: string;
  work_mode?: WorkMode;
  skills?: string[];
  page?: number;
  page_size?: number;
}

export function searchJobs(params: JobSearchParams = {}) {
  const searchParams = new URLSearchParams();

  if (params.keyword) searchParams.set("keyword", params.keyword);
  if (params.location) searchParams.set("location", params.location);
  if (params.work_mode) searchParams.set("work_mode", params.work_mode);
  if (params.skills?.length) searchParams.set("skills", params.skills.join(","));
  if (params.page) searchParams.set("page", String(params.page));
  if (params.page_size) searchParams.set("page_size", String(params.page_size));

  const query = searchParams.toString();
  return request<JobListResponse>(`/skill-sync/v1/jobs${query ? `?${query}` : ""}`);
}

export function getJob(jobId: string) {
  return request<BackendJob>(`/skill-sync/v1/jobs/${jobId}`);
}
