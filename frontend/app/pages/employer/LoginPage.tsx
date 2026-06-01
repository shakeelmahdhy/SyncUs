import { Navigate, useLocation } from "react-router";

/** Legacy route: unified sign-in lives at `/login?type=employer`. */
export function EmployerLoginPage() {
  const location = useLocation();
  return (
    <Navigate
      replace
      to={{ pathname: "/login", search: "?type=employer" }}
      state={location.state}
    />
  );
}
