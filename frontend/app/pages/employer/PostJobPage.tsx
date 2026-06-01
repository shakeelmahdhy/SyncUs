import { useState } from "react";
import { Save, X } from "lucide-react";
import { useNavigate } from "react-router";
import { createJob, publishJob, type CreateJobPayload, type WorkMode } from "../../lib/api";
import { EmployerShell } from "./EmployerShell";

const skillSuggestions = [
  "React",
  "TypeScript",
  "Python",
  "FastAPI",
  "Figma",
  "User Research",
  "Product Strategy",
  "SQL",
  "Node.js",
  "Agile",
];

const emptyJob = {
  title: "",
  company_name: "",
  description: "",
  required_skills: [] as string[],
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
    required_skills: form.required_skills,
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
    required_skills: ["Figma", "User Research", "Prototyping", "Design Systems"],
    contact_email: "careers@FPT.com",
    salary_min: "120000",
    salary_max: "150000",
  });
  const [skillDraft, setSkillDraft] = useState("");
  const [publishImmediately, setPublishImmediately] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const updateField = (key: keyof JobForm, value: string) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const addSkill = (raw: string) => {
    const parts = raw
      .split(",")
      .map((skill) => skill.trim())
      .filter(Boolean);

    if (parts.length === 0) return;

    setForm((current) => {
      const next = [...current.required_skills];
      for (const skill of parts) {
        const exists = next.some((item) => item.toLowerCase() === skill.toLowerCase());
        if (!exists) next.push(skill);
      }
      return { ...current, required_skills: next };
    });
    setSkillDraft("");
  };

  const removeSkill = (skill: string) => {
    setForm((current) => ({
      ...current,
      required_skills: current.required_skills.filter((item) => item !== skill),
    }));
  };

  const handleSubmit = async () => {
    setSaving(true);
    setError(null);
    setMessage(null);

    if (form.required_skills.length === 0) {
      setError("Add at least one required skill.");
      setSaving(false);
      return;
    }

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
      <div className="mx-auto w-3/4">
        <header className="mb-8">
          <h1 className="font-serif text-[clamp(2.7rem,5vw,5rem)] leading-none tracking-normal">Post a New Job</h1>
          <p className="mt-4 text-base font-medium text-syncus-blue/68">
            Create a role in the jobs module, publish it, and make it available for tracking and AI candidate matching.
          </p>
        </header>

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
            <div className="md:col-span-2">
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">
                Required skills
              </span>
              <div className="rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 py-4">
                {form.required_skills.length > 0 ? (
                  <div className="mb-4 flex flex-wrap gap-2">
                    {form.required_skills.map((skill) => (
                      <span
                        key={skill}
                        className="inline-flex items-center gap-1.5 rounded-full border-2 border-syncus-green/40 bg-syncus-green/10 px-3 py-1.5 text-sm font-bold text-syncus-green"
                      >
                        {skill}
                        <button
                          type="button"
                          className="grid h-5 w-5 place-items-center rounded-full text-syncus-green transition hover:bg-syncus-green/15"
                          onClick={() => removeSkill(skill)}
                          aria-label={`Remove ${skill}`}
                        >
                          <X size={12} strokeWidth={3} />
                        </button>
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="mb-4 text-sm font-medium text-syncus-blue/50">No skills added yet.</p>
                )}

                <input
                  className="min-h-11 w-full rounded-lg border-2 border-syncus-blue/25 bg-white px-4 text-sm font-bold text-syncus-blue outline-none focus:border-syncus-green"
                  value={skillDraft}
                  onChange={(event) => setSkillDraft(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      event.preventDefault();
                      addSkill(skillDraft);
                    }
                  }}
                  onBlur={() => {
                    if (skillDraft.trim()) addSkill(skillDraft);
                  }}
                  placeholder="Type a skill and press Enter"
                />

                <p className="mt-4 text-xs font-bold uppercase tracking-[0.08em] text-syncus-blue/45">Suggestions</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {skillSuggestions
                    .filter(
                      (suggestion) =>
                        !form.required_skills.some(
                          (skill) => skill.toLowerCase() === suggestion.toLowerCase()
                        )
                    )
                    .map((suggestion) => (
                      <button
                        key={suggestion}
                        type="button"
                        className="rounded-full border-2 border-syncus-blue/20 px-3 py-1.5 text-xs font-bold text-syncus-blue transition hover:border-syncus-green hover:text-syncus-green"
                        onClick={() => addSkill(suggestion)}
                      >
                        + {suggestion}
                      </button>
                    ))}
                </div>
              </div>
            </div>
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
              <Save size={16} />
            </button>
          </div>
          {message && <p className="mt-4 text-sm font-black text-syncus-green">{message}</p>}
          {error && <p className="mt-4 text-sm font-black text-red-600">{error}</p>}
        </form>
      </div>
    </EmployerShell>
  );
}
