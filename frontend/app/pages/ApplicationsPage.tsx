import { useEffect, useMemo, useState } from "react";
import {
  AlertCircle,
  CalendarDays,
  CheckCircle,
  ChevronRight,
  Clock,
  XCircle,
} from "lucide-react";
import { useNavigate } from "react-router";
import { listApplications, searchJobs } from "../lib/api";
import { type Application, toFrontendApplication, toFrontendJob } from "../lib/jobs";

const statusConfig: Record<
  Application["status"],
  { label: string; color: string; bg: string; icon: typeof CheckCircle }
> = {
  Applied: { label: "Applied", color: "#1e4890", bg: "#e5eceb", icon: Clock },
  Shortlisted: { label: "Shortlisted", color: "#d39000", bg: "#f5eed9", icon: CheckCircle },
  Interviewing: { label: "Interviewing", color: "#7c3aed", bg: "#eee1f8", icon: CalendarDays },
  Rejected: { label: "Rejected", color: "#dc2626", bg: "#f8dddd", icon: XCircle },
  Withdrawn: { label: "Withdrawn", color: "#6b7280", bg: "#e8e8e8", icon: AlertCircle },
};

const filterTabs = ["All", "Applied", "Shortlisted", "Interviewing", "Rejected"] as const;
type FilterTab = (typeof filterTabs)[number];

const inProgressStatuses: Application["status"][] = ["Applied", "Shortlisted", "Interviewing"];

