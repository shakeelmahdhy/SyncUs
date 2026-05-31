import { useEffect, useMemo, useState } from "react";
import { Bot, BriefcaseBusiness, CheckCircle2, Clock, Search, Users } from "lucide-react";
import { useLocation } from "react-router";
import {
  getCandidateRecommendations,
  getEmployerJobs,
  getJobPipeline,
  updateApplicationStatus,
  type ApplicationStatus,
  type BackendJob,
  type CandidateRecommendation,
  type TrackingApplication,
} from "../../lib/api";
import { EmployerShell } from "./EmployerShell";

const statusLabels: Record<ApplicationStatus, string> = {
  applied: "Applied",
  shortlisted: "Shortlisted",
  interview: "Interview",
  offered: "Offered",
  rejected: "Rejected",
  withdrawn: "Withdrawn",
};

const statusOptions: ApplicationStatus[] = ["applied", "shortlisted", "interview", "offered", "rejected"];

interface ApplicationRow {
  id: string;
  jobId: string;
  jobTitle: string;
  candidateId: string;
  candidateName: string;
  skills: string[];
  status: ApplicationStatus;
  createdAt: string;
  matchScore: number;
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("en-AU", { month: "short", day: "numeric", year: "numeric" });
}

function buildRows(
  jobs: Pick<BackendJob, "job_id" | "title">[],
  pipelines: Record<string, TrackingApplication[]>,
  matches: Record<string, CandidateRecommendation[]>
): ApplicationRow[] {
  return jobs.flatMap((job) => {
    const jobMatches = matches[job.job_id] ?? [];
    return (pipelines[job.job_id] ?? []).map((application) => {
      const match = jobMatches.find((candidate) => candidate.candidate_id === application.job_seeker_id);
      return {
        id: application.id,
        jobId: job.job_id,
        jobTitle: job.title,
        candidateId: application.job_seeker_id,
        candidateName: match?.name || `Candidate ${application.job_seeker_id.slice(0, 8)}`,
        skills: match?.skills ?? [],
        status: application.status,
        createdAt: application.created_at,
        matchScore: match ? Math.round(match.score * 100) : 0,
      };
    });
  });
}

