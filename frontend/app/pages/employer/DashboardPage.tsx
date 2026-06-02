import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Bot,
  BriefcaseBusiness,
  CalendarDays,
  Download,
  Eye,
  FilePenLine,
  Send,
  Star,
  Trash2,
  Users,
} from "lucide-react";
import { useNavigate } from "react-router";
import {
  deleteJob,
  getCandidateRecommendations,
  getEmployerJobs,
  getEmployerJobStats,
  getJobPipeline,
  publishJob,
  type BackendJob,
  type CandidateRecommendation,
  type JobStatsResponse,
} from "../../lib/api";
import { EmployerShell } from "./EmployerShell";

function StatCard({ icon: Icon, label, value, hint }: { icon: typeof BriefcaseBusiness; label: string; value: string | number; hint?: string }) {
  return (
    <article className="min-h-[124px] rounded-2xl border-2 border-syncus-blue/45 bg-syncus-cream p-4 sm:p-5">
      <span className="grid h-11 w-11 place-items-center rounded-xl bg-syncus-blue/20 text-syncus-blue">
        <Icon size={21} />
      </span>
      <p className="mt-3 text-xs font-black uppercase tracking-[0.06em] text-syncus-blue/65">{label}</p>
      <p className="mt-1 text-2xl font-black leading-none text-syncus-blue sm:text-[1.7rem]">{value}</p>
      {hint && <p className="mt-1 text-xs italic text-syncus-blue/48">{hint}</p>}
    </article>
  );
}

