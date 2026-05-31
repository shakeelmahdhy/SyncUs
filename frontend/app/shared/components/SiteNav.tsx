import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import { clearAccessToken, getAccountProfile, hasStoredAccessToken } from "../../lib/api";
import { SyncUsMark } from "./SyncUsMark";

export function SiteNav() {
  const navigate = useNavigate();
  const [signedIn, setSignedIn] = useState(hasStoredAccessToken());
  const [displayName, setDisplayName] = useState<string | null>(null);

  useEffect(() => {
    if (!hasStoredAccessToken()) {
      setSignedIn(false);
      setDisplayName(null);
      return;
    }

    let isMounted = true;

    getAccountProfile()
      .then((profile) => {
        if (!isMounted) return;
        setSignedIn(true);
        setDisplayName(`${profile.first_name} ${profile.last_name}`.trim() || profile.email || null);
      })
      .catch(() => {
        if (!isMounted) return;
        setSignedIn(hasStoredAccessToken());
        setDisplayName(null);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const handleSignOut = () => {
    clearAccessToken();
    setSignedIn(false);
    setDisplayName(null);
    navigate("/");
  };

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
            <Link className="transition hover:text-syncus-lime" to="/recommendations">
              Recommendations
            </Link>
            <Link className="transition hover:text-syncus-lime" to="/profile">
              Profile
            </Link>
            <Link className="transition hover:text-syncus-lime" to="/employer/login">
              For Employers
            </Link>
          </nav>
        </div>
        <div className="flex items-center gap-3">
          {signedIn ? (
            <>
              {displayName && (
                <span className="hidden text-sm font-medium text-white/80 sm:inline">{displayName}</span>
              )}
              <button
                className="rounded-lg border border-white/30 px-4 py-2 text-sm font-bold transition hover:bg-white/10"
                onClick={handleSignOut}
                type="button"
              >
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link
                className="rounded-lg border border-white/30 px-4 py-2 text-sm font-bold transition hover:bg-white/10"
                to="/login"
              >
                Sign in
              </Link>
              <Link
                className="rounded-lg bg-syncus-lime px-5 py-2 text-sm font-bold text-syncus-blue transition hover:-translate-y-0.5 hover:shadow-card"
                to="/register"
              >
                Create Account
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
