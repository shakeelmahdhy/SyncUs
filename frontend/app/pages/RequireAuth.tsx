import { useEffect, useState, type ReactNode } from "react";
import { Navigate, useLocation } from "react-router";
import {
  clearAccessToken,
  getAccountProfile,
  getStoredAccountType,
  hasStoredAccessToken,
  isAuthFailureMessage,
} from "../lib/api";

export function RequireAuth({ children }: { children: ReactNode }) {
  const location = useLocation();
  const [allowed, setAllowed] = useState<boolean | null>(null);

  useEffect(() => {
    if (!hasStoredAccessToken()) {
      setAllowed(false);
      return;
    }

    if (getStoredAccountType() === "employer") {
      setAllowed(false);
      return;
    }

    let isMounted = true;

    getAccountProfile()
      .then(() => {
        if (isMounted) setAllowed(true);
      })
      .catch((error) => {
        const message = error instanceof Error ? error.message : "";
        if (isAuthFailureMessage(message)) {
          clearAccessToken();
        }
        if (isMounted) setAllowed(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  if (allowed === null) {
    return (
      <main className="flex min-h-[50vh] items-center justify-center bg-syncus-cream px-6 text-syncus-blue">
        <p className="text-lg font-medium">Checking your session...</p>
      </main>
    );
  }

  if (!allowed) {
    if (hasStoredAccessToken() && getStoredAccountType() === "employer") {
      return <Navigate replace to="/employer/dashboard" />;
    }
    return <Navigate replace state={{ from: location.pathname }} to="/login" />;
  }

  return <>{children}</>;
}