export function EmployerDashboardPage() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<BackendJob[]>([]);
  const [stats, setStats] = useState<JobStatsResponse | null>(null);
  const [candidateMatches, setCandidateMatches] = useState<Record<string, CandidateRecommendation[]>>({});
  const [interviewCount, setInterviewCount] = useState(0);
  const [interviewApplications, setInterviewApplications] = useState<
    { id: string; jobTitle: string; createdAt: string }[]
  >([]);
  const [shortlistedCount, setShortlistedCount] = useState(0);
  const [notice, setNotice] = useState<string | null>(null);
  const [actionJobId, setActionJobId] = useState<string | null>(null);

  const loadDashboard = useCallback(async () => {
    const [jobResponse, statsResponse] = await Promise.all([
      getEmployerJobs({ page_size: 50 }),
      getEmployerJobStats(),
    ]);

    const liveJobs = jobResponse.jobs;
    setJobs(liveJobs);
    setStats(statsResponse);
    setNotice(null);

    const publishedJobs = liveJobs.filter((job) => job.status === "published");
    const topJobs = publishedJobs.slice(0, 3);

    const pipelines = await Promise.allSettled(topJobs.map((job) => getJobPipeline(job.job_id)));
    const interviews: { id: string; jobTitle: string; createdAt: string }[] = [];
    let shortlistedCount = 0;

    pipelines.forEach((result, index) => {
      if (result.status !== "fulfilled") return;
      const jobTitle = topJobs[index]?.title ?? "Role";
      for (const application of result.value.applications) {
        if (application.status === "interview") {
          interviews.push({
            id: application.id,
            jobTitle,
            createdAt: application.created_at,
          });
        }
        if (application.status === "shortlisted") {
          shortlistedCount += 1;
        }
      }
    });

    setInterviewApplications(interviews.slice(0, 5));
    setInterviewCount(interviews.length);
    setShortlistedCount(shortlistedCount);

    const matches = await Promise.allSettled(topJobs.map((job) => getCandidateRecommendations(job.job_id)));
    setCandidateMatches(
      Object.fromEntries(
        matches.map((result, index) => [
          topJobs[index]?.job_id,
          result.status === "fulfilled" ? result.value : [],
        ])
      )
    );
  }, []);

  useEffect(() => {
    let isMounted = true;

    loadDashboard().catch((error) => {
      if (!isMounted) return;
      setJobs([]);
      setStats(null);
      setNotice(error instanceof Error ? error.message : "Employer APIs are unavailable.");
    });

    return () => {
      isMounted = false;
    };
  }, [loadDashboard]);

  const publishedJobs = useMemo(() => jobs.filter((job) => job.status === "published"), [jobs]);
  const draftJobs = useMemo(() => jobs.filter((job) => job.status === "draft"), [jobs]);
  const applicants = stats?.total_applications ?? jobs.reduce((sum, job) => sum + job.applications_count, 0);
  const averageMatch = useMemo(() => {
    const scores = Object.values(candidateMatches)
      .flat()
      .map((candidate) => Math.round(candidate.score * 100));

    if (scores.length === 0) return 0;
    return Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length);
  }, [candidateMatches]);

  const handlePublishDraft = async (jobId: string) => {
    setActionJobId(jobId);
    setNotice(null);
    try {
      await publishJob(jobId);
      await loadDashboard();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Could not publish draft.");
    } finally {
      setActionJobId(null);
    }
  };

  const handleDeleteDraft = async (job: BackendJob) => {
    if (!window.confirm(`Delete draft "${job.title}"? This cannot be undone.`)) {
      return;
    }

    setActionJobId(job.job_id);
    setNotice(null);
    try {
      await deleteJob(job.job_id);
      await loadDashboard();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Could not delete draft.");
    } finally {
      setActionJobId(null);
    }
  };

  return (
    <EmployerShell>
      <header className="mb-7 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="font-serif text-[clamp(2.35rem,4.2vw,4rem)] leading-none tracking-normal text-syncus-blue">
            Dashboard Overview
          </h1>
          <p className="mt-3 max-w-2xl text-sm font-medium leading-6 text-syncus-blue/70 sm:text-base">
            Welcome back. Here is what is happening with your hiring pipeline today.
          </p>
          {notice && <p className="mt-2 text-sm font-bold text-red-600">{notice}</p>}
        </div>
        <div className="flex flex-wrap gap-3">
          <button className="inline-flex min-h-10 items-center gap-2 rounded-lg bg-syncus-green px-4 text-xs font-black uppercase text-syncus-cream" type="button">
            <CalendarDays size={15} />
            Last 30 Days
          </button>
          <button className="inline-flex min-h-10 items-center gap-2 rounded-lg bg-syncus-green px-4 text-xs font-black uppercase text-syncus-cream" type="button">
            <Download size={15} />
            Download Report
          </button>
        </div>
      </header>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        <StatCard icon={BriefcaseBusiness} label="Active Postings" value={stats?.published_count ?? publishedJobs.length} />
        <StatCard icon={FilePenLine} label="Draft Jobs" value={stats?.draft_count ?? draftJobs.length} hint="Unpublished postings" />
        <StatCard icon={Users} label="Total Applicants" value={applicants} />
        <StatCard icon={Star} label="Shortlisted" value={shortlistedCount} hint="From active job pipelines" />
        <StatCard icon={Bot} label="AI Match Score" value={`${averageMatch}%`} hint="Avg. match quality across active roles" />
      </section>

      {draftJobs.length > 0 && (
        <section className="mt-8">
          <h2 className="font-serif text-[clamp(1.7rem,2.6vw,2.35rem)] leading-none text-syncus-blue">
            Draft Jobs ({draftJobs.length})
          </h2>
          <p className="mt-2 text-sm font-medium text-syncus-blue/60">
            Drafts are only visible to you until you publish them.
          </p>
          <div className="mt-4 grid gap-3">
            {draftJobs.map((job) => {
              const busy = actionJobId === job.job_id;
              return (
                <article
                  key={job.job_id}
                  className="grid gap-4 rounded-2xl border-2 border-dashed border-syncus-blue/40 bg-syncus-cream/80 px-4 py-4 md:grid-cols-[auto_minmax(0,1fr)_auto] md:items-center"
                >
                  <span className="grid h-10 w-10 place-items-center rounded-xl bg-syncus-blue/15 text-syncus-blue">
                    <FilePenLine size={18} />
                  </span>
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="truncate text-xl font-medium leading-tight text-syncus-blue">{job.title}</h3>
                      <span className="rounded-full border-2 border-syncus-blue/30 bg-white px-2.5 py-0.5 text-[0.65rem] font-black uppercase tracking-[0.12em] text-syncus-blue/70">
                        Draft
                      </span>
                    </div>
                    <p className="text-sm font-medium text-syncus-blue/70">
                      {job.company_name} · {job.location}
                    </p>
                    <p className="mt-1 text-xs font-bold text-syncus-blue/50">
                      Last updated {new Date(job.updated_at).toLocaleDateString("en-AU")}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button
                      className="inline-flex min-h-9 items-center justify-center gap-2 rounded-lg border-2 border-syncus-blue px-3 text-xs font-black text-syncus-blue transition hover:bg-syncus-blue/5 disabled:opacity-60 sm:text-sm"
                      disabled={busy}
                      onClick={() => navigate(`/employer/post-job?edit=${job.job_id}`)}
                      type="button"
                    >
                      <FilePenLine size={15} />
                      Edit
                    </button>
                    <button
                      className="inline-flex min-h-9 items-center justify-center gap-2 rounded-lg bg-syncus-green px-3 text-xs font-black text-syncus-cream transition hover:-translate-y-0.5 disabled:opacity-60 sm:text-sm"
                      disabled={busy}
                      onClick={() => void handlePublishDraft(job.job_id)}
                      type="button"
                    >
                      <Send size={15} />
                      {busy ? "Publishing..." : "Publish"}
                    </button>
                    <button
                      className="inline-flex min-h-9 items-center justify-center gap-2 rounded-lg border-2 border-red-300 px-3 text-xs font-black text-red-700 transition hover:bg-red-50 disabled:opacity-60 sm:text-sm"
                      disabled={busy}
                      onClick={() => void handleDeleteDraft(job)}
                      type="button"
                    >
                      <Trash2 size={15} />
                      Delete
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      )}

      <section className="mt-8">
        <h2 className="font-serif text-[clamp(1.7rem,2.6vw,2.35rem)] leading-none text-syncus-blue">
          Active Job Postings ({publishedJobs.length})
        </h2>
        <div className="mt-4 grid gap-3">
          {publishedJobs.length === 0 && (
            <div className="rounded-2xl border-2 border-dashed border-syncus-blue/35 px-6 py-10 text-center">
              <p className="text-lg font-black sm:text-xl">No published jobs yet.</p>
              <p className="mt-2 text-sm font-bold text-syncus-blue/55">
                Publish a draft or post a new job to start receiving applicants.
              </p>
              <button
                className="mt-5 inline-flex min-h-11 items-center justify-center rounded-lg bg-syncus-blue px-6 text-sm font-black text-syncus-cream"
                onClick={() => navigate("/employer/post-job")}
                type="button"
              >
                Post a New Job
              </button>
            </div>
          )}
          {publishedJobs.slice(0, 3).map((job) => {
            const topMatch = candidateMatches[job.job_id]?.[0];
            return (
              <article
                key={job.job_id}
                className="grid gap-4 rounded-2xl border-2 border-syncus-blue bg-syncus-cream px-4 py-4 md:grid-cols-[auto_minmax(0,1fr)_72px_72px_auto] md:items-center"
              >
                <span className="grid h-10 w-10 place-items-center rounded-xl bg-syncus-blue text-syncus-cream">
                  <BriefcaseBusiness size={18} />
                </span>
                <div className="min-w-0">
                  <h3 className="truncate text-xl font-medium leading-tight text-syncus-blue">{job.title}</h3>
                  <p className="text-sm font-medium text-syncus-blue/70">
                    {job.company_name} · {job.location}
                  </p>
                  {topMatch && (
                    <p className="mt-1 text-xs font-bold text-syncus-green">
                      Top AI match: {topMatch.name || "Candidate"} · {Math.round(topMatch.score * 100)}%
                    </p>
                  )}
                </div>
                <span className="text-center">
                  <strong className="block text-xl font-black">{job.applications_count}</strong>
                  <span className="text-xs text-syncus-blue/60">Applicants</span>
                </span>
                <span className="text-center">
                  <strong className="block text-xl font-black">{Math.max(0, Math.round(job.applications_count * 0.1))}</strong>
                  <span className="text-xs text-syncus-blue/60">Interviews</span>
                </span>
                <button
                  className="inline-flex min-h-9 items-center justify-center gap-2 rounded-lg bg-syncus-blue px-4 text-xs font-black text-syncus-cream transition hover:-translate-y-0.5 sm:text-sm"
                  onClick={() => navigate("/employer/review-applications", { state: { jobId: job.job_id } })}
                  type="button"
                >
                  <Eye size={15} />
                  View Applicants
                </button>
              </article>
            );
          })}
        </div>
      </section>

      <section className="mt-8 max-w-[620px] rounded-2xl border-2 border-syncus-blue bg-syncus-cream p-5 sm:p-6">
        <h2 className="font-serif text-[clamp(1.55rem,2.3vw,2rem)] leading-none">Upcoming Interviews</h2>
        <div className="mt-4 grid gap-3">
          {interviewCount === 0 ? (
            <p className="rounded-xl border-2 border-dashed border-syncus-blue/25 px-4 py-5 text-sm font-bold text-syncus-blue/55">
              No live interview applications yet.
            </p>
          ) : (
            interviewApplications.map((item) => {
              const date = new Date(item.createdAt);
              const month = date.toLocaleString("en-AU", { month: "short" }).toUpperCase();
              const day = date.getDate();

              return (
                <article key={item.id} className="flex min-h-16 items-center gap-4 rounded-xl border-2 border-syncus-blue px-4">
                  <span className="grid h-11 w-11 place-items-center rounded-lg bg-syncus-blue/15 text-xs font-black text-syncus-blue">
                    {month}
                    <br />
                    {day}
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-black">Interview scheduled</span>
                    <span className="block truncate text-xs text-syncus-blue/60">{item.jobTitle}</span>
                  </span>
                </article>
              );
            })
          )}
          <p className="text-xs font-bold text-syncus-blue/50">Live interview applications: {interviewCount}</p>
        </div>
      </section>
    </EmployerShell>
  );
}
