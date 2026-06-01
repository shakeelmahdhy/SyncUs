import { FormEvent, useEffect, useMemo, useState } from "react";
import { BriefcaseBusiness, CheckCircle2, Eye, EyeOff, LogIn, UserRound } from "lucide-react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router";
import {
  clearAccessToken,
  getAccountProfile,
  getEmployerJobStats,
  loginAccount,
  storeAccessToken,
  storeAccountType,
  type AccountType,
} from "../lib/api";

const accountOptions: Array<{
  value: AccountType;
  label: string;
  description: string;
  icon: typeof UserRound;
}> = [
  {
    value: "job_seeker",
    label: "Job seeker",
    description: "Apply and track roles",
    icon: UserRound,
  },
  {
    value: "employer",
    label: "Employer",
    description: "Post jobs and hire",
    icon: BriefcaseBusiness,
  },
];

const copyByAccountType: Record<
  AccountType,
  { eyebrow: string; title: string; body: string; bullets: string[] }
> = {
  job_seeker: {
    eyebrow: "Welcome back",
    title: "Sign in to apply and track your applications.",
    body: "Use your job seeker credentials to access your profile, recommendations, and applications.",
    bullets: [
    
      "Profile and resume access",
      "Intelligienly match with jobs",
    ],
  },
  employer: {
    eyebrow: "Welcome back",
    title: "Sign in to your recruiter workspace.",
    body: "Manage job postings, review applications, and use candidate matching from one place.",
    bullets: [
   
      "Post and publish job roles",
      "Intelligienly match with candidates",
    ],
  },
};

function accountTypeFromSearch(searchParams: URLSearchParams): AccountType {
  const type = searchParams.get("type");
  return type === "employer" ? "employer" : "job_seeker";
}

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const [accountType, setAccountType] = useState<AccountType>(() => accountTypeFromSearch(searchParams));

  const redirectFromState = (location.state as { from?: string } | null)?.from;
  const jobSeekerRedirect = redirectFromState ?? "/profile";
  const employerRedirect =
    redirectFromState?.startsWith("/employer") ? redirectFromState : "/employer/dashboard";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const copy = useMemo(() => copyByAccountType[accountType], [accountType]);

  useEffect(() => {
    setAccountType(accountTypeFromSearch(searchParams));
  }, [searchParams]);

  const selectAccountType = (value: AccountType) => {
    setAccountType(value);
    setError(null);
    const next = new URLSearchParams(searchParams);
    if (value === "employer") {
      next.set("type", "employer");
    } else {
      next.delete("type");
    }
    setSearchParams(next, { replace: true });
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const response = await loginAccount({ email: email.trim(), password });

      if (accountType === "employer") {
        if (response.user.account_type !== "employer") {
          setError("This account is not registered as an employer. Switch to job seeker or create an employer account.");
          return;
        }

        storeAccessToken(response.access_token);
        storeAccountType("employer");

        try {
          await getEmployerJobStats();
        } catch (statsError) {
          const message = statsError instanceof Error ? statsError.message : "";
          if (message.includes("Cannot reach the SyncUs API")) {
            setError(message);
            return;
          }
          clearAccessToken();
          setError("This account is not registered as an employer.");
          return;
        }

        navigate(employerRedirect, { replace: true });
        return;
      }

      if (response.user.account_type === "employer") {
        setError("This is an employer account. Switch to Employer above or sign in from the recruiter workspace.");
        return;
      }

      storeAccessToken(response.access_token);
      storeAccountType("job_seeker");

      try {
        await getAccountProfile();
      } catch {
        clearAccessToken();
        setError("This account is not set up as a job seeker. Switch to Employer or register again.");
        return;
      }

      navigate(jobSeekerRedirect, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign in failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="bg-syncus-cream px-5 py-10 text-syncus-blue sm:px-8 lg:py-14">
      <section className="mx-auto grid max-w-[1120px] gap-8 lg:grid-cols-[0.88fr_1.12fr] lg:items-start">
        <div className="pt-2">
          <p className="text-sm font-bold uppercase text-syncus-green">{copy.eyebrow}</p>
          <h1 className="mt-4 max-w-[620px] font-serif text-[clamp(2.45rem,5vw,4.8rem)] leading-none tracking-normal text-syncus-blue">
            {copy.title}
          </h1>
          <p className="mt-5 max-w-[520px] text-base font-medium leading-7 text-syncus-blue/65">{copy.body}</p>

          <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
            {copy.bullets.map((item) => (
              <div
                key={item}
                className="flex min-h-12 items-center gap-3 rounded-lg border-2 border-syncus-green/25 px-4 text-sm font-bold text-syncus-green"
              >
                <CheckCircle2 size={18} />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>

        <form className="rounded-2xl border-2 border-syncus-green bg-syncus-cream p-5 shadow-syncus sm:p-7" onSubmit={handleSubmit}>
          <div className="grid gap-3 sm:grid-cols-2">
            {accountOptions.map((option) => {
              const Icon = option.icon;
              const isSelected = accountType === option.value;

              return (
                <button
                  key={option.value}
                  className={`flex min-h-20 items-center gap-3 rounded-xl border-2 px-4 text-left transition hover:-translate-y-0.5 ${
                    isSelected
                      ? "border-syncus-blue bg-syncus-blue text-syncus-cream"
                      : "border-syncus-green/30 text-syncus-blue hover:border-syncus-green"
                  }`}
                  type="button"
                  onClick={() => selectAccountType(option.value)}
                >
                  <span
                    className={`grid h-10 w-10 shrink-0 place-items-center rounded-lg ${
                      isSelected ? "bg-syncus-lime text-syncus-blue" : "bg-syncus-green/10 text-syncus-green"
                    }`}
                  >
                    <Icon size={19} />
                  </span>
                  <span>
                    <span className="block text-sm font-bold">{option.label}</span>
                    <span
                      className={`mt-1 block text-xs font-medium ${
                        isSelected ? "text-syncus-cream/75" : "text-syncus-blue/55"
                      }`}
                    >
                      {option.description}
                    </span>
                  </span>
                </button>
              );
            })}
          </div>

          <div className="mt-6 grid gap-4">
            <label>
              <span className="mb-1.5 block text-xs font-bold text-syncus-blue/55">Email Address</span>
              <input
                className="min-h-11 w-full rounded-xl border-2 border-syncus-blue/20 bg-syncus-cream px-4 text-sm text-syncus-blue outline-none transition focus:border-syncus-green"
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

          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <button
              className="inline-flex min-h-12 items-center justify-center gap-2 rounded-xl bg-syncus-green px-7 text-sm font-bold text-syncus-cream transition hover:-translate-y-0.5 hover:bg-syncus-blue disabled:cursor-not-allowed disabled:opacity-60"
              disabled={submitting}
              type="submit"
            >
              {submitting ? "Signing in..." : "Sign in"}
              <LogIn size={16} />
            </button>
            <Link
              className="text-sm font-bold text-syncus-blue underline decoration-syncus-green underline-offset-4 transition hover:text-syncus-green"
              to="/register"
            >
              Create account
            </Link>
          </div>
        </form>
      </section>
    </main>
  );
}