export function ApplicationsPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<FilterTab>("All");
  const [trackedApplications, setTrackedApplications] = useState<Application[]>([]);
  const [loadingApplications, setLoadingApplications] = useState(true);
  const [applicationsError, setApplicationsError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    Promise.all([listApplications(), searchJobs({ page_size: 100 })])
      .then(([applicationResponse, jobResponse]) => {
        if (!isMounted) return;
        const jobsById = new Map(jobResponse.jobs.map((job) => [job.job_id, toFrontendJob(job)]));
        setTrackedApplications(
          applicationResponse.items.map((application) =>
            toFrontendApplication(application, jobsById.get(application.job_id))
          )
        );
        setApplicationsError(null);
      })
      .catch((error) => {
        if (!isMounted) return;
        setTrackedApplications([]);
        setApplicationsError(error instanceof Error ? error.message : "Applications could not be loaded.");
      })
      .finally(() => {
        if (isMounted) {
          setLoadingApplications(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const filtered =
    activeTab === "All"
      ? trackedApplications
      : trackedApplications.filter((application) => application.status === activeTab);

  const counts = Object.fromEntries(
    filterTabs.map((tab) => [
      tab,
      tab === "All"
        ? trackedApplications.length
        : trackedApplications.filter((application) => application.status === tab).length,
    ])
  ) as Record<FilterTab, number>;

  const averageMatch = useMemo(() => {
    if (trackedApplications.length === 0) return 0;

    return Math.round(
      trackedApplications.reduce((total, application) => total + application.matchScore, 0) /
        trackedApplications.length
    );
  }, [trackedApplications]);

  const stats = [
    { label: "Total Applied", value: trackedApplications.length, color: "#1e4890" },
    {
      label: "In Progress",
      value: trackedApplications.filter((application) => inProgressStatuses.includes(application.status)).length,
      color: "#00804d",
    },
    {
      label: "Interviews",
      value: trackedApplications.filter((application) => application.status === "Interviewing").length,
      color: "#7c3aed",
    },
    { label: "Avg. Match Score", value: `${averageMatch}%`, color: "#d39000" },
  ];

  return (
    <main className="bg-syncus-cream px-5 py-8 text-syncus-blue sm:px-8 lg:py-10">
      <section className="mx-auto max-w-[1120px]">
        <header className="mb-7">
          <h1 className="font-serif text-[clamp(2.35rem,4vw,3.8rem)] font-bold leading-none tracking-normal text-syncus-blue">
            My Applications
          </h1>
          <p className="mt-3 text-base font-medium text-syncus-blue/55 sm:text-lg">
            {loadingApplications ? "Loading your applications..." : "Track the progress of all your submitted applications"}
          </p>
          {applicationsError && (
            <p className="mt-2 text-sm font-bold text-red-600">
              {applicationsError}
            </p>
          )}
        </header>

        <div className="mb-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map(({ label, value, color }) => (
            <article
              key={label}
              className="min-h-[96px] rounded-2xl border-2 border-syncus-blue/15 bg-syncus-cream px-5 py-5"
            >
              <p className="text-sm font-bold text-syncus-blue/55">{label}</p>
              <p className="mt-2 text-[2.15rem] font-bold leading-none" style={{ color }}>
                {value}
              </p>
            </article>
          ))}
        </div>

        <div className="mb-7 flex gap-2.5 overflow-x-auto pb-2">
          {filterTabs.map((tab) => {
            const isActive = activeTab === tab;

            return (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className="flex min-h-11 shrink-0 items-center gap-2 rounded-xl border-2 px-4 text-sm font-bold transition hover:-translate-y-0.5 sm:text-base"
                style={{
                  backgroundColor: isActive ? "#1e4890" : "#f6f8ed",
                  borderColor: "#1e4890",
                  color: isActive ? "#f6f8ed" : "#1e4890",
                }}
                type="button"
              >
                {tab}
                {counts[tab] > 0 && (
                  <span
                    className="grid h-6 min-w-6 place-items-center rounded-full px-1.5 text-xs font-bold"
                    style={{
                      backgroundColor: isActive ? "#dbe64c" : "rgba(30,72,144,0.12)",
                      color: "#1e4890",
                    }}
                  >
                    {counts[tab]}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        <div className="grid gap-4">
          {filtered.length === 0 ? (
            <section className="rounded-2xl border-2 border-dashed border-syncus-blue/15 py-12 text-center">
              <p className="text-lg font-bold text-syncus-blue/55">
                {applicationsError ? "Applications are unavailable" : `No ${activeTab.toLowerCase()} applications`}
              </p>
            </section>
          ) : (
            filtered.map((application) => {
              const { color, bg, icon: StatusIcon } = statusConfig[application.status];

              return (
                <button
                  key={application.id}
                  className="grid min-h-[84px] grid-cols-[auto_1fr] items-center gap-x-4 gap-y-2 rounded-2xl border-2 border-syncus-blue/15 bg-syncus-cream px-4 py-4 text-left transition hover:-translate-y-0.5 hover:shadow-card sm:px-5 lg:grid-cols-[auto_minmax(0,1fr)_86px_126px_100px_22px] lg:gap-x-5"
                  onClick={() => navigate(`/jobs/${application.jobId}`)}
                  type="button"
                >
                  <span
                    className="grid h-12 w-12 place-items-center rounded-xl"
                    style={{ backgroundColor: bg, color }}
                  >
                    <StatusIcon size={20} />
                  </span>

                  <span className="min-w-0">
                    <span className="block truncate text-lg font-bold leading-tight text-syncus-blue sm:text-xl">
                      {application.title}
                    </span>
                    <span className="mt-1 block truncate text-sm font-medium text-syncus-blue/55 sm:text-base">
                      {application.company} · {application.location}
                    </span>
                  </span>

                  <span className="col-start-2 row-start-2 flex items-baseline gap-2 lg:col-auto lg:row-auto lg:block lg:text-center">
                    <span
                      className="block text-xl font-bold leading-none lg:text-2xl"
                      style={{ color: application.matchScore >= 90 ? "#00804d" : "#1e4890" }}
                    >
                      {application.matchScore}%
                    </span>
                    <span className="block text-sm font-medium text-syncus-blue/55 lg:mt-1">Match</span>
                  </span>

                  <span
                    className="col-start-2 row-start-3 w-fit rounded-full px-4 py-1.5 text-sm font-bold lg:col-auto lg:row-auto lg:justify-self-center"
                    style={{ backgroundColor: bg, color }}
                  >
                    {statusConfig[application.status].label}
                  </span>

                  <span className="col-start-2 row-start-4 text-sm font-medium text-syncus-blue/55 lg:col-auto lg:row-auto lg:justify-self-center">
                    {application.appliedDate}
                  </span>

                  <ChevronRight className="hidden text-syncus-blue lg:block" size={21} />
                </button>
              );
            })
          )}
        </div>
      </section>
    </main>
  );
}
