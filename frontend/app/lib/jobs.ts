import type { ApplicationStatus, BackendJob, SearchJobResult, TrackingApplication, WorkMode } from "./api";
import { getJob, getJobRecommendations } from "./api";

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  types: string[];
  respondsWithin: string;
  description: string;
  fullDescription: string;
  requirements: string[];
  recommended: boolean;
  postedDate: string;
  salary: string;
  experience: string;
  matchScore: number;
  applicants: number;
  interviews: number;
  skills: string[];
  category: string;
  workType: "Full-Time";
  locationMode: "Remote" | "On-site" | "Hybrid";
}

export interface Application {
  id: string;
  jobId: string;
  title: string;
  company: string;
  location: string;
  status: "Applied" | "Interviewing" | "Shortlisted" | "Offered" | "Rejected" | "Withdrawn";
  appliedDate: string;
  matchScore: number;
}

export interface RecommendedRole {
  jobId: string;
  title: string;
  company: string;
  location: string;
  workMode: string;
  skills: string[];
  matchScore: number;
  description: string;
  salary: string;
  category: string;
}

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

export function toFrontendSearchJob(job: SearchJobResult): Job {
  const skills = job.required_skills.map(titleCaseSkill);
  const locationMode = job.work_mode ? workModeLabels[job.work_mode] : "Hybrid";
  const category = inferCategory({
    title: job.title,
    description: "",
    required_skills: job.required_skills,
  } as BackendJob);

  return {
    id: job.job_id,
    title: job.title,
    company: job.company_name,
    location: job.location,
    types: [locationMode, "Full-Time"],
    respondsWithin: "<3 days",
    description: skills.length ? `Required skills: ${skills.join(", ")}` : "Open role from SyncUs jobs search.",
    fullDescription: "Open role from SyncUs jobs search. View the role for the full job description.",
    requirements: skills.map((skill) => `Experience with ${skill}`),
    recommended: false,
    postedDate: job.published_at ? formatPostedDate(job.published_at) : "Recently posted",
    salary: "Salary not listed",
    experience: "Any experience",
    matchScore: Math.min(98, 70 + Math.max(0, skills.length * 4)),
    applicants: job.applications_count,
    interviews: Math.floor(job.applications_count * 0.12),
    skills,
    category,
    workType: "Full-Time",
    locationMode,
  };
}

const applicationStatusLabels: Record<ApplicationStatus, Application["status"]> = {
  applied: "Applied",
  shortlisted: "Shortlisted",
  interview: "Interviewing",
  offered: "Offered",
  rejected: "Rejected",
  withdrawn: "Withdrawn",
};

export async function fetchRecommendedRoles(): Promise<RecommendedRole[]> {
  const recommendations = await getJobRecommendations();
  if (recommendations.length === 0) return [];

  const jobDetails = await Promise.allSettled(recommendations.map((item) => getJob(item.job_id)));

  return recommendations.map((item, index) => {
    const detail = jobDetails[index]?.status === "fulfilled" ? jobDetails[index].value : null;
    const skills = item.required_skills.map(titleCaseSkill);
    const location = item.location ?? detail?.location ?? "Location TBD";
    const workMode = item.work_mode
      ? workModeLabels[item.work_mode as WorkMode] ?? titleCaseSkill(item.work_mode)
      : detail
        ? workModeLabels[detail.work_mode]
        : "Hybrid";

    return {
      jobId: item.job_id,
      title: item.title,
      company: detail?.company_name ?? "Employer",
      location,
      workMode,
      skills,
      matchScore: Math.round(item.score * 100),
      description:
        detail?.description ??
        (skills.length ? `Required skills: ${skills.join(", ")}` : "Open role from SyncUs matching."),
      salary: detail ? formatSalary(detail) : "Salary not listed",
      category: detail ? inferCategory(detail) : "General",
    };
  });
}

export function toFrontendApplication(application: TrackingApplication, job?: Job): Application {
  return {
    id: application.id,
    jobId: application.job_id,
    title: job?.title ?? `Job ${application.job_id.slice(0, 8)}`,
    company: job?.company ?? "Employer",
    location: job?.location ?? "Location unavailable",
    status: applicationStatusLabels[application.status],
    appliedDate: new Date(application.created_at).toLocaleDateString("en-AU", {
      month: "short",
      day: "numeric",
      year: "numeric",
    }),
    matchScore: job?.matchScore ?? 0,
  };
}
