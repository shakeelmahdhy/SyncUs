import { useState } from "react";
import { ArrowRight, CheckCircle2, Plus, Send } from "lucide-react";
import { useNavigate } from "react-router";
import { createJob, publishJob, type CreateJobPayload, type WorkMode } from "../../lib/api";
import { EmployerShell } from "./EmployerShell";

const emptyJob = {
  title: "",
  company_name: "",
  description: "",
  required_skills: "",
  location: "Sydney, NSW",
  work_mode: "hybrid" as WorkMode,
  education_level: "any",
  experience_level: "mid",
  min_years_experience: "2",
  max_years_experience: "5",
  salary_min: "",
  salary_max: "",
  contact_email: "",
  website: "",
};

type JobForm = typeof emptyJob;

function toNumberOrNull(value: string) {
  const parsed = Number(value);
  return Number.isFinite(parsed) && value.trim() !== "" ? parsed : null;
}

function toPayload(form: JobForm): CreateJobPayload {
  return {
    title: form.title,
    company_name: form.company_name,
    description: form.description,
    required_skills: form.required_skills
      .split(",")
      .map((skill) => skill.trim())
      .filter(Boolean),
    location: form.location,
    work_mode: form.work_mode,
    education_level: form.education_level,
    experience_level: form.experience_level,
    min_years_experience: toNumberOrNull(form.min_years_experience),
    max_years_experience: toNumberOrNull(form.max_years_experience),
    salary_min: toNumberOrNull(form.salary_min),
    salary_max: toNumberOrNull(form.salary_max),
    contact_email: form.contact_email,
    website: form.website.trim() || null,
  };
}

