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
  return request<JobListResponse>(`/jobs${query ? `?${query}` : ""}`);
}

export function getJob(jobId: string) {
  return request<BackendJob>(`/jobs/${jobId}`);
}
