import { useMemo, useState } from "react";
import {
  Briefcase,
  CalendarDays,
  Eye,
  Search,
  Shield,
  Trash2,
  UserPlus,
  Users,
} from "lucide-react";
import { teamMembers as initialTeamMembers } from "../../data/mockData";
import type { TeamMember } from "../../data/mockData";

const accessConfig: Record<
  TeamMember["accessLevel"],
  { label: string; color: string; bg: string; icon: typeof Shield }
> = {
  Admin: { label: "Admin", color: "#1e4890", bg: "#e5eceb", icon: Shield },
  Reviewer: { label: "Reviewer", color: "#00804d", bg: "#e1f0df", icon: Eye },
  Interviewer: { label: "Interviewer", color: "#7c3aed", bg: "#eee1f8", icon: CalendarDays },
};

const filterTabs = ["All", "Admin", "Reviewer", "Interviewer"] as const;
type FilterTab = (typeof filterTabs)[number];

const accessLevels: TeamMember["accessLevel"][] = ["Admin", "Reviewer", "Interviewer"];

const CURRENT_USER_ID = 1;

/**
 * Employer hiring-team management: collaborators, access levels, and job assignments.
 */
export function HiringTeamPage() {
  const [members, setMembers] = useState<TeamMember[]>(initialTeamMembers);
  const [activeTab, setActiveTab] = useState<FilterTab>("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<TeamMember["accessLevel"]>("Reviewer");

  const filteredMembers = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    return members.filter((member) => {
      const matchesSearch =
        !query ||
        member.name.toLowerCase().includes(query) ||
        member.email.toLowerCase().includes(query) ||
        member.role.toLowerCase().includes(query) ||
        member.jobsAssigned.some((job) => job.toLowerCase().includes(query));

      const matchesTab = activeTab === "All" || member.accessLevel === activeTab;

      return matchesSearch && matchesTab;
    });
  }, [activeTab, members, searchQuery]);

  const counts = useMemo(
    () =>
      Object.fromEntries(
        filterTabs.map((tab) => [
          tab,
          tab === "All"
            ? members.length
            : members.filter((member) => member.accessLevel === tab).length,
        ])
      ) as Record<FilterTab, number>,
    [members]
  );

  const openPositions = useMemo(
    () => new Set(members.flatMap((member) => member.jobsAssigned)).size,
    [members]
  );

  const activeCollaborators = useMemo(
    () => members.filter((member) => member.jobsAssigned.length > 0).length,
    [members]
  );

  const interviewerCount = useMemo(
    () => members.filter((member) => member.accessLevel === "Interviewer").length,
    [members]
  );

  const stats = [
    { label: "Team Members", value: members.length, color: "#1e4890" },
    { label: "Active Collaborators", value: activeCollaborators, color: "#00804d" },
    { label: "Open Positions", value: openPositions, color: "#7c3aed" },
    { label: "Interviewers", value: interviewerCount, color: "#d39000" },
  ];

  const handleInvite = () => {
    const email = inviteEmail.trim();
    if (!email) return;

    const nameFromEmail = email.split("@")[0]?.replace(/\./g, " ") ?? "New Member";
    const displayName = nameFromEmail
      .split(" ")
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(" ");
    const initials = displayName
      .split(" ")
      .map((part) => part[0])
      .join("")
      .slice(0, 2)
      .toUpperCase();

    setMembers((current) => [
      ...current,
      {
        id: Date.now(),
        name: displayName,
        email,
        role: "Collaborator",
        accessLevel: inviteRole,
        jobsAssigned: [],
        joinedDate: "Pending",
        avatar: initials || "?",
      },
    ]);
    setInviteEmail("");
    setInviteRole("Reviewer");
    setShowInviteModal(false);
  };

  const handleRemove = (member: TeamMember) => {
    if (member.id === CURRENT_USER_ID) return;
    if (!window.confirm(`Remove ${member.name} from the hiring team?`)) return;
    setMembers((current) => current.filter((item) => item.id !== member.id));
  };

  return (
    <main className="bg-syncus-cream px-5 py-8 text-syncus-blue sm:px-8 lg:py-10">
      <section className="mx-auto max-w-[1120px]">
        <header className="mb-7 flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <h1 className="font-serif text-[clamp(2.35rem,4vw,3.8rem)] font-bold leading-none tracking-normal text-syncus-blue">
              Hiring Team
            </h1>
            <p className="mt-3 max-w-xl text-base font-medium text-syncus-blue/55 sm:text-lg">
              Collaborate with your team to review candidates and make hiring decisions
            </p>
          </div>

          <button
            className="flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-xl bg-syncus-lime px-5 text-sm font-bold text-syncus-blue transition hover:-translate-y-0.5 hover:bg-syncus-green hover:text-syncus-cream"
            onClick={() => setShowInviteModal(true)}
            type="button"
          >
            <UserPlus size={16} />
            Add Collaborator
          </button>
        </header>

        <label className="relative mb-7 block">
          <Search className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-syncus-blue/45" size={18} />
          <input
            className="min-h-11 w-full rounded-xl border-2 border-syncus-blue/20 bg-syncus-cream py-2 pl-11 pr-4 text-sm font-medium text-syncus-blue outline-none transition focus:border-syncus-green"
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="Search team members..."
            type="search"
            value={searchQuery}
          />
        </label>

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
            const Icon =
              tab === "All" ? Users : accessConfig[tab as TeamMember["accessLevel"]]?.icon ?? Users;

            return (
              <button
                key={tab}
                className="flex min-h-11 shrink-0 items-center gap-2 rounded-xl border-2 px-4 text-sm font-bold transition hover:-translate-y-0.5 sm:text-base"
                onClick={() => setActiveTab(tab)}
                style={{
                  backgroundColor: isActive ? "#1e4890" : "#f6f8ed",
                  borderColor: "#1e4890",
                  color: isActive ? "#f6f8ed" : "#1e4890",
                }}
                type="button"
              >
                <Icon size={16} />
                {tab === "All" ? "All Members" : tab}
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
          {filteredMembers.length === 0 ? (
            <section className="rounded-2xl border-2 border-dashed border-syncus-blue/15 py-12 text-center">
              <Users className="mx-auto mb-4 text-syncus-blue/25" size={48} />
              <p className="text-lg font-bold text-syncus-blue">No team members found</p>
              <p className="mt-2 text-sm font-medium text-syncus-blue/55">
                {searchQuery
                  ? "Try adjusting your search"
                  : "Get started by inviting your first collaborator"}
              </p>
              {!searchQuery && (
                <button
                  className="mt-6 inline-flex min-h-11 items-center gap-2 rounded-xl bg-syncus-blue px-5 text-sm font-bold text-syncus-cream transition hover:bg-syncus-green"
                  onClick={() => setShowInviteModal(true)}
                  type="button"
                >
                  <UserPlus size={16} />
                  Add Collaborator
                </button>
              )}
            </section>
          ) : (
            filteredMembers.map((member) => {
              const { color, bg, icon: AccessIcon, label } = accessConfig[member.accessLevel];
              const isCurrentUser = member.id === CURRENT_USER_ID;

              return (
                <article
                  key={member.id}
                  className="rounded-2xl border-2 border-syncus-blue/15 bg-syncus-cream p-4 transition hover:-translate-y-0.5 hover:shadow-card sm:p-5"
                >
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div className="flex min-w-0 flex-1 gap-4">
                      <span
                        className="grid h-14 w-14 shrink-0 place-items-center rounded-xl text-lg font-bold"
                        style={{ backgroundColor: isCurrentUser ? "#00804d" : "#1e4890", color: "#f6f8ed" }}
                      >
                        {member.avatar}
                      </span>

                      <div className="min-w-0 flex-1 space-y-3">
                        <div>
                          <p className="text-lg font-bold text-syncus-blue sm:text-xl">{member.name}</p>
                          <p className="text-sm font-medium text-syncus-blue/55">{member.email}</p>
                        </div>

                        <div className="flex flex-wrap items-center gap-4">
                          <div>
                            <p className="text-xs font-bold uppercase tracking-wide text-syncus-blue/45">Role</p>
                            <p className="text-sm font-bold text-syncus-blue">{member.role}</p>
                          </div>
                          <span className="hidden h-8 w-px bg-syncus-blue/15 sm:block" />
                          <div>
                            <p className="text-xs font-bold uppercase tracking-wide text-syncus-blue/45">
                              Access Level
                            </p>
                            <span
                              className="mt-1 inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-bold"
                              style={{ backgroundColor: bg, color }}
                            >
                              <AccessIcon size={14} />
                              {label}
                            </span>
                          </div>
                          <span className="hidden h-8 w-px bg-syncus-blue/15 sm:block" />
                          <div>
                            <p className="text-xs font-bold uppercase tracking-wide text-syncus-blue/45">Joined</p>
                            <p className="text-sm font-medium text-syncus-blue/55">{member.joinedDate}</p>
                          </div>
                        </div>

                        <div>
                          <p className="mb-2 text-xs font-bold uppercase tracking-wide text-syncus-blue/45">
                            Jobs Assigned ({member.jobsAssigned.length})
                          </p>
                          {member.jobsAssigned.length > 0 ? (
                            <div className="flex flex-wrap gap-2">
                              {member.jobsAssigned.map((job) => (
                                <span
                                  key={job}
                                  className="inline-flex items-center gap-1 rounded-full border border-syncus-blue/20 bg-syncus-blue/10 px-3 py-1 text-xs font-bold text-syncus-blue"
                                >
                                  <Briefcase size={12} />
                                  {job}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <p className="text-sm font-medium text-syncus-blue/45">No roles assigned yet</p>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex shrink-0 flex-row gap-2 lg:flex-col">
                      {isCurrentUser ? (
                        <span className="inline-flex w-fit items-center rounded-full bg-syncus-green px-4 py-1.5 text-sm font-bold text-syncus-cream">
                          You
                        </span>
                      ) : (
                        <>
                          <button
                            className="min-h-10 rounded-xl border-2 border-syncus-blue px-4 text-sm font-bold text-syncus-blue transition hover:bg-syncus-blue/5"
                            type="button"
                          >
                            Edit
                          </button>
                          <button
                            className="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl border-2 border-red-300 px-4 text-sm font-bold text-red-600 transition hover:bg-red-50"
                            onClick={() => handleRemove(member)}
                            type="button"
                          >
                            <Trash2 size={14} />
                            Remove
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </article>
              );
            })
          )}
        </div>
      </section>

      {showInviteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-syncus-blue/45 px-5 backdrop-blur-sm">
          <section className="w-full max-w-md rounded-3xl border-2 border-syncus-green bg-syncus-cream p-8 shadow-syncus">
            <h3 className="font-serif text-3xl text-syncus-blue">Invite Team Member</h3>
            <p className="mt-2 text-sm leading-relaxed text-syncus-blue/55">
              Send an invitation to collaborate on hiring decisions
            </p>

            <label className="mt-6 block">
              <span className="mb-1.5 block text-xs font-bold text-syncus-blue/55">Email Address</span>
              <input
                className="min-h-11 w-full rounded-xl border-2 border-syncus-blue/20 bg-syncus-cream px-4 text-sm text-syncus-blue outline-none focus:border-syncus-green"
                onChange={(event) => setInviteEmail(event.target.value)}
                placeholder="email@company.com"
                type="email"
                value={inviteEmail}
              />
            </label>

            <div className="mt-5">
              <span className="mb-2 block text-xs font-bold text-syncus-blue/55">Access Level</span>
              <div className="flex flex-wrap gap-2">
                {accessLevels.map((level) => {
                  const { icon: LevelIcon, bg, color } = accessConfig[level];
                  const isSelected = inviteRole === level;

                  return (
                    <button
                      key={level}
                      className="flex items-center gap-2 rounded-full border-2 px-4 py-2 text-sm font-bold transition"
                      onClick={() => setInviteRole(level)}
                      style={{
                        backgroundColor: isSelected ? bg : "#f6f8ed",
                        borderColor: isSelected ? color : "rgba(30,72,144,0.2)",
                        color: isSelected ? color : "#1e4890",
                      }}
                      type="button"
                    >
                      <LevelIcon size={14} />
                      {level}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="mt-8 grid gap-3 sm:grid-cols-2">
              <button
                className="min-h-12 rounded-2xl bg-syncus-blue px-5 text-sm font-bold text-syncus-cream transition hover:bg-syncus-green"
                onClick={handleInvite}
                type="button"
              >
                Send Invitation
              </button>
              <button
                className="min-h-12 rounded-2xl border-2 border-syncus-blue px-5 text-sm font-bold text-syncus-blue transition hover:bg-syncus-blue/5"
                onClick={() => {
                  setShowInviteModal(false);
                  setInviteEmail("");
                  setInviteRole("Reviewer");
                }}
                type="button"
              >
                Cancel
              </button>
            </div>
          </section>
        </div>
      )}
    </main>
  );
}