export function EmployerPostJobPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState<JobForm>({
    ...emptyJob,
    title: "Senior Product Designer",
    company_name: "ThisCompany",
    description:
      "Join our hiring team as a Senior Product Designer responsible for research, design systems, prototyping, and partnering with product and engineering to ship accessible user experiences.",
    required_skills: "Figma, User Research, Prototyping, Design Systems",
    contact_email: "careers@thiscompany.com",
    salary_min: "120000",
    salary_max: "150000",
  });
  const [publishImmediately, setPublishImmediately] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const updateField = (key: keyof JobForm, value: string) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleSubmit = async () => {
    setSaving(true);
    setError(null);
    setMessage(null);

    try {
      const job = await createJob(toPayload(form));
      if (publishImmediately) {
        await publishJob(job.job_id);
      }
      setMessage(publishImmediately ? "Job posted and published." : "Job saved as a draft.");
      window.setTimeout(() => navigate("/employer/dashboard"), 700);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Job could not be saved.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <EmployerShell>
      <header className="mb-8 max-w-[940px]">
        <h1 className="font-serif text-[clamp(2.7rem,5vw,5rem)] leading-none tracking-normal">Post a New Job</h1>
        <p className="mt-4 text-base font-medium text-syncus-blue/68">
          Create a role in the jobs module, publish it, and make it available for tracking and AI candidate matching.
        </p>
      </header>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
        <form
          className="rounded-[18px] border-2 border-syncus-blue bg-syncus-cream p-5 sm:p-7"
          onSubmit={(event) => {
            event.preventDefault();
            void handleSubmit();
          }}
        >
          <div className="grid gap-5 md:grid-cols-2">
            <label>
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">Job title</span>
              <input
                className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 font-bold outline-none focus:border-syncus-green"
                value={form.title}
                onChange={(event) => updateField("title", event.target.value)}
              />
            </label>
            <label>
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">Company</span>
              <input
                className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 font-bold outline-none focus:border-syncus-green"
                value={form.company_name}
                onChange={(event) => updateField("company_name", event.target.value)}
              />
            </label>
            <label className="md:col-span-2">
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">Role description</span>
              <textarea
                className="min-h-[150px] w-full resize-none rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 py-3 font-medium outline-none focus:border-syncus-green"
                value={form.description}
                onChange={(event) => updateField("description", event.target.value)}
              />
            </label>
            <label className="md:col-span-2">
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">Required skills</span>
              <input
                className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 font-bold outline-none focus:border-syncus-green"
                value={form.required_skills}
                onChange={(event) => updateField("required_skills", event.target.value)}
                placeholder="React, TypeScript, Product Strategy"
              />
            </label>
            <label>
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">Location</span>
              <input
                className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 font-bold outline-none focus:border-syncus-green"
                value={form.location}
                onChange={(event) => updateField("location", event.target.value)}
              />
            </label>
            <label>
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">Work mode</span>
              <select
                className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 font-bold outline-none focus:border-syncus-green"
                value={form.work_mode}
                onChange={(event) => updateField("work_mode", event.target.value)}
              >
                <option value="hybrid">Hybrid</option>
                <option value="remote">Remote</option>
                <option value="onsite">On-site</option>
              </select>
            </label>
            <label>
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">Experience</span>
              <select
                className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 font-bold outline-none focus:border-syncus-green"
                value={form.experience_level}
                onChange={(event) => updateField("experience_level", event.target.value)}
              >
                <option value="entry">Entry</option>
                <option value="junior">Junior</option>
                <option value="mid">Mid</option>
                <option value="senior">Senior</option>
                <option value="lead">Lead</option>
                <option value="any">Any</option>
              </select>
            </label>
            <label>
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">Education</span>
              <select
                className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 font-bold outline-none focus:border-syncus-green"
                value={form.education_level}
                onChange={(event) => updateField("education_level", event.target.value)}
              >
                <option value="any">Any</option>
                <option value="bachelor">Bachelor</option>
                <option value="master">Master</option>
                <option value="phd">PhD</option>
                <option value="associate">Associate</option>
                <option value="high_school">High school</option>
              </select>
            </label>
            <label>
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">Min years</span>
              <input
                className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 font-bold outline-none focus:border-syncus-green"
                value={form.min_years_experience}
                onChange={(event) => updateField("min_years_experience", event.target.value)}
                type="number"
              />
            </label>
            <label>
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">Max years</span>
              <input
                className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 font-bold outline-none focus:border-syncus-green"
                value={form.max_years_experience}
                onChange={(event) => updateField("max_years_experience", event.target.value)}
                type="number"
              />
            </label>
            <label>
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">Salary min</span>
              <input
                className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 font-bold outline-none focus:border-syncus-green"
                value={form.salary_min}
                onChange={(event) => updateField("salary_min", event.target.value)}
                type="number"
              />
            </label>
            <label>
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">Salary max</span>
              <input
                className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 font-bold outline-none focus:border-syncus-green"
                value={form.salary_max}
                onChange={(event) => updateField("salary_max", event.target.value)}
                type="number"
              />
            </label>
            <label>
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">Contact email</span>
              <input
                className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 font-bold outline-none focus:border-syncus-green"
                value={form.contact_email}
                onChange={(event) => updateField("contact_email", event.target.value)}
                type="email"
              />
            </label>
            <label>
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">Website</span>
              <input
                className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 font-bold outline-none focus:border-syncus-green"
                value={form.website}
                onChange={(event) => updateField("website", event.target.value)}
              />
            </label>
          </div>

          <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <label className="flex items-center gap-3 text-sm font-bold">
              <input
                className="h-4 w-4 accent-syncus-green"
                checked={publishImmediately}
                onChange={(event) => setPublishImmediately(event.target.checked)}
                type="checkbox"
              />
              Publish immediately
            </label>
            <button
              className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-syncus-blue px-7 text-sm font-black text-syncus-cream transition hover:-translate-y-0.5 disabled:opacity-60"
              disabled={saving}
              type="submit"
            >
              {saving ? "Saving..." : "Save Job"}
              <Send size={16} />
            </button>
          </div>
          {message && <p className="mt-4 text-sm font-black text-syncus-green">{message}</p>}
          {error && <p className="mt-4 text-sm font-black text-red-600">{error}</p>}
        </form>

        <aside className="rounded-[18px] border-2 border-syncus-blue bg-syncus-blue p-6 text-syncus-cream">
          <CheckCircle2 size={32} className="text-syncus-lime" />
          <h2 className="mt-5 font-serif text-3xl leading-none">Connected workflow</h2>
          <div className="mt-6 grid gap-4 text-sm font-medium text-white/78">
            <p className="flex gap-3">
              <Plus className="mt-0.5 shrink-0 text-syncus-lime" size={16} />
              Create the role through the Jobs module.
            </p>
            <p className="flex gap-3">
              <ArrowRight className="mt-0.5 shrink-0 text-syncus-lime" size={16} />
              Published jobs feed candidate search and AI matching.
            </p>
            <p className="flex gap-3">
              <CheckCircle2 className="mt-0.5 shrink-0 text-syncus-lime" size={16} />
              New applications become visible in Review Applications.
            </p>
          </div>
        </aside>
      </section>
    </EmployerShell>
  );
}
