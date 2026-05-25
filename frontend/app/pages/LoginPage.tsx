import { FormEvent, useState } from "react";
import { CheckCircle2, Eye, EyeOff, LogIn, ShieldCheck, UserRound } from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router";
import {
  clearAccessToken,
  getAccountProfile,
  loginAccount,
  storeAccessToken,
  storeAccountType,
} from "../lib/api";

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = (location.state as { from?: string } | null)?.from ?? "/profile";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const response = await loginAccount({ email: email.trim(), password });

      if (response.user.account_type === "employer") {
        storeAccessToken(response.access_token);
        storeAccountType(response.user.account_type);
        navigate("/employer/dashboard", { replace: true });
        return;
      }

      storeAccessToken(response.access_token);
      storeAccountType(response.user.account_type);

      try {
        await getAccountProfile();
      } catch {
        clearAccessToken();
        setError("This account is not set up as a job seeker. Try employer login or register again.");
        return;
      }

      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="bg-syncus-cream px-5 py-10 text-syncus-blue sm:px-8 lg:py-14">
      <section className="mx-auto grid max-w-[1120px] gap-8 lg:grid-cols-[0.88fr_1.12fr] lg:items-start">
        <div className="pt-2">
          <p className="text-sm font-bold uppercase text-syncus-green">Welcome back</p>
          <h1 className="mt-4 max-w-[620px] font-serif text-[clamp(2.45rem,5vw,4.8rem)] leading-none tracking-normal text-syncus-blue">
            Sign in to apply and track your applications.
          </h1>
          <p className="mt-5 max-w-[520px] text-base font-medium leading-7 text-syncus-blue/65">
            Use the email and password from your job seeker account to access your profile and applications.
          </p>

          <div className="mt-8 grid gap-3 text-sm font-bold text-syncus-green">
            {[
              { icon: ShieldCheck, label: "Secure Supabase Auth session" },
              { icon: UserRound, label: "Profile access verified before entry" },
              { icon: CheckCircle2, label: "Applications and saved profile data stay connected" },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <span key={item.label} className="flex min-h-12 items-center gap-3 rounded-lg border-2 border-syncus-green/25 px-4">
                  <Icon size={18} />
                  {item.label}
                </span>
              );
            })}
          </div>
        </div>

        <form className="rounded-2xl border-2 border-syncus-green bg-syncus-cream p-5 shadow-syncus sm:p-7" onSubmit={handleSubmit}>
          <h2 className="font-serif text-4xl leading-none text-syncus-blue">Sign in</h2>
          <p className="mt-3 text-sm font-medium text-syncus-blue/60">Enter your SyncUs account credentials.</p>

          <div className="mt-7 grid gap-4">
            <label>
              <span className="mb-1.5 block text-xs font-bold text-syncus-blue/55">Email Address</span>
              <input
                className="min-h-11 w-full rounded-xl border-2 border-syncus-blue/20 bg-syncus-cream px-4 text-sm text-syncus-blue outline-none transition focus:border-syncus-green"
                autoComplete="email"
                required
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </label>
            <label>
              <span className="mb-1.5 block text-xs font-bold text-syncus-blue/55">Password</span>
              <span className="flex min-h-11 items-center rounded-xl border-2 border-syncus-blue/20 px-4 transition focus-within:border-syncus-green">
                <input
                  className="min-w-0 flex-1 bg-transparent text-sm text-syncus-blue outline-none"
                  autoComplete="current-password"
                  required
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                />
                <button
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  className="grid h-8 w-8 place-items-center rounded-lg text-syncus-blue/65 transition hover:bg-syncus-green/10 hover:text-syncus-green"
                  type="button"
                  onClick={() => setShowPassword((current) => !current)}
                >
                  {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
                </button>
              </span>
            </label>
          </div>

          {error && <p className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm font-bold text-red-700">{error}</p>}

          <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <button
              className="inline-flex min-h-12 items-center justify-center gap-2 rounded-xl bg-syncus-green px-7 text-sm font-bold text-syncus-cream transition hover:-translate-y-0.5 hover:bg-syncus-blue disabled:opacity-60"
              disabled={submitting}
              type="submit"
            >
              {submitting ? "Signing in..." : "Sign in"}
              <LogIn size={16} />
            </button>
            <Link className="text-sm font-bold text-syncus-blue underline decoration-syncus-green underline-offset-4" to="/register">
              Create account
            </Link>
          </div>

          <p className="mt-5 text-sm font-medium text-syncus-blue/55">
            Hiring talent?{" "}
            <Link className="font-bold text-syncus-green underline underline-offset-4" to="/employer/login">
              Employer login
            </Link>
          </p>
        </form>
      </section>
    </main>
  );
}