export function EmployerReviewApplicationsPage() {
  const location = useLocation();
  const initialJobId = (location.state as { jobId?: string } | null)?.jobId ?? "all";
  const [jobs, setJobs] = useState<BackendJob[]>([]);
  const [rows, setRows] = useState<ApplicationRow[]>([]);
  const [selectedJobId, setSelectedJobId] = useState(initialJobId);
  const [query, setQuery] = useState("");
  const [notice, setNotice] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    getEmployerJobs({ page_size: 50 })
      .then(async (jobResponse) => {
        if (!isMounted) return;
        const liveJobs = jobResponse.jobs;
        setJobs(liveJobs);

        const [pipelineResults, matchResults] = await Promise.all([
          Promise.allSettled(liveJobs.map((job) => getJobPipeline(job.job_id))),
          Promise.allSettled(liveJobs.map((job) => getCandidateRecommendations(job.job_id))),
        ]);

        if (!isMounted) return;
        const pipelines = Object.fromEntries(
          pipelineResults.map((result, index) => [
            liveJobs[index].job_id,
            result.status === "fulfilled" ? result.value.applications : [],
          ])
        );
        const matches = Object.fromEntries(
          matchResults.map((result, index) => [
            liveJobs[index].job_id,
            result.status === "fulfilled" ? result.value : [],
          ])
        );

        setRows(buildRows(liveJobs, pipelines, matches));
        setNotice(null);
      })
      .catch((error) => {
        if (!isMounted) return;
        setJobs([]);
        setRows([]);
        setNotice(error instanceof Error ? error.message : "Jobs, tracking, or matching APIs are unavailable.");
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const visibleRows = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return rows.filter((row) => {
      const matchesJob = selectedJobId === "all" || row.jobId === selectedJobId;
      const matchesQuery =
        !normalizedQuery ||
        [row.candidateName, row.jobTitle, ...row.skills].some((value) => value.toLowerCase().includes(normalizedQuery));
      return matchesJob && matchesQuery;
    });
  }, [query, rows, selectedJobId]);

  const updateStatus = async (applicationId: string, status: ApplicationStatus) => {
    setUpdatingId(applicationId);
    try {
      await updateApplicationStatus(applicationId, status);
      setRows((current) =>
        current.map((row) => (row.id === applicationId ? { ...row, status } : row))
      );
      setNotice(null);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Application status could not be updated.");
    } finally {
      setUpdatingId(null);
    }
  };

  const counts = {
    total: rows.length,
    shortlisted: rows.filter((row) => row.status === "shortlisted").length,
    interview: rows.filter((row) => row.status === "interview").length,
  };

  return (
    <EmployerShell>
      <header className="mb-8 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="font-serif text-[clamp(2.55rem,5vw,4.8rem)] leading-none tracking-normal">
            Review Applications
          </h1>
          <p className="mt-4 text-base font-medium text-syncus-blue/68">
            Review tracking pipeline applications with AI match context from the matching module.
          </p>
          {notice && <p className="mt-2 text-sm font-bold text-red-600">{notice}</p>}
        </div>
        <label className="flex min-h-12 w-full max-w-[360px] items-center gap-3 rounded-lg border-2 border-syncus-blue/30 px-4">
          <Search size={18} />
          <input
            className="min-w-0 flex-1 bg-transparent text-sm font-bold outline-none placeholder:text-syncus-blue/45"
            placeholder="Search candidates, jobs, skills..."
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
      </header>

      <section className="mb-6 grid gap-4 sm:grid-cols-3">
        {[
          { label: "Applications", value: counts.total, icon: Users },
          { label: "Shortlisted", value: counts.shortlisted, icon: CheckCircle2 },
          { label: "Interviews", value: counts.interview, icon: Clock },
        ].map(({ label, value, icon: Icon }) => (
          <article key={label} className="rounded-[18px] border-2 border-syncus-blue/35 bg-syncus-cream p-5">
            <Icon className="text-syncus-blue" size={24} />
            <p className="mt-4 text-sm font-bold text-syncus-blue/58">{label}</p>
            <p className="text-3xl font-black">{value}</p>
          </article>
        ))}
      </section>

      <div className="mb-6 flex gap-2 overflow-x-auto pb-2">
        <button
          className={`min-h-11 shrink-0 rounded-lg border-2 px-4 text-sm font-black ${
            selectedJobId === "all" ? "border-syncus-blue bg-syncus-blue text-syncus-cream" : "border-syncus-blue/35 text-syncus-blue"
          }`}
          onClick={() => setSelectedJobId("all")}
          type="button"
        >
          All Jobs
        </button>
        {jobs.map((job) => (
          <button
            key={job.job_id}
            className={`min-h-11 shrink-0 rounded-lg border-2 px-4 text-sm font-black ${
              selectedJobId === job.job_id ? "border-syncus-blue bg-syncus-blue text-syncus-cream" : "border-syncus-blue/35 text-syncus-blue"
            }`}
            onClick={() => setSelectedJobId(job.job_id)}
            type="button"
          >
            {job.title}
          </button>
        ))}
      </div>

      <section className="grid gap-4">
        {visibleRows.length === 0 ? (
          <div className="rounded-[18px] border-2 border-dashed border-syncus-blue/30 py-14 text-center">
            <p className="text-xl font-black">No applications match this view.</p>
          </div>
        ) : (
          visibleRows.map((row) => (
            <article
              key={row.id}
              className="grid gap-4 rounded-[18px] border-2 border-syncus-blue bg-syncus-cream p-5 lg:grid-cols-[minmax(0,1fr)_110px_190px] lg:items-center"
            >
              <div className="min-w-0">
                <div className="flex items-start gap-3">
                  <span className="grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-syncus-blue text-syncus-cream">
                    <BriefcaseBusiness size={20} />
                  </span>
                  <span className="min-w-0">
                    <h2 className="truncate text-2xl font-medium leading-tight">{row.candidateName}</h2>
                    <p className="truncate text-sm font-bold text-syncus-blue/60">
                      {row.jobTitle} · Applied {formatDate(row.createdAt)}
                    </p>
                  </span>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {row.skills.slice(0, 4).map((skill) => (
                    <span key={skill} className="rounded-full border border-syncus-blue/25 px-3 py-1 text-xs font-bold">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              <div className="rounded-xl bg-syncus-blue/10 p-4 text-center">
                <Bot className="mx-auto text-syncus-blue" size={22} />
                <strong className="mt-2 block text-2xl font-black">{row.matchScore || "N/A"}{row.matchScore ? "%" : ""}</strong>
                <span className="text-xs font-bold text-syncus-blue/58">AI Match</span>
              </div>

              <label>
                <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">Pipeline status</span>
                <select
                  className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-3 text-sm font-black outline-none focus:border-syncus-green"
                  value={row.status}
                  disabled={updatingId === row.id}
                  onChange={(event) => void updateStatus(row.id, event.target.value as ApplicationStatus)}
                >
                  {statusOptions.map((status) => (
                    <option key={status} value={status}>
                      {statusLabels[status]}
                    </option>
                  ))}
                </select>
              </label>
            </article>
          ))
        )}
      </section>
    </EmployerShell>
  );
}
