import type { ReactNode } from "react";
import { BarChart3, BriefcaseBusiness, ClipboardList, LayoutDashboard, Search } from "lucide-react";
import { NavLink, useNavigate } from "react-router";
import { clearAccessToken, getStoredAccessToken } from "../../lib/api";
import { SyncUsMark } from "../../shared/components";

function getDisplayNameFromToken() {
  const token = getStoredAccessToken();
  if (!token) return { initials: "SU", label: "Employer" };

  try {
    const [, payload] = token.split(".");
    const normalizedPayload = payload.replace(/-/g, "+").replace(/_/g, "/");
    const paddedPayload = normalizedPayload.padEnd(
      normalizedPayload.length + ((4 - (normalizedPayload.length % 4)) % 4),
      "="
    );
    const decoded = JSON.parse(window.atob(paddedPayload)) as { email?: string };
    const email = decoded.email ?? "Employer";
    const initials = email
      .split("@")[0]
      .split(/[._-]+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part.charAt(0).toUpperCase())
      .join("");
    return { initials: initials || "SU", label: email };
  } catch {
    return { initials: "SU", label: "Employer" };
  }
}

const employerLinks = [
  { label: "Dashboard", to: "/employer/dashboard", icon: LayoutDashboard },
  { label: "Post Job", to: "/employer/post-job", icon: BriefcaseBusiness },
  { label: "Applications", to: "/employer/review-applications", icon: ClipboardList },
];

export function EmployerShell({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const employerIdentity = getDisplayNameFromToken();

  return (
    <main className="bg-syncus-cream text-syncus-blue">
      <div className="mx-auto grid min-h-screen max-w-[1380px] lg:grid-cols-[244px_minmax(0,1fr)]">
        <aside className="bg-syncus-blue px-5 py-6 text-syncus-cream lg:min-h-screen">
          <div className="mb-10">
            <SyncUsMark />
            <p className="mt-1 text-[0.62rem] font-bold uppercase tracking-[0.16em] text-white/58">
              Recruiter dashboard
            </p>
          </div>

          <nav className="grid gap-2">
            {employerLinks.map(({ label, to, icon: Icon }) => (
              <NavLink
                key={to}
                className={({ isActive }) =>
                  `flex min-h-11 items-center gap-3 rounded-lg px-4 text-sm font-bold transition ${
                    isActive ? "bg-white/14 text-syncus-cream" : "text-white/72 hover:bg-white/10 hover:text-syncus-cream"
                  }`
                }
                to={to}
              >
                <Icon size={17} />
                {label}
              </NavLink>
            ))}
          </nav>

          <div className="my-8 h-px bg-white/30" />

          <div className="grid gap-3 text-sm font-bold text-white/72">
            <span className="flex items-center gap-3 px-4">
              <BarChart3 size={16} />
              Matching Insights
            </span>
          </div>
        </aside>

        <section className="min-w-0">
          <header className="flex min-h-[86px] flex-col gap-4 bg-syncus-blue px-5 py-4 text-syncus-cream sm:flex-row sm:items-center sm:justify-between lg:px-8">
            <label className="flex min-h-12 w-full max-w-[410px] items-center gap-3 rounded-lg bg-white/15 px-4 text-white">
              <Search size={18} />
              <input
                className="min-w-0 flex-1 bg-transparent text-sm font-bold outline-none placeholder:text-white/66"
                placeholder="Search candidates or jobs..."
              />
            </label>

            <div className="flex items-center gap-4">
              <button
                className="min-h-12 rounded-lg bg-syncus-lime px-5 text-sm font-black uppercase text-syncus-blue transition hover:-translate-y-0.5 hover:shadow-card"
                onClick={() => navigate("/employer/post-job")}
                type="button"
              >
                + Post a New Job
              </button>
              <button
                className="min-h-12 rounded-lg border border-white/30 px-4 text-sm font-bold text-syncus-cream transition hover:bg-white/10"
                onClick={() => {
                  clearAccessToken();
                  navigate("/employer/login");
                }}
                type="button"
              >
                Sign out
              </button>
              <div className="hidden items-center gap-3 sm:flex">
                <span className="grid h-11 w-11 place-items-center rounded-full bg-syncus-cream text-syncus-blue">
                  {employerIdentity.initials}
                </span>
                <span>
                  <span className="block max-w-[220px] truncate font-serif text-xl leading-none">
                    {employerIdentity.label}
                  </span>
                  <span className="block text-[0.66rem] font-bold uppercase tracking-[0.12em] text-white/72">
                    Employer account
                  </span>
                </span>
              </div>
            </div>
          </header>

          <div className="px-5 py-8 sm:px-7 lg:px-12 lg:py-10">{children}</div>
        </section>
      </div>
    </main>
  );
}
