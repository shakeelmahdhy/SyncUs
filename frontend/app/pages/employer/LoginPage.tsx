import { FormEvent, useState } from "react";
import { LockKeyhole, LogIn, ShieldCheck } from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router";
import {
  clearAccessToken,
  getEmployerJobStats,
  loginAccount,
  storeAccessToken,
  storeAccountType,
} from "../../lib/api";

export function EmployerLoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = (location.state as { from?: string } | null)?.from ?? "/employer/dashboard";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const response = await loginAccount({ email: email.trim(), password });

      if (response.user.account_type !== "employer") {
        setError("This account is not registered as an employer. Use job seeker login or register as an employer.");
        return;
      }

      storeAccessToken(response.access_token);
      storeAccountType("employer");

      try {
        await getEmployerJobStats();
      } catch {
        clearAccessToken();
        setError("This account is not registered as an employer.");
        return;
      }

      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Employer login failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-syncus-blue text-syncus-cream">
      <section className="mx-auto grid min-h-screen max-w-[1180px] gap-10 px-5 py-10 md:grid-cols-[0.9fr_1.1fr] md:items-center lg:px-8">
        <div>
          <p className="text-sm font-black uppercase tracking-[0.18em] text-syncus-lime">Employer access</p>
          <h1 className="mt-5 max-w-[560px] font-serif text-[clamp(3rem,6vw,6rem)] leading-none tracking-normal">
            Recruiter workspace
          </h1>
          <p className="mt-6 max-w-[470px] text-base font-medium leading-7 text-white/72">
            Sign in with an employer account before creating jobs, reviewing applications, or using candidate matching.
          </p>
          <div className="mt-8 grid gap-3 text-sm font-bold text-white/76">
            <span className="flex items-center gap-3">
              <ShieldCheck className="text-syncus-lime" size={19} />
              Uses Supabase Auth access tokens
            </span>
            <span className="flex items-center gap-3">
              <LockKeyhole className="text-syncus-lime" size={19} />
              Verifies employer access before posting jobs
            </span>
          </div>
        </div>

        <form
          className="rounded-[18px] border border-white/25 bg-syncus-cream p-6 text-syncus-blue shadow-card sm:p-8"
          onSubmit={handleSubmit}
        >
          <h2 className="font-serif text-4xl leading-none">Employer Login</h2>
          <p className="mt-3 text-sm font-medium text-syncus-blue/60">
            Use the email and password for your employer account.
          </p>

          <div className="mt-7 grid gap-4">
            <label>
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">
                Email address
              </span>
              <input
                className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 font-bold outline-none focus:border-syncus-green"
                required
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </label>
            <label>
              <span className="mb-2 block text-xs font-black uppercase tracking-[0.08em] text-syncus-blue/55">
                Password
              </span>
              <input
                className="min-h-12 w-full rounded-lg border-2 border-syncus-blue/25 bg-syncus-cream px-4 font-bold outline-none focus:border-syncus-green"
                required
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
          </div>

          {error && <p className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm font-black text-red-700">{error}</p>}

          <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <button
              className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-syncus-blue px-7 text-sm font-black text-syncus-cream transition hover:-translate-y-0.5 disabled:opacity-60"
              disabled={submitting}
              type="submit"
            >
              {submitting ? "Signing in..." : "Log in"}
              <LogIn size={16} />
            </button>
            <Link className="text-sm font-black text-syncus-blue underline decoration-syncus-green underline-offset-4" to="/register">
              Create employer account
            </Link>
          </div>
        </form>
      </section>
    </main>
  );
}
