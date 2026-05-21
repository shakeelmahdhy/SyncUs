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
            <Link className="transition hover:text-syncus-lime" to="/applications">
              Applications
            </Link>
            <Link className="transition hover:text-syncus-lime" to="/profile">
              Profile
            </Link>
            <Link className="transition hover:text-syncus-lime" to="/employer/dashboard">
              Employer
            </Link>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <Link
            className="hidden rounded-lg border border-syncus-cream/55 px-5 py-2 text-sm font-bold text-syncus-cream transition hover:-translate-y-0.5 hover:border-syncus-lime hover:text-syncus-lime sm:inline-flex"
            to="/employer/post-job"
          >
            Post Job
          </Link>
          <Link
            className="rounded-lg bg-syncus-lime px-5 py-2 text-sm font-bold text-syncus-blue transition hover:-translate-y-0.5 hover:shadow-card"
            to="/register"
          >
            Create Account
          </Link>
        </div>
      </div>
    </header>
  );
}
