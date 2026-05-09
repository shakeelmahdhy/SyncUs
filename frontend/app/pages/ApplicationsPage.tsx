import { useState } from "react";
import {
  AlertCircle,
  CalendarDays,
  CheckCircle,
  ChevronRight,
  Clock,
  Eye,
  XCircle,
} from "lucide-react";
import { useNavigate } from "react-router";
import { applications } from "../data/mockData";
import type { Application } from "../data/mockData";

const statusConfig: Record<
  Application["status"],
  { label: string; color: string; bg: string; icon: typeof CheckCircle }
> = {
  Applied: { label: "Applied", color: "#1e4890", bg: "#e5eceb", icon: Clock },
  Viewed: { label: "Viewed", color: "#00804d", bg: "#e1f0df", icon: Eye },
  Shortlisted: { label: "Shortlisted", color: "#d39000", bg: "#f5eed9", icon: CheckCircle },
  Interviewing: { label: "Interviewing", color: "#7c3aed", bg: "#eee1f8", icon: CalendarDays },
  Rejected: { label: "Rejected", color: "#dc2626", bg: "#f8dddd", icon: XCircle },
  Withdrawn: { label: "Withdrawn", color: "#6b7280", bg: "#e8e8e8", icon: AlertCircle },
};

const filterTabs = ["All", "Applied", "Viewed", "Shortlisted", "Interviewing", "Rejected"] as const;
type FilterTab = (typeof filterTabs)[number];

const inProgressStatuses: Application["status"][] = ["Applied", "Viewed", "Shortlisted", "Interviewing"];

export function ApplicationsPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<FilterTab>("All");

  const filtered =
    activeTab === "All"
      ? applications
      : applications.filter((application) => application.status === activeTab);

  const counts = Object.fromEntries(
    filterTabs.map((tab) => [
      tab,
      tab === "All"
        ? applications.length
        : applications.filter((application) => application.status === tab).length,
    ])
  ) as Record<FilterTab, number>;

  const averageMatch = Math.round(
    applications.reduce((total, application) => total + application.matchScore, 0) / applications.length
  );

  const stats = [
    { label: "Total Applied", value: applications.length, color: "#1e4890" },
    {
      label: "In Progress",
      value: applications.filter((application) => inProgressStatuses.includes(application.status)).length,
      color: "#00804d",
    },
    {
      label: "Interviews",
      value: applications.filter((application) => application.status === "Interviewing").length,
      color: "#7c3aed",
    },
    { label: "Avg. Match Score", value: `${averageMatch}%`, color: "#d39000" },
  ];

  return (
    <main className="min-h-screen bg-syncus-cream px-6 py-10 text-syncus-blue sm:px-10">
      <section className="mx-auto max-w-[1580px]">
        <header className="mb-12">
          <h1 className="font-serif text-[clamp(3.25rem,5vw,5.8rem)] font-bold leading-none tracking-normal text-syncus-blue">
            My Applications
          </h1>
          <p className="mt-5 text-[clamp(1.1rem,1.4vw,1.45rem)] font-medium text-syncus-blue/55">
            Track the progress of all your submitted applications
          </p>
        </header>

        <div className="mb-12 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          {stats.map(({ label, value, color }) => (
            <article
              key={label}
              className="min-h-[135px] rounded-[22px] border-[3px] border-syncus-blue/15 bg-syncus-cream px-8 py-8"
            >
              <p className="text-lg font-bold text-syncus-blue/55">{label}</p>
              <p className="mt-4 text-5xl font-bold leading-none" style={{ color }}>
                {value}
              </p>
            </article>
          ))}
        </div>

        <div className="mb-10 flex flex-wrap gap-3">
          {filterTabs.map((tab) => {
            const isActive = activeTab === tab;

            return (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className="flex min-h-[58px] items-center gap-3 rounded-[20px] border-[3px] px-7 text-xl font-bold transition hover:-translate-y-0.5"
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
                    className="grid h-8 min-w-8 place-items-center rounded-full px-2 text-base font-bold"
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

        <div className="grid gap-6">
          {filtered.length === 0 ? (
            <section className="rounded-[22px] border-[3px] border-dashed border-syncus-blue/15 py-16 text-center">
              <p className="text-xl font-bold text-syncus-blue/55">No {activeTab.toLowerCase()} applications</p>
            </section>
          ) : (
            filtered.map((application) => {
              const { color, bg, icon: StatusIcon } = statusConfig[application.status];

              return (
                <button
                  key={application.id}
                  className="grid min-h-[118px] grid-cols-[auto_1fr] items-center gap-6 rounded-[22px] border-[3px] border-syncus-blue/15 bg-syncus-cream px-7 py-6 text-left transition hover:-translate-y-0.5 hover:shadow-card lg:grid-cols-[auto_1fr_auto_auto_auto_auto]"
                  onClick={() => navigate(`/jobs/${application.jobId}`)}
                  type="button"
                >
                  <span
                    className="grid h-16 w-16 place-items-center rounded-[18px]"
                    style={{ backgroundColor: bg, color }}
                  >
                    <StatusIcon size={26} />
                  </span>

                  <span className="min-w-0">
                    <span className="block truncate text-2xl font-bold text-syncus-blue">
                      {application.title}
                    </span>
                    <span className="mt-2 block truncate text-xl font-medium text-syncus-blue/55">
                      {application.company} · {application.location}
                    </span>
                  </span>

                  <span className="col-start-2 row-start-2 text-center lg:col-auto lg:row-auto">
                    <span
                      className="block text-3xl font-bold leading-none"
                      style={{ color: application.matchScore >= 90 ? "#00804d" : "#1e4890" }}
                    >
                      {application.matchScore}%
                    </span>
                    <span className="mt-2 block text-lg font-medium text-syncus-blue/55">Match</span>
                  </span>

                  <span
                    className="col-start-2 row-start-3 w-fit rounded-full px-6 py-2 text-lg font-bold lg:col-auto lg:row-auto"
                    style={{ backgroundColor: bg, color }}
                  >
                    {statusConfig[application.status].label}
                  </span>

                  <span className="col-start-2 row-start-4 text-lg font-medium text-syncus-blue/55 lg:col-auto lg:row-auto">
                    {application.appliedDate}
                  </span>

                  <ChevronRight className="hidden text-syncus-blue lg:block" size={28} />
                </button>
              );
            })
          )}
        </div>
      </section>
    </main>
  );
}
