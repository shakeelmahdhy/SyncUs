import { useEffect, useRef, useState } from "react";
import {
  Briefcase,
  CheckCircle,
  Code,
  GraduationCap,
  Plus,
  Upload,
  User,
} from "lucide-react";
import {
  getAccountProfile,
  listProfileResumes,
  updateAccountProfile,
  uploadProfileResume,
  type AccountProfile,
  type ResumeRecord,
} from "../lib/api";

interface ResumeView {
  id: string;
  name: string;
  uploadedDate: string;
  isDefault: boolean;
  fileUrl: string;
}

function toResumeView(record: ResumeRecord): ResumeView {
  const uploadedDate = record.created_at
    ? new Date(record.created_at).toLocaleDateString("en-AU", {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : "Recently uploaded";

  return {
    id: record.id,
    name: record.resume_name || "Resume",
    uploadedDate,
    isDefault: record.is_primary,
    fileUrl: record.file_url,
  };
}

const skillSuggestions = [
  "Figma",
  "React",
  "TypeScript",
  "Product Strategy",
  "User Research",
  "Node.js",
  "Python",
  "SQL",
  "Agile",
  "Sketch",
];

const steps = ["Personal Info", "Professional", "Skills", "Resumes"] as const;
const stepIcons = [User, Briefcase, Code, GraduationCap];

const personalFields = [
  { label: "First Name", key: "firstName" },
  { label: "Last Name", key: "lastName" },
  { label: "Email Address", key: "email" },
  { label: "Phone Number", key: "phone" },
] as const;

const professionalFields = [
  { label: "Current Job Title", key: "title" },
  { label: "Years of Experience", key: "experience" },
  { label: "Education", key: "education" },
] as const;

const emptyProfile = {
  firstName: "",
  lastName: "",
  email: "",
  phone: "",
  title: "",
  experience: "",
  education: "",
};

type ProfileForm = typeof emptyProfile;

function toProfileForm(profile: AccountProfile): ProfileForm {
  return {
    firstName: profile.first_name,
    lastName: profile.last_name,
    email: profile.email ?? "",
    phone: profile.phone,
    title: profile.title,
    experience: profile.experience,
    education: profile.education,
  };
}

function toAccountProfileUpdate(form: ProfileForm, skills: string[]) {
  return {
    first_name: form.firstName,
    last_name: form.lastName,
    phone: form.phone,
    title: form.title,
    experience: form.experience,
    education: form.education,
    skills,
  };
}

export function ProfilePage() {
  const uploadInputRef = useRef<HTMLInputElement>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [resumes, setResumes] = useState<ResumeView[]>([]);
  const [skills, setSkills] = useState<string[]>([]);
  const [newSkill, setNewSkill] = useState("");
  const [saved, setSaved] = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(true);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [savingProfile, setSavingProfile] = useState(false);
  const [uploadingResume, setUploadingResume] = useState(false);

  const [form, setForm] = useState<ProfileForm>(emptyProfile);

  const loadResumes = () =>
    listProfileResumes()
      .then((response) => setResumes(response.items.map(toResumeView)))
      .catch(() => setResumes([]));

  useEffect(() => {
    let isMounted = true;

    Promise.all([getAccountProfile(), listProfileResumes()])
      .then(([profile, resumeResponse]) => {
        if (!isMounted) return;
        setForm(toProfileForm(profile));
        setSkills(profile.skills);
        setResumes(resumeResponse.items.map(toResumeView));
        setProfileError(null);
      })
      .catch((error) => {
        if (!isMounted) return;
        setProfileError(error instanceof Error ? error.message : "Profile could not be loaded.");
      })
      .finally(() => {
        if (isMounted) {
          setLoadingProfile(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const profileCompletion = Math.min(
    100,
    Math.round(
      (Object.values(form).filter(Boolean).length / Object.values(form).length) * 60 +
        skills.length * 5 +
        resumes.length * 5
    )
  );

  const updateField = (key: keyof ProfileForm, value: string) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleResumeUpload = async (file: File | undefined) => {
    if (!file) return;

    setUploadingResume(true);
    setProfileError(null);

    try {
      await uploadProfileResume(file);
      await loadResumes();
    } catch (error) {
      setProfileError(error instanceof Error ? error.message : "Resume upload failed.");
    } finally {
      setUploadingResume(false);
      if (uploadInputRef.current) {
        uploadInputRef.current.value = "";
      }
    }
  };

  const addSkill = (skill: string) => {
    const trimmed = skill.trim();
    if (trimmed && !skills.includes(trimmed)) {
      setSkills((current) => [...current, trimmed]);
    }
    setNewSkill("");
  };

  const removeSkill = (skill: string) => {
    setSkills((current) => current.filter((item) => item !== skill));
  };

  const handleSave = async () => {
    setSavingProfile(true);
    setProfileError(null);

    try {
      const profile = await updateAccountProfile(toAccountProfileUpdate(form, skills));
      setForm(toProfileForm(profile));
      setSkills(profile.skills);
      setSaved(true);
      window.setTimeout(() => setSaved(false), 2500);
    } catch {
      setProfileError("Profile changes could not be saved to the backend.");
    } finally {
      setSavingProfile(false);
    }
  };

  return (
    <main className="bg-syncus-cream px-5 py-8 text-syncus-blue sm:px-8 lg:py-10">
      <section className="mx-auto max-w-[1120px]">
        <header className="mb-7 flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
          <div>
            <h1 className="font-serif text-[clamp(2.35rem,4vw,3.8rem)] font-bold leading-none tracking-normal">
              My Profile
            </h1>
            <p className="mt-3 text-base font-medium text-syncus-blue/55 sm:text-lg">
              {loadingProfile ? "Loading your profile..." : "Keep your profile up to date for the best AI match results"}
            </p>
            {profileError && <p className="mt-2 text-sm font-bold text-red-600">{profileError}</p>}
          </div>

          <aside className="w-full rounded-2xl border-2 border-syncus-green bg-syncus-green/5 p-5 md:w-[190px]">
            <p className="text-3xl font-bold leading-none text-syncus-green">{profileCompletion}%</p>
            <p className="mt-1 text-xs font-bold text-syncus-green/70">Profile Complete</p>
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-syncus-green/15">
              <div className="h-full rounded-full bg-syncus-green" style={{ width: `${profileCompletion}%` }} />
            </div>
          </aside>
        </header>

        <div className="grid gap-6 lg:grid-cols-[210px_minmax(0,1fr)]">
          <nav className="flex gap-2 overflow-x-auto pb-2 lg:flex-col lg:overflow-visible lg:pb-0">
            {steps.map((step, index) => {
              const Icon = stepIcons[index];
              const isActive = activeStep === index;

              return (
                <button
                  key={step}
                  onClick={() => setActiveStep(index)}
                  className="flex min-h-11 shrink-0 items-center gap-2.5 rounded-xl border-2 px-4 text-left text-sm font-bold transition hover:-translate-y-0.5 lg:w-full"
                  style={{
                    backgroundColor: isActive ? "#1e4890" : "transparent",
                    borderColor: isActive ? "#1e4890" : "transparent",
                    color: isActive ? "#f6f8ed" : "#1e4890",
                  }}
                  type="button"
                >
                  <Icon size={16} />
                  {step}
                </button>
              );
            })}
          </nav>

          <section className="rounded-2xl border-2 border-syncus-blue/15 bg-syncus-cream p-5 sm:p-6 lg:p-7">
            {activeStep === 0 && (
              <div>
                <h2 className="mb-5 text-xl font-bold text-syncus-blue">Personal Information</h2>
                <div className="grid gap-4 md:grid-cols-2">
                  {personalFields.map((field) => (
                    <label key={field.key} className={"wide" in field && field.wide ? "md:col-span-2" : undefined}>
                      <span className="mb-1.5 block text-xs font-bold text-syncus-blue/55">{field.label}</span>
                      <input
                        value={form[field.key]}
                        onChange={(event) => updateField(field.key, event.target.value)}
                        className="min-h-11 w-full rounded-xl border-2 border-syncus-blue/20 bg-syncus-cream px-4 text-sm text-syncus-blue outline-none transition focus:border-syncus-green"
                      />
                    </label>
                  ))}
                </div>
              </div>
            )}

            {activeStep === 1 && (
              <div>
                <h2 className="mb-5 text-xl font-bold text-syncus-blue">Professional Details</h2>
                <div className="grid gap-4 md:grid-cols-2">
                  {professionalFields.map(({ label, key }) => (
                    <label key={key}>
                      <span className="mb-1.5 block text-xs font-bold text-syncus-blue/55">{label}</span>
                      <input
                        value={form[key]}
                        onChange={(event) => updateField(key, event.target.value)}
                        className="min-h-11 w-full rounded-xl border-2 border-syncus-blue/20 bg-syncus-cream px-4 text-sm text-syncus-blue outline-none transition focus:border-syncus-green"
                      />
                    </label>
                  ))}
                </div>
              </div>
            )}

            {activeStep === 2 && (
              <div>
                <h2 className="mb-5 text-xl font-bold text-syncus-blue">Skills & Expertise</h2>
                <div className="mb-5 flex flex-wrap gap-2">
                  {skills.map((skill) => (
                    <span
                      key={skill}
                      className="flex items-center gap-2 rounded-xl bg-syncus-blue px-3 py-1.5 text-sm font-bold text-syncus-cream"
                    >
                      {skill}
                      <button className="transition hover:opacity-70" onClick={() => removeSkill(skill)} type="button">
                        ×
                      </button>
                    </span>
                  ))}
                </div>

                <div className="mb-6 flex gap-2">
                  <input
                    value={newSkill}
                    onChange={(event) => setNewSkill(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        event.preventDefault();
                        addSkill(newSkill);
                      }
                    }}
                    placeholder="Add a skill..."
                    className="min-h-11 min-w-0 flex-1 rounded-xl border-2 border-syncus-blue bg-syncus-cream px-4 text-sm text-syncus-blue outline-none"
                  />
                  <button
                    onClick={() => addSkill(newSkill)}
                    className="grid min-h-11 w-11 place-items-center rounded-xl bg-syncus-blue text-syncus-cream"
                    type="button"
                    aria-label="Add skill"
                  >
                    <Plus size={16} />
                  </button>
                </div>

                <p className="mb-3 text-xs font-bold text-syncus-blue/50">Suggested</p>
                <div className="flex flex-wrap gap-2">
                  {skillSuggestions
                    .filter((suggestion) => !skills.includes(suggestion))
                    .map((suggestion) => (
                      <button
                        key={suggestion}
                        onClick={() => addSkill(suggestion)}
                        className="rounded-xl border-2 border-syncus-blue/20 px-3 py-1.5 text-sm font-bold text-syncus-blue transition hover:border-syncus-green hover:text-syncus-green"
                        type="button"
                      >
                        + {suggestion}
                      </button>
                    ))}
                </div>
              </div>
            )}

            {activeStep === 3 && (
              <div>
                <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <h2 className="text-xl font-bold text-syncus-blue">My Resumes</h2>
                  <button
                    className="flex min-h-11 items-center justify-center gap-2 rounded-xl bg-syncus-green px-4 text-sm font-bold text-syncus-cream disabled:opacity-60"
                    disabled={uploadingResume}
                    onClick={() => uploadInputRef.current?.click()}
                    type="button"
                  >
                    <Upload size={14} />
                    {uploadingResume ? "Uploading..." : "Upload Resume"}
                  </button>
                  <input
                    ref={uploadInputRef}
                    accept=".pdf,.doc,.docx"
                    className="hidden"
                    type="file"
                    onChange={(event) => void handleResumeUpload(event.target.files?.[0])}
                  />
                </div>

                <div className="grid gap-3">
                  {resumes.length === 0 && (
                    <p className="rounded-xl border-2 border-dashed border-syncus-blue/15 px-4 py-8 text-center text-sm font-medium text-syncus-blue/55">
                      No resumes uploaded yet. Upload a PDF or Word document to apply faster.
                    </p>
                  )}
                  {resumes.map((resume) => (
                    <article
                      key={resume.id}
                      className="flex flex-col gap-3 rounded-2xl border-2 border-syncus-blue/15 bg-syncus-cream p-4 sm:flex-row sm:items-center"
                      style={{ backgroundColor: resume.isDefault ? "rgba(0,128,77,0.06)" : "#f6f8ed" }}
                    >
                      <div
                        className="grid h-10 w-10 shrink-0 place-items-center rounded-xl"
                        style={{ backgroundColor: resume.isDefault ? "#00804d" : "rgba(30,72,144,0.1)" }}
                      >
                        <Briefcase size={16} color={resume.isDefault ? "#f6f8ed" : "#1e4890"} />
                      </div>
                      <div className="min-w-0 flex-1">
                        <a
                          className="truncate text-sm font-bold text-syncus-blue underline decoration-syncus-green underline-offset-4"
                          href={resume.fileUrl}
                          rel="noreferrer"
                          target="_blank"
                        >
                          {resume.name}
                        </a>
                        <p className="text-xs text-syncus-blue/50">Uploaded {resume.uploadedDate}</p>
                      </div>
                      {resume.isDefault && (
                        <span className="flex w-fit items-center gap-1 rounded-full bg-syncus-green px-3 py-1 text-xs font-bold text-syncus-cream">
                          <CheckCircle size={10} />
                          Primary
                        </span>
                      )}
                      <a
                        className="w-fit text-xs font-bold text-syncus-blue underline underline-offset-4"
                        href={resume.fileUrl}
                        rel="noreferrer"
                        target="_blank"
                      >
                        View
                      </a>
                    </article>
                  ))}
                </div>
              </div>
            )}

            <footer className="mt-8 flex flex-col gap-3 border-t border-syncus-blue/15 pt-5 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex gap-3">
                {activeStep > 0 && (
                  <button
                    onClick={() => setActiveStep((step) => step - 1)}
                    className="min-h-11 rounded-xl border-2 border-syncus-blue px-5 text-sm font-bold text-syncus-blue"
                    type="button"
                  >
                    Back
                  </button>
                )}
                {activeStep < steps.length - 1 && (
                  <button
                    onClick={() => setActiveStep((step) => step + 1)}
                    className="min-h-11 rounded-xl border-2 border-syncus-blue px-5 text-sm font-bold text-syncus-blue"
                    type="button"
                  >
                    Next
                  </button>
                )}
              </div>
              <button
                onClick={handleSave}
                className="flex min-h-11 items-center justify-center gap-2 rounded-xl bg-syncus-green px-6 text-sm font-bold text-syncus-cream"
                type="button"
                disabled={savingProfile}
              >
                {saved ? (
                  <>
                    <CheckCircle size={14} /> Saved!
                  </>
                ) : (
                  savingProfile ? "Saving..." : "Save Changes"
                )}
              </button>
            </footer>
          </section>
        </div>
      </section>
    </main>
  );
}