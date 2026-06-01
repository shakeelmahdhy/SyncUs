import { useEffect, useMemo, useState } from "react";
import { BarChart3, BriefcaseBusiness, CalendarDays, CheckCircle2, TrendingUp, Users } from "lucide-react";
import {
  getEmployerJobs,
  getEmployerJobStats,
  getJobPipeline,
  searchCandidates,
  type BackendJob,
  type CandidateSearchResult,
  type JobStatsResponse,
} from "../../lib/api";
import { EmployerShell } from "./EmployerShell";

function StatCard({
  icon: Icon,
  label,
  value,
  detail,
}: {
  icon: typeof BarChart3;
  label: string;
  value: string | number;
  detail: string;
}) {
  return (
    <article className="rounded-2xl border-2 border-syncus-blue/20 bg-syncus-cream p-5 shadow-card">
      <span className="grid h-12 w-12 place-items-center rounded-xl bg-syncus-blue/10 text-syncus-blue">
        <Icon size={22} />
      </span>
      <p className="mt-4 text-sm font-bold text-syncus-blue/55">{label}</p>
      <p className="mt-1 text-3xl font-black leading-none text-syncus-blue">{value}</p>
      <p className="mt-2 text-xs font-medium text-syncus-blue/50">{detail}</p>
    </article>
  );
}

