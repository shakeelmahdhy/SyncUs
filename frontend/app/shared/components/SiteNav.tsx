import { Bell, Settings } from "lucide-react";
import { Link } from "react-router";
import { SyncUsMark } from "./SyncUsMark";

export function SiteNav() {
  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-syncus-blue text-syncus-cream shadow-md">
      <div className="mx-auto flex h-[72px] max-w-[1380px] items-center justify-between px-6 lg:px-10">
        <div className="flex items-center gap-10">
          <SyncUsMark compact />
          <nav className="hidden items-center gap-8 text-sm font-medium md:flex">
            <Link className="transition hover:text-syncus-lime" to="/#jobs">
              Jobs
            </Link>
            <Link className="transition hover:text-syncus-lime" to="/#matches">
              Matches
            </Link>
            <Link className="transition hover:text-syncus-lime" to="/applications">
              Applications
            </Link>
            <Link className="transition hover:text-syncus-lime" to="/#messages">
              Messages
            </Link>
            <Link className="transition hover:text-syncus-lime" to="/dashboard">
              Dashboard
            </Link>
            <Link className="transition hover:text-syncus-lime" to="/talent-pool">
              Talent Pool
            </Link>
            <Link className="transition hover:text-syncus-lime" to="/hiring-team">
              Hiring Team
            </Link>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <button className="hidden text-sm font-bold transition hover:text-syncus-lime sm:block" type="button">
            Post a Job
          </button>
          <button
            className="rounded-lg bg-syncus-lime px-5 py-2 text-sm font-bold text-syncus-blue transition hover:-translate-y-0.5 hover:shadow-card"
            type="button"
          >
            Sign In
          </button>
          <span className="hidden h-7 w-px bg-white/30 md:block" />
          <button
            className="hidden rounded-full p-2 transition hover:bg-white/10 md:block"
            aria-label="Notifications"
            type="button"
          >
            <Bell size={18} />
          </button>
          <button
            className="hidden rounded-full p-2 transition hover:bg-white/10 md:block"
            aria-label="Settings"
            type="button"
          >
            <Settings size={18} />
          </button>
        </div>
      </div>
    </header>
  );
}
