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
