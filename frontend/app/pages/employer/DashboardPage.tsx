import { useEffect, useMemo, useState } from "react";
import { Bot, BriefcaseBusiness, CalendarDays, Download, Eye, Star, Users } from "lucide-react";
import { useNavigate } from "react-router";
import {
  getCandidateRecommendations,
  getEmployerJobs,
  getEmployerJobStats,
  getJobPipeline,
  type BackendJob,
  type CandidateRecommendation,
  type JobStatsResponse,
} from "../../lib/api";
import { jobs as sampleJobs } from "../../data/mockData";
import { EmployerShell } from "./EmployerShell";

const fallbackJobs = sampleJobs.slice(0, 3).map((job) => ({
  job_id: String(job.id),
  title: job.title,
  company_name: job.company,
  location: job.location,
  applications_count: job.applicants,
  views_count: job.applicants * 3,
  status: "published",
})) as Pick<BackendJob, "job_id" | "title" | "company_name" | "location" | "applications_count" | "views_count" | "status">[];

function StatCard({ icon: Icon, label, value, hint }: { icon: typeof BriefcaseBusiness; label: string; value: string | number; hint?: string }) {
  return (
    <article className="min-h-[150px] rounded-[18px] border-2 border-syncus-blue/55 bg-syncus-cream p-6">
      <span className="grid h-14 w-14 place-items-center rounded-xl bg-syncus-blue/20 text-syncus-blue">
        <Icon size={25} />
      </span>
      <p className="mt-4 text-sm font-medium text-syncus-blue">{label}</p>
      <p className="mt-1 text-3xl font-black leading-none text-syncus-blue">{value}</p>
      {hint && <p className="mt-1 text-xs italic text-syncus-blue/48">{hint}</p>}
    </article>
  );
}

export function EmployerDashboardPage() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState(fallbackJobs);
  const [stats, setStats] = useState<JobStatsResponse | null>(null);
  const [candidateMatches, setCandidateMatches] = useState<Record<string, CandidateRecommendation[]>>({});
  const [interviewCount, setInterviewCount] = useState(0);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    Promise.all([getEmployerJobs({ page_size: 20 }), getEmployerJobStats()])
      .then(async ([jobResponse, statsResponse]) => {
        if (!isMounted) return;
        const liveJobs = jobResponse.jobs;
        setJobs(liveJobs);
        setStats(statsResponse);
        setNotice(null);

        const topJobs = liveJobs.slice(0, 3);
        const pipelines = await Promise.allSettled(topJobs.map((job) => getJobPipeline(job.job_id)));
        if (isMounted) {
          setInterviewCount(
            pipelines.reduce((count, result) => {
              if (result.status !== "fulfilled") return count;
              return count + result.value.applications.filter((application) => application.status === "interview").length;
            }, 0)
          );
        }

        const matches = await Promise.allSettled(topJobs.map((job) => getCandidateRecommendations(job.job_id)));
        if (isMounted) {
          setCandidateMatches(
            Object.fromEntries(
              matches.map((result, index) => [
                topJobs[index]?.job_id,
                result.status === "fulfilled" ? result.value : [],
              ])
            )
          );
        }
      })
      .catch(() => {
        if (!isMounted) return;
        setNotice("Showing sample dashboard data until employer APIs are available.");
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const activeJobs = jobs.filter((job) => job.status === "published");
  const applicants = stats?.total_applications ?? jobs.reduce((sum, job) => sum + job.applications_count, 0);
  const averageMatch = useMemo(() => {
    const scores = Object.values(candidateMatches)
      .flat()
      .map((candidate) => Math.round(candidate.score * 100));

    if (scores.length === 0) return 94;
    return Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length);
  }, [candidateMatches]);

  return (
    <EmployerShell>
      <header className="mb-8 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="font-serif text-[clamp(2.7rem,5vw,5.2rem)] leading-none tracking-normal text-syncus-blue">
            Dashboard Overview
          </h1>
          <p className="mt-4 text-base font-medium text-syncus-blue">
            Welcome back, John. Here is what is happening with your hiring pipeline today.
          </p>
          {notice && <p className="mt-2 text-sm font-bold text-syncus-green">{notice}</p>}
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

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard icon={BriefcaseBusiness} label="Active Postings" value={stats?.published_count ?? activeJobs.length} />
        <StatCard icon={Users} label="Total Applicants" value={applicants} />
        <StatCard icon={Star} label="Shortlisted" value={Math.max(0, applicants ? Math.round(applicants * 0.2) : 84)} />
        <StatCard icon={Bot} label="AI Match Score" value={`${averageMatch}%`} hint="Avg. match quality across active roles" />
      </section>

      <section className="mt-9">
        <h2 className="font-serif text-[clamp(2rem,3vw,2.8rem)] leading-none text-syncus-blue">
          Active Job Postings ({activeJobs.length || jobs.length})
        </h2>
        <div className="mt-5 grid gap-4">
          {(activeJobs.length ? activeJobs : jobs).slice(0, 3).map((job) => {
            const topMatch = candidateMatches[job.job_id]?.[0];
            return (
              <article
                key={job.job_id}
                className="grid gap-4 rounded-[18px] border-2 border-syncus-blue bg-syncus-cream px-5 py-4 md:grid-cols-[auto_minmax(0,1fr)_88px_88px_auto] md:items-center"
              >
                <span className="grid h-12 w-12 place-items-center rounded-xl bg-syncus-blue text-syncus-cream">
                  <BriefcaseBusiness size={21} />
                </span>
                <div className="min-w-0">
                  <h3 className="truncate text-2xl font-medium leading-tight text-syncus-blue">{job.title}</h3>
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
                  <strong className="block text-2xl font-black">{job.applications_count}</strong>
                  <span className="text-xs text-syncus-blue/60">Applicants</span>
                </span>
                <span className="text-center">
                  <strong className="block text-2xl font-black">{Math.max(0, Math.round(job.applications_count * 0.1))}</strong>
                  <span className="text-xs text-syncus-blue/60">Interviews</span>
                </span>
                <button
                  className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-syncus-blue px-5 text-sm font-black text-syncus-cream transition hover:-translate-y-0.5"
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

      <section className="mt-10 max-w-[520px] rounded-[18px] border-2 border-syncus-blue bg-syncus-cream p-7">
        <h2 className="font-serif text-3xl leading-none">Upcoming Interviews</h2>
        <div className="mt-5 grid gap-3">
          {[0, 1].map((item) => (
            <article key={item} className="flex min-h-16 items-center gap-4 rounded-xl border-2 border-syncus-blue px-4">
              <span className="grid h-11 w-11 place-items-center rounded-lg bg-syncus-blue/15 text-xs font-black text-syncus-blue">
                OCT<br />24
              </span>
              <span className="min-w-0">
                <span className="block truncate text-sm font-black">Samantha Lee</span>
                <span className="block truncate text-xs text-syncus-blue/60">
                  Senior Product Designer · {item === 0 ? "10:00 AM" : "2:30 PM"} AEST
                </span>
              </span>
            </article>
          ))}
          <p className="text-xs font-bold text-syncus-blue/50">Live interview applications: {interviewCount}</p>
        </div>
      </section>
    </EmployerShell>
  );
}
