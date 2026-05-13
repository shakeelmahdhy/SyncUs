import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router";
import {
  Briefcase,
  CheckCircle,
  ChevronLeft,
  Clock,
  DollarSign,
  MapPin,
  Monitor,
  Star,
  Zap,
} from "lucide-react";
import { jobs } from "../data/mockData";
import type { Job } from "../data/mockData";
import { getJob, searchJobs } from "../lib/api";
import { storeApplication, toFrontendJob } from "../lib/jobs";
import { SyncUsMark } from "../shared/components";

export function JobDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState<Job | null>(null);
  const [allJobs, setAllJobs] = useState<Job[]>(jobs);
  const [loadingJob, setLoadingJob] = useState(true);
  const [jobError, setJobError] = useState<string | null>(null);
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [coverLetter, setCoverLetter] = useState("");
  const [selectedResume, setSelectedResume] = useState("Product_Designer_Resume_v3.pdf");

  useEffect(() => {
    if (!id) return;

    let isMounted = true;
    const fallbackJob = jobs.find((currentJob) => String(currentJob.id) === id) ?? null;

    setLoadingJob(true);
    setJobError(null);

    Promise.all([
      getJob(id).then(toFrontendJob),
      searchJobs({ page_size: 100 }).then((response) => response.jobs.map(toFrontendJob)),
    ])
      .then(([apiJob, apiJobs]) => {
        if (!isMounted) return;
        setJob(apiJob);
        setAllJobs(apiJobs.length > 0 ? apiJobs : jobs);
      })
      .catch(() => {
        if (!isMounted) return;
        setJob(fallbackJob);
        setAllJobs(jobs);
        setJobError("Showing local job details until the jobs API is available.");
      })
      .finally(() => {
        if (isMounted) {
          setLoadingJob(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [id]);

  const similar = useMemo(
    () =>
      allJobs
        .filter((currentJob) => String(currentJob.id) !== String(job?.id) && currentJob.category === job?.category)
        .slice(0, 2),
    [allJobs, job?.category, job?.id]
  );

  if (loadingJob) {
    return (
      <main className="flex h-96 items-center justify-center px-6">
        <p className="text-xl font-medium text-syncus-blue">Loading job details...</p>
      </main>
    );
  }

  if (!job) {
    return (
      <main className="flex h-96 items-center justify-center px-6">
        <div className="text-center">
          <p className="text-xl font-medium">Job not found</p>
          <button className="mt-4 text-sm underline" onClick={() => navigate("/")} type="button">
            Browse all jobs
          </button>
        </div>
      </main>
    );
  }

  const handleSubmit = () => {
    storeApplication(job, selectedResume, coverLetter);
    setSubmitted(true);
    window.setTimeout(() => {
      setShowApplyModal(false);
      setSubmitted(false);
      navigate("/applications");
    }, 1800);
  };

  return (
    <div>
      <main className="mx-auto max-w-screen-xl px-6 py-10">
        <button
          onClick={() => navigate(-1)}
          className="mb-6 flex items-center gap-2 text-sm font-bold text-syncus-green transition-opacity hover:opacity-70"
          type="button"
        >
          <ChevronLeft size={16} />
          Back to Jobs
        </button>

        {jobError && (
          <p className="mb-5 rounded-xl border-2 border-syncus-blue/15 bg-syncus-blue/5 px-4 py-3 text-sm font-bold text-syncus-blue">
            {jobError}
          </p>
        )}

        <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
          <div>
            <section className="mb-6 rounded-3xl border-2 border-syncus-green bg-syncus-cream p-6 shadow-sm sm:p-8">
              <div className="mb-5 flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
                <div className="flex items-start gap-5">
                  <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-syncus-green p-3">
                    <SyncUsMark compact />
                  </div>
                  <div>
                    <h1 className="mb-1 text-3xl font-medium tracking-normal text-syncus-green">
                      {job.title}
                    </h1>
                    <p className="text-base text-syncus-green">
                      {job.company} ·{" "}
                      <span className="inline-flex items-center gap-1">
                        <MapPin size={13} />
                        {job.location}
                      </span>
                    </p>
                  </div>
                </div>
                <div className="flex shrink-0 flex-wrap gap-2 md:flex-col md:items-end">
                  {job.recommended && (
                    <span className="flex items-center gap-1 rounded-full bg-syncus-blue px-3 py-1.5 text-xs font-bold text-syncus-cream">
                      <Star size={10} fill="currentColor" /> Recommended
                    </span>
                  )}
                  <span className="rounded-full bg-syncus-lime px-3 py-1.5 text-sm font-bold text-syncus-blue">
                    {job.matchScore}% Match
                  </span>
                </div>
              </div>

              <div className="mb-5 flex flex-wrap gap-2">
                <span className="flex items-center gap-1.5 rounded-xl bg-syncus-green/55 px-3 py-1.5 text-xs font-medium text-white">
                  <Monitor size={12} /> {job.locationMode}
                </span>
                <span className="flex items-center gap-1.5 rounded-xl bg-syncus-green/55 px-3 py-1.5 text-xs font-medium text-white">
                  <Clock size={12} /> {job.workType}
                </span>
                <span className="flex items-center gap-1.5 rounded-xl bg-syncus-blue/50 px-3 py-1.5 text-xs font-medium text-white">
                  <Zap size={12} /> Responds within {job.respondsWithin}
                </span>
                <span className="flex items-center gap-1.5 rounded-xl bg-syncus-blue/50 px-3 py-1.5 text-xs font-medium text-white">
                  <DollarSign size={12} /> {job.salary}
                </span>
                <span className="flex items-center gap-1.5 rounded-xl bg-syncus-blue/50 px-3 py-1.5 text-xs font-medium text-white">
                  <Briefcase size={12} /> {job.experience}
                </span>
              </div>

              <div className="mb-5 flex flex-wrap gap-6 text-sm text-syncus-blue">
                <span className="opacity-60">{job.applicants} applicants</span>
                <span className="opacity-60">Posted {job.postedDate}</span>
                <span className="opacity-60">{job.interviews} interviews scheduled</span>
              </div>

              <button
                onClick={() => setShowApplyModal(true)}
                className="rounded-2xl bg-syncus-blue px-10 py-3 text-base font-bold text-syncus-cream transition hover:bg-syncus-green"
                type="button"
              >
                Apply Now
              </button>
            </section>

            <section className="mb-6 rounded-3xl border-2 border-syncus-green/30 bg-syncus-cream p-6 shadow-sm sm:p-8">
              <h2 className="mb-4 font-serif text-2xl font-bold text-syncus-blue">About the Role</h2>
              <p className="text-sm leading-relaxed text-syncus-blue">{job.fullDescription}</p>
            </section>

            <section className="mb-6 rounded-3xl border-2 border-syncus-green/30 bg-syncus-cream p-6 shadow-sm sm:p-8">
              <h2 className="mb-4 font-serif text-2xl font-bold text-syncus-blue">Requirements</h2>
              <ul className="flex flex-col gap-3">
                {job.requirements.map((requirement) => (
                  <li key={requirement} className="flex items-start gap-3">
                    <CheckCircle size={16} className="mt-0.5 shrink-0 text-syncus-green" />
                    <span className="text-sm text-syncus-blue">{requirement}</span>
                  </li>
                ))}
              </ul>
            </section>

            <section className="rounded-3xl border-2 border-syncus-green/30 bg-syncus-cream p-6 shadow-sm sm:p-8">
              <h2 className="mb-4 font-serif text-2xl font-bold text-syncus-blue">Key Skills</h2>
              <div className="flex flex-wrap gap-2">
                {job.skills.map((skill) => (
                  <span key={skill} className="rounded-xl bg-syncus-blue/10 px-4 py-2 text-sm font-medium text-syncus-blue">
                    {skill}
                  </span>
                ))}
              </div>
            </section>
          </div>

          <aside className="flex flex-col gap-5">
            <section className="rounded-2xl border-2 border-syncus-blue bg-syncus-cream p-5 shadow-sm">
              <h3 className="mb-3 font-bold text-syncus-blue">Quick Apply</h3>
              <p className="mb-4 text-xs text-syncus-blue/60">Apply in under 60 seconds using your saved profile.</p>
              <button
                onClick={() => setShowApplyModal(true)}
                className="w-full rounded-2xl bg-syncus-green py-3 text-sm font-bold text-syncus-cream transition hover:bg-syncus-blue"
                type="button"
              >
                Quick Apply
              </button>
            </section>

            <section className="rounded-2xl border-2 border-syncus-green/30 bg-syncus-cream p-5 shadow-sm">
              <h3 className="mb-3 font-bold text-syncus-blue">About {job.company}</h3>
              <div className="flex flex-col gap-2 text-xs text-syncus-blue/60">
                <p>Category: {job.category}</p>
                <p>Location: {job.location}</p>
                <p>Response time: Responds within {job.respondsWithin}</p>
              </div>
            </section>

            {similar.length > 0 && (
              <section>
                <h3 className="mb-3 font-bold text-syncus-blue">Similar Roles</h3>
                <div className="flex flex-col gap-3">
                  {similar.map((similarJob) => (
                    <button
                      key={similarJob.id}
                      className="rounded-2xl border-2 border-syncus-green/30 bg-syncus-cream p-4 text-left transition hover:shadow-md"
                      onClick={() => navigate(`/jobs/${similarJob.id}`)}
                      type="button"
                    >
                      <p className="text-sm font-semibold text-syncus-green">{similarJob.title}</p>
                      <p className="mt-0.5 text-xs text-syncus-blue/60">
                        {similarJob.company} · {similarJob.matchScore}% match
                      </p>
                    </button>
                  ))}
                </div>
              </section>
            )}
          </aside>
        </div>
      </main>

      {showApplyModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
          <section className="w-full max-w-md rounded-3xl border-2 border-syncus-green bg-syncus-cream p-8 shadow-2xl">
            {submitted ? (
              <div className="py-6 text-center">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-syncus-green">
                  <CheckCircle size={32} color="#f6f8ed" />
                </div>
                <h3 className="mb-2 font-serif text-xl font-bold text-syncus-blue">Application Submitted!</h3>
                <p className="text-sm text-syncus-blue/60">Redirecting to your applications...</p>
              </div>
            ) : (
              <>
                <h3 className="mb-1 font-serif text-xl font-bold text-syncus-blue">Apply to {job.title}</h3>
                <p className="mb-5 text-sm text-syncus-blue/60">
                  {job.company} · {job.location}
                </p>
                <label className="mb-4 block">
                  <span className="mb-1.5 block text-xs font-semibold text-syncus-blue/60">Select Resume *</span>
                  <select
                    value={selectedResume}
                    onChange={(event) => setSelectedResume(event.target.value)}
                    className="w-full rounded-xl border-2 border-syncus-green bg-syncus-cream px-3 py-2.5 text-sm text-syncus-blue outline-none"
                  >
                    <option>Product_Designer_Resume_v3.pdf</option>
                    <option>Frontend_Engineer_Resume.pdf</option>
                    <option>General_Resume_2026.pdf</option>
                  </select>
                </label>
                <label className="mb-6 block">
                  <span className="mb-1.5 block text-xs font-semibold text-syncus-blue/60">Cover Letter (optional)</span>
                  <textarea
                    rows={4}
                    placeholder={`Tell ${job.company} why you're a great fit...`}
                    value={coverLetter}
                    onChange={(event) => setCoverLetter(event.target.value)}
                    className="w-full resize-none rounded-xl border-2 border-syncus-green/30 bg-syncus-cream px-3 py-2.5 text-sm text-syncus-blue outline-none"
                  />
                </label>
                <div className="flex gap-3">
                  <button
                    onClick={handleSubmit}
                    className="flex-1 rounded-2xl bg-syncus-green py-3 text-sm font-bold text-syncus-cream"
                    type="button"
                  >
                    Submit Application
                  </button>
                  <button
                    onClick={() => setShowApplyModal(false)}
                    className="rounded-2xl border-2 border-syncus-green px-5 py-3 text-sm font-bold text-syncus-green"
                    type="button"
                  >
                    Cancel
                  </button>
                </div>
              </>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
