import { BarChart3, BriefcaseBusiness, CalendarDays, CheckCircle2, TrendingUp, Users } from "lucide-react";
import { applications, candidates, jobs, teamMembers } from "../../data/mockData";
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

const funnel = [
  { label: "Applied", value: applications.length, color: "bg-syncus-blue" },
  { label: "Shortlisted", value: applications.filter((application) => application.status === "Shortlisted").length, color: "bg-syncus-green" },
  { label: "Interviewing", value: applications.filter((application) => application.status === "Interviewing").length, color: "bg-syncus-lime" },
];

export function EmployerAnalyticsPage() {
  const averageJobMatch = Math.round(jobs.reduce((total, job) => total + job.matchScore, 0) / jobs.length);
  const averageCandidateMatch = Math.round(
    candidates.reduce((total, candidate) => total + candidate.matchScore, 0) / candidates.length
  );
  const totalApplicants = jobs.reduce((total, job) => total + job.applicants, 0);
  const topJobs = [...jobs].sort((left, right) => right.applicants - left.applicants).slice(0, 4);
  const topCandidates = [...candidates].sort((left, right) => right.matchScore - left.matchScore).slice(0, 4);
  const maxApplicants = Math.max(...topJobs.map((job) => job.applicants), 1);

  return (
    <EmployerShell>
      <section className="text-syncus-blue">
        <header className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 className="font-serif text-[clamp(2.35rem,4vw,3.8rem)] leading-none text-syncus-blue">
              Analytics
            </h1>
            <p className="mt-3 max-w-2xl text-base font-medium text-syncus-blue/58">
              Hiring performance, matching quality, and pipeline health across active roles.
            </p>
          </div>
          <span className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-syncus-lime px-4 text-sm font-black text-syncus-blue">
            <TrendingUp size={17} />
            {averageJobMatch}% average role match
          </span>
        </header>

        <section className="mb-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard icon={BriefcaseBusiness} label="Active jobs" value={jobs.length} detail="Open roles currently listed" />
          <StatCard icon={Users} label="Applicants" value={totalApplicants} detail="Across all active postings" />
          <StatCard icon={CheckCircle2} label="Candidate match" value={`${averageCandidateMatch}%`} detail="Average recommended talent score" />
          <StatCard icon={CalendarDays} label="Interviews" value={jobs.reduce((total, job) => total + job.interviews, 0)} detail="Scheduled from open pipelines" />
        </section>

        <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
          <section className="rounded-2xl border-2 border-syncus-blue/20 bg-syncus-cream p-5 shadow-card">
            <div className="mb-5 flex items-center justify-between gap-3">
              <div>
                <h2 className="text-xl font-black text-syncus-blue">Role performance</h2>
                <p className="mt-1 text-sm font-medium text-syncus-blue/55">Applicant volume and match quality by role.</p>
              </div>
              <BarChart3 className="text-syncus-green" size={24} />
            </div>

            <div className="grid gap-4">
              {topJobs.map((job) => (
                <article className="rounded-xl border border-syncus-blue/15 p-4" key={job.id}>
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 className="font-black text-syncus-blue">{job.title}</h3>
                      <p className="text-sm font-medium text-syncus-blue/55">{job.company} · {job.location}</p>
                    </div>
                    <span className="rounded-full bg-syncus-lime px-3 py-1 text-xs font-black text-syncus-blue">
                      {job.matchScore}% match
                    </span>
                  </div>
                  <div className="mt-4 h-3 overflow-hidden rounded-full bg-syncus-blue/10">
                    <div
                      className="h-full rounded-full bg-syncus-green"
                      style={{ width: `${Math.max(8, (job.applicants / maxApplicants) * 100)}%` }}
                    />
                  </div>
                  <p className="mt-2 text-xs font-bold text-syncus-blue/55">
                    {job.applicants} applicants · {job.interviews} interviews
                  </p>
                </article>
              ))}
            </div>
          </section>

          <aside className="grid gap-6">
            <section className="rounded-2xl border-2 border-syncus-blue/20 bg-syncus-cream p-5 shadow-card">
              <h2 className="text-xl font-black text-syncus-blue">Pipeline funnel</h2>
              <div className="mt-5 grid gap-4">
                {funnel.map((item) => (
                  <div key={item.label}>
                    <div className="mb-2 flex justify-between text-sm font-bold text-syncus-blue">
                      <span>{item.label}</span>
                      <span>{item.value}</span>
                    </div>
                    <div className="h-3 overflow-hidden rounded-full bg-syncus-blue/10">
                      <div
                        className={`h-full rounded-full ${item.color}`}
                        style={{ width: `${Math.max(10, (item.value / Math.max(applications.length, 1)) * 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border-2 border-syncus-blue/20 bg-syncus-cream p-5 shadow-card">
              <h2 className="text-xl font-black text-syncus-blue">Top candidates</h2>
              <div className="mt-4 grid gap-3">
                {topCandidates.map((candidate) => (
                  <div className="rounded-xl bg-syncus-blue/5 p-4" key={candidate.id}>
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="font-black text-syncus-blue">{candidate.name}</p>
                        <p className="text-sm font-medium text-syncus-blue/55">{candidate.role}</p>
                      </div>
                      <span className="rounded-full bg-syncus-green px-3 py-1 text-xs font-black text-syncus-cream">
                        {candidate.matchScore}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border-2 border-syncus-blue/20 bg-syncus-blue p-5 text-syncus-cream shadow-card">
              <p className="text-sm font-bold text-white/62">Hiring team coverage</p>
              <p className="mt-2 text-3xl font-black">{teamMembers.length} collaborators</p>
              <p className="mt-2 text-sm font-medium text-white/68">
                {teamMembers.filter((member) => member.jobsAssigned.length > 0).length} assigned to active roles.
              </p>
            </section>
          </aside>
        </div>
      </section>
    </EmployerShell>
  );
}
