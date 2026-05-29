<<<<<<< HEAD
import { useEffect, useMemo, useState } from "react";
=======
import { useState } from "react";
>>>>>>> 28d9068 (Clean matching module branch for push)
import {
  AlertCircle,
  CalendarDays,
  CheckCircle,
  ChevronRight,
  Clock,
<<<<<<< HEAD
  XCircle,
} from "lucide-react";
import { useNavigate } from "react-router";
import { listApplications, searchJobs } from "../lib/api";
import { type Application, toFrontendApplication, toFrontendJob } from "../lib/jobs";
=======
  Eye,
  Trash2,
  XCircle,
} from "lucide-react";
import { useNavigate } from "react-router";
import { applications as initialApps } from "../data/mockData";
import type { Application } from "../data/mockData";
>>>>>>> 28d9068 (Clean matching module branch for push)

const statusConfig: Record<
  Application["status"],
  { label: string; color: string; bg: string; icon: typeof CheckCircle }
> = {
<<<<<<< HEAD
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
=======
  Applied: { label: "Applied", color: "#1e4890", bg: "rgba(30,72,144,0.12)", icon: Clock },
  Viewed: { label: "Viewed", color: "#00804d", bg: "rgba(0,128,77,0.12)", icon: Eye },
  Shortlisted: { label: "Shortlisted", color: "#ca8a04", bg: "rgba(202,138,4,0.12)", icon: CheckCircle },
  Interviewing: { label: "Interviewing", color: "#7c3aed", bg: "rgba(124,58,237,0.12)", icon: CalendarDays },
  Rejected: { label: "Not Progressed", color: "#dc2626", bg: "rgba(220,38,38,0.12)", icon: XCircle },
  Withdrawn: { label: "Withdrawn", color: "#6b7280", bg: "rgba(107,114,128,0.12)", icon: AlertCircle },
};

const filterTabs = ["All", "Applied", "Viewed", "Shortlisted", "Interviewing", "Rejected"] as const;
type FilterTab = (typeof filterTabs)[number];

