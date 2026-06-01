import { useCallback, useEffect, useState } from "react";
import {
  AlertCircle,
  CalendarDays,
  CheckCircle,
  ChevronRight,
  Clock,
  Eye,
  Trash2,
  XCircle,
} from "lucide-react";
import { useNavigate } from "react-router";
import { getJob, listApplications, updateApplicationStatus } from "../lib/api";
import { toFrontendApplication, toFrontendJob, type Application } from "../lib/jobs";

const statusConfig: Record<
  Application["status"],
  { label: string; color: string; bg: string; icon: typeof CheckCircle }
> = {
  Applied: { label: "Applied", color: "#1e4890", bg: "rgba(30,72,144,0.12)", icon: Clock },
  Shortlisted: { label: "Shortlisted", color: "#ca8a04", bg: "rgba(202,138,4,0.12)", icon: CheckCircle },
  Interviewing: { label: "Interviewing", color: "#7c3aed", bg: "rgba(124,58,237,0.12)", icon: CalendarDays },
  Offered: { label: "Offered", color: "#00804d", bg: "rgba(0,128,77,0.12)", icon: Eye },
  Rejected: { label: "Not Progressed", color: "#dc2626", bg: "rgba(220,38,38,0.12)", icon: XCircle },
  Withdrawn: { label: "Withdrawn", color: "#6b7280", bg: "rgba(107,114,128,0.12)", icon: AlertCircle },
};

const filterTabs = ["All", "Applied", "Shortlisted", "Interviewing", "Offered", "Rejected", "Withdrawn"] as const;
type FilterTab = (typeof filterTabs)[number];

export function ApplicationsPage() {
  const navigate = useNavigate();
  const [apps, setApps] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<FilterTab>("All");
  const [withdrawingId, setWithdrawingId] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [withdrawing, setWithdrawing] = useState(false);

  const loadApplications = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const { items } = await listApplications();
      const uniqueJobIds = [...new Set(items.map((item) => item.job_id))];
      const jobResults = await Promise.allSettled(uniqueJobIds.map((jobId) => getJob(jobId)));
      const jobsById = new Map(
        uniqueJobIds.map((jobId, index) => {
          const result = jobResults[index];
          if (result.status === "fulfilled") {
            return [jobId, toFrontendJob(result.value)] as const;
          }
          return [jobId, undefined] as const;
        })
      );

      setApps(items.map((item) => toFrontendApplication(item, jobsById.get(item.job_id))));
    } catch (err) {
      setApps([]);
      setError(err instanceof Error ? err.message : "Could not load applications.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadApplications();
  }, [loadApplications]);

  const filtered =
    activeTab === "All" ? apps : apps.filter((application) => application.status === activeTab);

  const handleWithdraw = async (id: string) => {
    setWithdrawing(true);
    setError(null);
    try {
      await updateApplicationStatus(id, "withdrawn");
      setApps((prev) =>
        prev.map((application) =>
          application.id === id ? { ...application, status: "Withdrawn" } : application
        )
      );
      setWithdrawingId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not withdraw application.");
    } finally {
      setWithdrawing(false);
    }
  };

  const counts = Object.fromEntries(
    filterTabs.map((tab) => [
      tab,
      tab === "All" ? apps.length : apps.filter((application) => application.status === tab).length,
    ])
  ) as Record<FilterTab, number>;

  const avgMatch =
    apps.length > 0 ? Math.round(apps.reduce((score, application) => score + application.matchScore, 0) / apps.length) : 0;

  const stats = [
    { label: "Total Applied", value: apps.length, color: "#1e4890" },
    {
      label: "In Progress",
      value: apps.filter((application) =>
        ["Applied", "Shortlisted", "Interviewing", "Offered"].includes(application.status)
      ).length,
      color: "#00804d",
    },
    {
      label: "Interviews",
      value: apps.filter((application) => application.status === "Interviewing").length,
      color: "#7c3aed",
    },
    { label: "Avg. Match Score", value: apps.length ? `${avgMatch}%` : "—", color: "#ca8a04" },
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
        {error && <p className="mt-3 text-sm font-bold text-red-600">{error}</p>}
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
              {loading ? "—" : value}
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
            {!loading && counts[tab] > 0 && (
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
        {loading && (
          <p className="py-16 text-center text-sm font-bold text-syncus-blue/55">Loading applications...</p>
        )}

        {!loading && filtered.length === 0 ? (
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
                onClick={() => void handleWithdraw(withdrawingId)}
                className="flex-1 rounded-2xl py-3 text-sm font-bold disabled:opacity-60"
                disabled={withdrawing}
                style={{ backgroundColor: "#dc2626", color: "#f6f8ed", fontFamily: "'DM Sans', sans-serif" }}
                type="button"
              >
                {withdrawing ? "Withdrawing..." : "Yes, Withdraw"}
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
  );
}
