import { ReactNode, useEffect, useState } from "react";
import { Navigate, useLocation } from "react-router";
import { clearAccessToken, getEmployerJobStats, hasStoredAccessToken, isAuthFailureMessage } from "../../lib/api";

export function RequireEmployer({ children }: { children: ReactNode }) {
  const location = useLocation();
  const [allowed, setAllowed] = useState<boolean | null>(() => (hasStoredAccessToken() ? null : false));

  useEffect(() => {
    if (!hasStoredAccessToken()) {
      setAllowed(false);
      return;
    }

    let isMounted = true;
    getEmployerJobStats()
      .then(() => {
        if (isMounted) setAllowed(true);
      })
      .catch((error) => {
        const message = error instanceof Error ? error.message : "";
        if (message.includes("Cannot reach the SyncUs API")) {
          if (isMounted) setAllowed(true);
          return;
        }
        if (!isAuthFailureMessage(message) && isMounted) {
          setAllowed(false);
          return;
        }
        clearAccessToken();
        if (isMounted) setAllowed(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  if (allowed === null) {
    return (
      <main className="grid min-h-screen place-items-center bg-syncus-blue px-5 text-syncus-cream">
        <p className="text-sm font-black uppercase tracking-[0.16em] text-syncus-lime">Checking employer session...</p>
      </main>
    );
  }

  if (!allowed) {
    return (
      <Navigate
        replace
        state={{ from: location.pathname }}
        to={{ pathname: "/login", search: "?type=employer" }}
      />
    );
  }

  return children;
}