export function ApplicationsPage() {
  const navigate = useNavigate();
  const [apps, setApps] = useState<Application[]>(initialApps);
  const [activeTab, setActiveTab] = useState<FilterTab>("All");
  const [withdrawingId, setWithdrawingId] = useState<number | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const filtered =
    activeTab === "All" ? apps : apps.filter((application) => application.status === activeTab);

  const handleWithdraw = (id: number) => {
    setApps((prev) =>
      prev.map((application) =>
        application.id === id ? { ...application, status: "Withdrawn" as const } : application
      )
    );
    setWithdrawingId(null);
  };
>>>>>>> 28d9068 (Clean matching module branch for push)

  const counts = Object.fromEntries(
    filterTabs.map((tab) => [
      tab,
<<<<<<< HEAD
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
=======
      tab === "All" ? apps.length : apps.filter((application) => application.status === tab).length,
    ])
  ) as Record<FilterTab, number>;

  const stats = [
    { label: "Total Applied", value: apps.length, color: "#1e4890" },
    {
      label: "In Progress",
      value: apps.filter((application) =>
        ["Applied", "Viewed", "Shortlisted", "Interviewing"].includes(application.status)
      ).length,
>>>>>>> 28d9068 (Clean matching module branch for push)
      color: "#00804d",
    },
    {
      label: "Interviews",
<<<<<<< HEAD
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
=======
      value: apps.filter((application) => application.status === "Interviewing").length,
      color: "#7c3aed",
    },
    {
      label: "Avg. Match Score",
      value: `${Math.round(apps.reduce((score, application) => score + application.matchScore, 0) / apps.length)}%`,
      color: "#ca8a04",
    },
  ];

  return (
    <div className="mx-auto max-w-screen-xl px-6 py-10">
      <div className="mb-8">
        <h1
          className="mb-2 text-4xl font-medium tracking-tight"
          style={{ fontFamily: "'Young Serif', serif", color: "#1e4890" }}
        >
          My Applications
        </h1>
        <p className="text-sm opacity-60" style={{ fontFamily: "'DM Sans', sans-serif", color: "#1e4890" }}>
          Track the progress of all your submitted applications
        </p>
      </div>

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map(({ label, value, color }) => (
          <div
            key={label}
            className="rounded-2xl p-5"
            style={{ backgroundColor: "#f6f8ed", border: "2px solid rgba(30,72,144,0.2)" }}
          >
            <p
              className="mb-1 text-xs font-medium opacity-60"
              style={{ fontFamily: "'DM Sans', sans-serif", color: "#1e4890" }}
            >
              {label}
            </p>
            <p className="text-3xl font-bold" style={{ fontFamily: "'DM Sans', sans-serif", color }}>
              {value}
            </p>
          </div>
        ))}
      </div>

      <div className="mb-6 flex gap-2 overflow-x-auto pb-1">
        {filterTabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className="flex shrink-0 items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition-all"
            style={{
              fontFamily: "'DM Sans', sans-serif",
              backgroundColor: activeTab === tab ? "#1e4890" : "transparent",
              color: activeTab === tab ? "#f6f8ed" : "#1e4890",
              border: "2px solid #1e4890",
            }}
            type="button"
          >
            {tab}
            {counts[tab] > 0 && (
              <span
                className="rounded-full px-1.5 py-0.5 text-xs"
                style={{
                  backgroundColor: activeTab === tab ? "#dbe64c" : "rgba(30,72,144,0.15)",
                  color: "#1e4890",
                }}
              >
                {counts[tab]}
              </span>
            )}
          </button>
        ))}
      </div>

      <div className="flex flex-col gap-4">
        {filtered.length === 0 ? (
          <div className="py-16 text-center" style={{ color: "#1e4890" }}>
            <p className="text-lg font-medium opacity-60" style={{ fontFamily: "'DM Sans', sans-serif" }}>
              No {activeTab.toLowerCase()} applications
            </p>
          </div>
        ) : (
          filtered.map((application) => {
            const { color, bg, icon: StatusIcon } = statusConfig[application.status];
            const isExpanded = expandedId === application.id;

            return (
              <div
                key={application.id}
                className="overflow-hidden rounded-2xl transition-shadow hover:shadow-md"
                style={{ border: "2px solid rgba(30,72,144,0.2)", backgroundColor: "#f6f8ed" }}
              >
                <button
                  className="flex w-full cursor-pointer items-center gap-4 p-5 text-left"
                  onClick={() => setExpandedId(isExpanded ? null : application.id)}
                  type="button"
                >
                  <div
                    className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl"
                    style={{ backgroundColor: bg }}
                  >
                    <StatusIcon size={18} style={{ color }} />
                  </div>

                  <div className="min-w-0 flex-1">
                    <p
                      className="truncate text-base font-semibold"
                      style={{ fontFamily: "'DM Sans', sans-serif", color: "#1e4890" }}
                    >
                      {application.title}
                    </p>
                    <p
                      className="mt-0.5 text-sm opacity-60"
                      style={{ fontFamily: "'DM Sans', sans-serif", color: "#1e4890" }}
                    >
                      {application.company} · {application.location}
                    </p>
                  </div>

                  <div className="shrink-0 text-center">
                    <p
                      className="text-xl font-bold"
                      style={{
                        color: application.matchScore >= 90 ? "#00804d" : "#1e4890",
                        fontFamily: "'DM Sans', sans-serif",
                      }}
                    >
                      {application.matchScore}%
                    </p>
                    <p className="text-xs opacity-50" style={{ fontFamily: "'DM Sans', sans-serif", color: "#1e4890" }}>
                      Match
                    </p>
                  </div>

                  <div className="shrink-0 rounded-xl px-3 py-1.5 text-xs font-semibold" style={{ backgroundColor: bg, color }}>
                    {statusConfig[application.status].label}
                  </div>

                  <p
                    className="shrink-0 text-xs opacity-50"
                    style={{ fontFamily: "'DM Sans', sans-serif", color: "#1e4890" }}
                  >
                    {application.appliedDate}
                  </p>

                  <ChevronRight
                    size={16}
                    className={`shrink-0 transition-transform ${isExpanded ? "rotate-90" : ""}`}
                    style={{ color: "#1e4890" }}
                  />
                </button>

                {isExpanded && (
                  <div className="border-t px-5 pb-5" style={{ borderColor: "rgba(30,72,144,0.15)" }}>
                    <div className="grid gap-4 pt-4 text-sm md:grid-cols-2">
                      <div>
                        <p
                          className="mb-1 text-xs font-semibold opacity-50"
                          style={{ fontFamily: "'DM Sans', sans-serif", color: "#1e4890" }}
                        >
                          Resume Submitted
                        </p>
                        <p style={{ fontFamily: "'DM Sans', sans-serif", color: "#1e4890" }}>
                          {application.resume}
                        </p>
                      </div>
                      {application.notes && (
                        <div>
                          <p
                            className="mb-1 text-xs font-semibold opacity-50"
                            style={{ fontFamily: "'DM Sans', sans-serif", color: "#1e4890" }}
                          >
                            Notes
                          </p>
                          <p style={{ fontFamily: "'DM Sans', sans-serif", color: "#1e4890" }}>
                            {application.notes}
                          </p>
                        </div>
                      )}
                    </div>

                    {!["Withdrawn", "Rejected"].includes(application.status) && (
                      <div className="mt-4 flex flex-wrap items-center gap-3">
                        <button
                          onClick={(event) => {
                            event.stopPropagation();
                            navigate(`/jobs/${application.jobId}`);
                          }}
                          className="flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium"
                          style={{ border: "2px solid #1e4890", color: "#1e4890", fontFamily: "'DM Sans', sans-serif" }}
                          type="button"
                        >
                          View Job
                          <ChevronRight size={14} />
                        </button>
                        <button
                          onClick={(event) => {
                            event.stopPropagation();
                            setWithdrawingId(application.id);
                          }}
                          className="flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium"
                          style={{ border: "2px solid #dc2626", color: "#dc2626", fontFamily: "'DM Sans', sans-serif" }}
                          type="button"
                        >
                          <Trash2 size={14} />
                          Withdraw Application
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {withdrawingId !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div
            className="mx-4 w-full max-w-sm rounded-3xl p-8 shadow-2xl"
            style={{ backgroundColor: "#f6f8ed", border: "2px solid #dc2626" }}
          >
            <h3
              className="mb-3 text-xl font-bold"
              style={{ fontFamily: "'Young Serif', serif", color: "#1e4890" }}
            >
              Withdraw Application?
            </h3>
            <p className="mb-6 text-sm opacity-70" style={{ fontFamily: "'DM Sans', sans-serif", color: "#1e4890" }}>
              This will notify the employer that you are no longer interested in this role.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => handleWithdraw(withdrawingId)}
                className="flex-1 rounded-2xl py-3 text-sm font-bold"
                style={{ backgroundColor: "#dc2626", color: "#f6f8ed", fontFamily: "'DM Sans', sans-serif" }}
                type="button"
              >
                Yes, Withdraw
              </button>
              <button
                onClick={() => setWithdrawingId(null)}
                className="flex-1 rounded-2xl py-3 text-sm font-bold"
                style={{ border: "2px solid #1e4890", color: "#1e4890", fontFamily: "'DM Sans', sans-serif" }}
                type="button"
              >
                Keep Application
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
>>>>>>> 28d9068 (Clean matching module branch for push)
  );
}
