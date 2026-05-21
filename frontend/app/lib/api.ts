const defaultApiBaseUrl =
  typeof window !== "undefined"
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : "http://127.0.0.1:8000";
const API_BASE_URL = ((import.meta as unknown) as { env: { VITE_API_BASE_URL?: string } }).env.VITE_API_BASE_URL ?? defaultApiBaseUrl;
const AUTH_TOKEN_KEY = "syncus_access_token";

export function getStoredAccessToken() {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(AUTH_TOKEN_KEY);
}

export function storeAccessToken(token: string) {
  window.localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function clearAccessToken() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(AUTH_TOKEN_KEY);
}

export function hasStoredAccessToken() {
  return Boolean(getStoredAccessToken());
}

function getJwtSub(token: string | null) {
  if (!token) return null;

  try {
    const [, payload] = token.split(".");
    const normalizedPayload = payload.replace(/-/g, "+").replace(/_/g, "/");
    const paddedPayload = normalizedPayload.padEnd(
      normalizedPayload.length + ((4 - (normalizedPayload.length % 4)) % 4),
      "="
    );
    const decoded = JSON.parse(window.atob(paddedPayload)) as { sub?: string };
    return decoded.sub ?? null;
  } catch {
    return null;
  }
}

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
  const token = getStoredAccessToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
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
  const userId = getJwtSub(getStoredAccessToken());
  if (!userId) {
    return Promise.reject(new Error("No authenticated user"));
  }
  return request<AccountProfile>(`/accounts/profile/${userId}`);
}

export function updateAccountProfile(profile: AccountProfileUpdate) {
  const userId = getJwtSub(getStoredAccessToken());
  if (!userId) {
    return Promise.reject(new Error("No authenticated user"));
  }
  return request<AccountProfile>(`/accounts/profile/${userId}`, {
    method: "PATCH",
    body: JSON.stringify(profile),
  });
}

export type AccountType = "job_seeker" | "employer";

export interface RegisterAccountPayload {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  account_type: AccountType;
  company_name?: string;
}

export interface RegisterAccountResponse {
  access_token: string | null;
  user: {
    id: string;
    email: string;
    account_type: AccountType;
  };
  profile: Record<string, unknown>;
}

export function registerAccount(payload: RegisterAccountPayload) {
  return request<RegisterAccountResponse>("/accounts/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export interface LoginAccountPayload {
  email: string;
  password: string;
}

export interface LoginAccountResponse {
  access_token: string;
  user: {
    id: string;
    email: string;
  };
}

export function loginAccount(payload: LoginAccountPayload) {
  return request<LoginAccountResponse>("/accounts/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
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

export interface SearchJobResult {
  job_id: string;
  title: string;
  company_name: string;
  location: string;
  work_mode: WorkMode | "";
  required_skills: string[];
  education_level: string | null;
  experience_level: string | null;
  salary_min: number | null;
  salary_max: number | null;
  published_at: string | null;
  views_count: number;
  applications_count: number;
}

export interface SearchJobResponse {
  results: SearchJobResult[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  keyword_used: string | null;
}

export interface CandidateSearchResult {
  candidate_id: string;
  full_name: string;
  major: string | null;
  education_level: string | null;
  skills: string[];
  location: string | null;
  gpa: number | null;
  profile_completeness: number | null;
  has_github: boolean;
  available_for: string | null;
}

export interface CandidateSearchResponse {
  results: CandidateSearchResult[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  filters_applied: string[];
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
  return request<JobListResponse>(`/jobs${query ? `?${query}` : ""}`);
}

export function searchJobDiscovery(params: JobSearchParams & { sort_by?: "newest" | "oldest" | "relevance" } = {}) {
  const searchParams = new URLSearchParams();

  if (params.keyword) searchParams.set("keyword", params.keyword);
  if (params.location) searchParams.set("location", params.location);
  if (params.work_mode) searchParams.set("work_mode", params.work_mode);
  if (params.skills?.length) searchParams.set("skills", params.skills.join(","));
  if (params.page) searchParams.set("page", String(params.page));
  if (params.page_size) searchParams.set("page_size", String(params.page_size));
  if (params.sort_by) searchParams.set("sort_by", params.sort_by);

  const query = searchParams.toString();
  return request<SearchJobResponse>(`/search/jobs${query ? `?${query}` : ""}`);
}

export function searchCandidates(params: { skills?: string[]; page?: number; page_size?: number } = {}) {
  const searchParams = new URLSearchParams();

  if (params.skills?.length) searchParams.set("skills", params.skills.join(","));
  if (params.page) searchParams.set("page", String(params.page));
  if (params.page_size) searchParams.set("page_size", String(params.page_size));

  const query = searchParams.toString();
  return request<CandidateSearchResponse>(`/search/candidates${query ? `?${query}` : ""}`);
}

export function getJob(jobId: string) {
  return request<BackendJob>(`/jobs/${jobId}`);
}

export interface CreateJobPayload {
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
}

export interface JobStatsResponse {
  total_jobs: number;
  draft_count: number;
  published_count: number;
  closed_count: number;
  total_views: number;
  total_applications: number;
}

export type ApplicationStatus =
  | "applied"
  | "shortlisted"
  | "interview"
  | "offered"
  | "rejected"
  | "withdrawn";

export interface TrackingApplication {
  id: string;
  job_id: string;
  job_seeker_id: string;
  resume_id: string | null;
  status: ApplicationStatus;
  created_at: string;
}

export interface JobPipelineResponse {
  job_id: string;
  applications: TrackingApplication[];
}

export interface ApplicationListResponse {
  items: TrackingApplication[];
  total: number;
}

export interface CandidateRecommendation {
  candidate_id: string;
  name: string;
  skills: string[];
  score: number;
  breakdown: {
    skill?: number;
    profile?: number;
    experience?: number;
  };
}

export function createJob(payload: CreateJobPayload) {
  return request<BackendJob>("/jobs", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function publishJob(jobId: string) {
  return request<{ job_id: string; status: JobStatus; published_at: string; message: string }>(
    `/jobs/${jobId}/publish`,
    { method: "POST" }
  );
}

export function getEmployerJobs(params: { status_filter?: JobStatus; page?: number; page_size?: number } = {}) {
  const searchParams = new URLSearchParams();

  if (params.status_filter) searchParams.set("status_filter", params.status_filter);
  if (params.page) searchParams.set("page", String(params.page));
  if (params.page_size) searchParams.set("page_size", String(params.page_size));

  const query = searchParams.toString();
  return request<JobListResponse>(`/jobs/employer/my-jobs${query ? `?${query}` : ""}`);
}

export function getEmployerJobStats() {
  return request<JobStatsResponse>("/jobs/stats/overview");
}

export function getJobPipeline(jobId: string) {
  return request<JobPipelineResponse>(`/tracking/jobs/${jobId}/pipeline`);
}

export function listApplications() {
  return request<ApplicationListResponse>("/tracking/applications");
}

export function createApplication(payload: { job_id: string; resume_id?: string | null }) {
  return request<TrackingApplication>("/tracking/applications", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateApplicationStatus(applicationId: string, status: ApplicationStatus) {
  return request<{ id: string; status: ApplicationStatus; updated_at: string }>(
    `/tracking/applications/${applicationId}/status`,
    {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }
  );
}

export function getCandidateRecommendations(jobId: string) {
  return request<CandidateRecommendation[]>(`/matching/jobs/${jobId}/candidates`);
}
