import type { ReactNode } from "react";
import { SiteFooter, SiteNav } from "../../shared/components";

export function JobSeekerLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-syncus-cream text-syncus-blue">
      <SiteNav />
      {children}
      <SiteFooter />
    </div>
  );
}
