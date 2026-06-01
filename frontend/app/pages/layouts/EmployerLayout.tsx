import type { ReactNode } from "react";
import { EmployerShell } from "../employer/EmployerShell";

export function EmployerLayout({ children }: { children: ReactNode }) {
  return <EmployerShell>{children}</EmployerShell>;
}