export function EmployerAnalyticsPage() {
  const [jobs, setJobs] = useState<BackendJob[]>([]);
  const [stats, setStats] = useState<JobStatsResponse | null>(null);
  const [funnel, setFunnel] = useState({ applied: 0, shortlisted: 0, interview: 0 });
  const [topCandidates, setTopCandidates] = useState<CandidateSearchResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const [jobResponse, statsResponse, candidateResponse] = await Promise.all([
          getEmployerJobs({ status_filter: "published", page_size: 50 }),
          getEmployerJobStats(),
          searchCandidates({ page_size: 4 }),
        ]);

        if (!isMounted) return;

        setJobs(jobResponse.jobs);
        setStats(statsResponse);
        setTopCandidates(candidateResponse.results);

        const pipelines = await Promise.allSettled(jobResponse.jobs.map((job) => getJobPipeline(job.job_id)));
        if (!isMounted) return;

        let applied = 0;
        let shortlisted = 0;
        let interview = 0;

        for (const result of pipelines) {
          if (result.status !== "fulfilled") continue;
          for (const application of result.value.applications) {
            if (application.status === "applied") applied += 1;
            if (application.status === "shortlisted") shortlisted += 1;
            if (application.status === "interview") interview += 1;
          }
        }

        setFunnel({ applied, shortlisted, interview });
      } catch (err) {
        if (!isMounted) return;
        setJobs([]);
        setStats(null);
        setTopCandidates([]);
        setFunnel({ applied: 0, shortlisted: 0, interview: 0 });
        setError(err instanceof Error ? err.message : "Analytics data is unavailable.");
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    void load();

    return () => {
      isMounted = false;
    };
  }, []);

  const topJobs = useMemo(
    () => [...jobs].sort((left, right) => right.applications_count - left.applications_count).slice(0, 4),
    [jobs]
  );

  const maxApplicants = Math.max(...topJobs.map((job) => job.applications_count), 1);
  const totalApplicants = stats?.total_applications ?? jobs.reduce((total, job) => total + job.applications_count, 0);
  const funnelTotal = Math.max(funnel.applied + funnel.shortlisted + funnel.interview, 1);

  const averageCandidateMatch = useMemo(() => {
    if (topCandidates.length === 0) return 0;
    return Math.round(
      topCandidates.reduce((total, candidate) => total + (candidate.profile_completeness ?? 0), 0) /
        topCandidates.length
    );
  }, [topCandidates]);

  const funnelItems = [
    { label: "Applied", value: funnel.applied, color: "bg-syncus-blue" },
    { label: "Shortlisted", value: funnel.shortlisted, color: "bg-syncus-green" },
    { label: "Interviewing", value: funnel.interview, color: "bg-syncus-lime" },
  ];

  return (
    <EmployerShell>
      <section className="text-syncus-blue">
        <header className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 className="font-serif text-[clamp(2.35rem,4vw,3.8rem)] leading-none text-syncus-blue">Analytics</h1>
            <p className="mt-3 max-w-2xl text-base font-medium text-syncus-blue/58">
              Hiring performance, pipeline health, and candidate discovery from live employer data.
            </p>
            {error && <p className="mt-3 text-sm font-bold text-red-600">{error}</p>}
          </div>
          <span className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-syncus-lime px-4 text-sm font-black text-syncus-blue">
            <TrendingUp size={17} />
            {loading ? "Loading..." : `${stats?.published_count ?? jobs.length} active roles`}
          </span>
        </header>

        <section className="mb-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            icon={BriefcaseBusiness}
            label="Active jobs"
            value={loading ? "—" : (stats?.published_count ?? jobs.length)}
            detail="Published roles"
          />
          <StatCard
            icon={Users}
            label="Applicants"
            value={loading ? "—" : totalApplicants}
            detail="Across all postings"
          />
          <StatCard
            icon={CheckCircle2}
            label="Candidate profiles"
            value={loading ? "—" : `${averageCandidateMatch}%`}
            detail="Avg. profile completeness (top pool)"
          />
          <StatCard
            icon={CalendarDays}
            label="Interviews"
            value={loading ? "—" : funnel.interview}
            detail="Applications in interview stage"
          />
        </section>

        <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
          <section className="rounded-2xl border-2 border-syncus-blue/20 bg-syncus-cream p-5 shadow-card">
            <div className="mb-5 flex items-center justify-between gap-3">
              <div>
                <h2 className="text-xl font-black text-syncus-blue">Role performance</h2>
                <p className="mt-1 text-sm font-medium text-syncus-blue/55">Applicant volume by published role.</p>
              </div>
              <BarChart3 className="text-syncus-green" size={24} />
            </div>

            <div className="grid gap-4">
              {!loading && topJobs.length === 0 && (
                <p className="rounded-xl border-2 border-dashed border-syncus-blue/25 px-4 py-8 text-center text-sm font-bold text-syncus-blue/55">
                  No published jobs yet.
                </p>
              )}
              {topJobs.map((job) => (
                <article className="rounded-xl border border-syncus-blue/15 p-4" key={job.job_id}>
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 className="font-black text-syncus-blue">{job.title}</h3>
                      <p className="text-sm font-medium text-syncus-blue/55">
                        {job.company_name} · {job.location}
                      </p>
                    </div>
                    <span className="rounded-full bg-syncus-lime px-3 py-1 text-xs font-black text-syncus-blue">
                      {job.views_count} views
                    </span>
                  </div>
                  <div className="mt-4 h-3 overflow-hidden rounded-full bg-syncus-blue/10">
                    <div
                      className="h-full rounded-full bg-syncus-green"
                      style={{ width: `${Math.max(8, (job.applications_count / maxApplicants) * 100)}%` }}
                    />
                  </div>
                  <p className="mt-2 text-xs font-bold text-syncus-blue/55">
                    {job.applications_count} applicants
                  </p>
                </article>
              ))}
            </div>
          </section>

          <aside className="grid gap-6">
            <section className="rounded-2xl border-2 border-syncus-blue/20 bg-syncus-cream p-5 shadow-card">
              <h2 className="text-xl font-black text-syncus-blue">Pipeline funnel</h2>
              <div className="mt-5 grid gap-4">
                {funnelItems.map((item) => (
                  <div key={item.label}>
                    <div className="mb-2 flex justify-between text-sm font-bold text-syncus-blue">
                      <span>{item.label}</span>
                      <span>{loading ? "—" : item.value}</span>
                    </div>
                    <div className="h-3 overflow-hidden rounded-full bg-syncus-blue/10">
                      <div
                        className={`h-full rounded-full ${item.color}`}
                        style={{ width: `${Math.max(10, (item.value / funnelTotal) * 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border-2 border-syncus-blue/20 bg-syncus-cream p-5 shadow-card">
              <h2 className="text-xl font-black text-syncus-blue">Top candidates</h2>
              <div className="mt-4 grid gap-3">
                {!loading && topCandidates.length === 0 && (
                  <p className="text-sm font-bold text-syncus-blue/50">No candidates in the pool yet.</p>
                )}
                {topCandidates.map((candidate) => (
                  <div className="rounded-xl bg-syncus-blue/5 p-4" key={candidate.candidate_id}>
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="font-black text-syncus-blue">{candidate.full_name}</p>
                        <p className="text-sm font-medium text-syncus-blue/55">{candidate.major ?? "Candidate"}</p>
                      </div>
                      <span className="rounded-full bg-syncus-green px-3 py-1 text-xs font-black text-syncus-cream">
                        {candidate.profile_completeness ?? 0}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border-2 border-syncus-blue/20 bg-syncus-blue p-5 text-syncus-cream shadow-card">
              <p className="text-sm font-bold text-white/62">Draft postings</p>
              <p className="mt-2 text-3xl font-black">{loading ? "—" : (stats?.draft_count ?? 0)}</p>
              <p className="mt-2 text-sm font-medium text-white/68">Unpublished roles waiting to go live.</p>
            </section>
          </aside>
        </div>
      </section>
    </EmployerShell>
  );
}
