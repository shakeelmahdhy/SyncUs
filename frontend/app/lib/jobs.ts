import type { Application, Job } from "../data/mockData";
import type { BackendJob, WorkMode } from "./api";

const applicationStorageKey = "syncus.applications";

const workModeLabels: Record<WorkMode, Job["locationMode"]> = {
  remote: "Remote",
  onsite: "On-site",
  hybrid: "Hybrid",
};

const experienceLabels: Record<string, string> = {
  entry: "Entry level",
  junior: "1+ years",
  mid: "3+ years",
  senior: "5+ years",
  lead: "7+ years",
  any: "Any experience",
};

function titleCaseSkill(skill: string) {
  return skill
    .split(/[\s_-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatSalary(job: BackendJob) {
  if (job.salary_min && job.salary_max) {
    return `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}`;
  }

  if (job.salary_min) {
    return `From $${job.salary_min.toLocaleString()}`;
  }

  if (job.salary_max) {
    return `Up to $${job.salary_max.toLocaleString()}`;
  }

  return "Salary not listed";
}

function formatPostedDate(value: string) {
  const created = new Date(value);
  const diffMs = Date.now() - created.getTime();
  const days = Math.max(0, Math.floor(diffMs / 86_400_000));

  if (Number.isNaN(days) || days === 0) return "Today";
  if (days === 1) return "1 day ago";
  if (days < 14) return `${days} days ago`;
  if (days < 31) return `${Math.round(days / 7)} weeks ago`;

  return created.toLocaleDateString("en-AU", { month: "short", day: "numeric", year: "numeric" });
}

function inferCategory(job: BackendJob) {
  const text = `${job.title} ${job.description} ${job.required_skills.join(" ")}`.toLowerCase();

  if (text.includes("design") || text.includes("figma") || text.includes("ux")) return "Design";
  if (text.includes("marketing") || text.includes("growth")) return "Marketing";
  if (text.includes("product manager") || text.includes("roadmap")) return "Product";
  if (text.includes("engineer") || text.includes("developer") || text.includes("react")) return "Engineering";

  return "General";
}

function buildRequirements(job: BackendJob) {
  const skills = job.required_skills.map(titleCaseSkill).slice(0, 5);
  const requirements = skills.map((skill) => `Experience with ${skill}`);

  if (job.experience_level !== "any") {
    requirements.unshift(`${experienceLabels[job.experience_level] ?? job.experience_level} experience preferred`);
  }

  if (job.education_level !== "any") {
    requirements.push(`${titleCaseSkill(job.education_level)} qualification or equivalent experience`);
  }

  return requirements.length > 0 ? requirements : ["Relevant experience for the role"];
}

export function toFrontendJob(job: BackendJob): Job {
  const category = inferCategory(job);
  const skills = job.required_skills.map(titleCaseSkill);
  const salary = formatSalary(job);
  const experience =
    job.min_years_experience && job.max_years_experience
      ? `${job.min_years_experience}-${job.max_years_experience} years`
      : experienceLabels[job.experience_level] ?? "Any experience";

  return {
    id: job.job_id,
    title: job.title,
    company: job.company_name,
    location: job.location,
    types: [workModeLabels[job.work_mode], "Full-Time"],
    respondsWithin: "<3 days",
    description:
      job.description.length > 150 ? `${job.description.slice(0, 147).trim()}...` : job.description,
    fullDescription: job.description,
    requirements: buildRequirements(job),
    recommended: true,
    postedDate: formatPostedDate(job.published_at ?? job.created_at),
    salary,
    experience,
    matchScore: Math.min(98, 70 + Math.max(0, skills.length * 4)),
    applicants: job.applications_count,
    interviews: Math.floor(job.applications_count * 0.12),
    skills,
    category,
    workType: "Full-Time",
    locationMode: workModeLabels[job.work_mode],
  };
}

export function readStoredApplications(): Application[] {
  try {
    const raw = window.localStorage.getItem(applicationStorageKey);
    return raw ? (JSON.parse(raw) as Application[]) : [];
  } catch {
    return [];
  }
}

export function storeApplication(job: Job, resume: string, notes: string) {
  const current = readStoredApplications();
  const existing = current.find((application) => String(application.jobId) === String(job.id));

  if (existing) {
    return existing;
  }

  const application: Application = {
    id: Date.now(),
    jobId: job.id,
    title: job.title,
    company: job.company,
    location: job.location,
    status: "Applied",
    appliedDate: new Date().toLocaleDateString("en-AU", {
      month: "short",
      day: "numeric",
      year: "numeric",
    }),
    matchScore: job.matchScore,
    resume,
    notes,
  };

  window.localStorage.setItem(applicationStorageKey, JSON.stringify([application, ...current]));
  return application;
}
