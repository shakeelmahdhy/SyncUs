import { FormEvent, useMemo, useState } from "react";
import { BriefcaseBusiness, CheckCircle2, Eye, EyeOff, UserRound } from "lucide-react";
import { Link, useNavigate } from "react-router";
import {
  registerAccount,
  storeAccessToken,
  storeAccountType,
  type AccountType,
  type RegisterAccountPayload,
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
    description: "Get matched with roles",
    icon: UserRound,
  },
  {
    value: "employer",
    label: "Employer",
    description: "Find aligned candidates",
    icon: BriefcaseBusiness,
  },
];

const initialForm = {
  firstName: "",
  lastName: "",
  companyName: "",
  email: "",
  password: "",
  confirmPassword: "",
};

export function RegistrationPage() {
  const navigate = useNavigate();
  const [accountType, setAccountType] = useState<AccountType>("job_seeker");
  const [form, setForm] = useState(initialForm);
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const passwordReady = useMemo(() => {
    return form.password.length >= 8 && form.password === form.confirmPassword;
  }, [form.confirmPassword, form.password]);

  const updateField = (key: keyof typeof initialForm, value: string) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    if (!passwordReady) {
      setError("Use at least 8 characters and make sure both passwords match.");
      return;
    }

    if (accountType === "employer" && !form.companyName.trim()) {
      setError("Company name is required for employer accounts.");
      return;
    }

    const payload: RegisterAccountPayload = {
      first_name: form.firstName.trim(),
      last_name: form.lastName.trim(),
      email: form.email.trim(),
      password: form.password,
      account_type: accountType,
      company_name: form.companyName.trim() || undefined,
    };

    setSubmitting(true);
    try {
      const response = await registerAccount(payload);
      if (response.access_token) {
        storeAccessToken(response.access_token);
        storeAccountType(accountType);
        navigate(accountType === "job_seeker" ? "/profile" : "/employer/dashboard");
        return;
      }

      setSuccess("Account created. Check your email to confirm your Supabase session.");
      setForm(initialForm);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="bg-syncus-cream px-5 py-10 text-syncus-blue sm:px-8 lg:py-14">
      <section className="mx-auto grid max-w-[1120px] gap-8 lg:grid-cols-[0.88fr_1.12fr] lg:items-start">
        <div className="pt-2">
          <p className="text-sm font-bold uppercase text-syncus-green">Create your SyncUs account</p>
          <h1 className="mt-4 max-w-[620px] font-serif text-[clamp(2.45rem,5vw,4.8rem)] leading-none tracking-normal text-syncus-blue">
            Start matching with the right opportunities.
          </h1>
          <p className="mt-5 max-w-[520px] text-base font-medium leading-7 text-syncus-blue/65">
            Build a profile that connects directly to job matching, applications, and employer workflows.
          </p>

          <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
            {[
              "Supabase Auth account",
              "JWT-ready profile ownership",
              "Matching uses jobs and profile data",
            ].map((item) => (
              <div key={item} className="flex min-h-12 items-center gap-3 rounded-lg border-2 border-syncus-green/25 px-4 text-sm font-bold text-syncus-green">
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
                  onClick={() => setAccountType(option.value)}
                >
                  <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-lg ${isSelected ? "bg-syncus-lime text-syncus-blue" : "bg-syncus-green/10 text-syncus-green"}`}>
                    <Icon size={19} />
                  </span>
                  <span>
                    <span className="block text-sm font-bold">{option.label}</span>
                    <span className={`mt-1 block text-xs font-medium ${isSelected ? "text-syncus-cream/75" : "text-syncus-blue/55"}`}>
                      {option.description}
                    </span>
                  </span>
                </button>
              );
            })}
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <label>
              <span className="mb-1.5 block text-xs font-bold text-syncus-blue/55">First Name</span>
              <input
                className="min-h-11 w-full rounded-xl border-2 border-syncus-blue/20 bg-syncus-cream px-4 text-sm text-syncus-blue outline-none transition focus:border-syncus-green"
                required
                value={form.firstName}
                onChange={(event) => updateField("firstName", event.target.value)}
              />
            </label>
            <label>
              <span className="mb-1.5 block text-xs font-bold text-syncus-blue/55">Last Name</span>
              <input
                className="min-h-11 w-full rounded-xl border-2 border-syncus-blue/20 bg-syncus-cream px-4 text-sm text-syncus-blue outline-none transition focus:border-syncus-green"
                required
                value={form.lastName}
                onChange={(event) => updateField("lastName", event.target.value)}
              />
            </label>
            {accountType === "employer" && (
              <label className="sm:col-span-2">
                <span className="mb-1.5 block text-xs font-bold text-syncus-blue/55">Company Name</span>
                <input
                  className="min-h-11 w-full rounded-xl border-2 border-syncus-blue/20 bg-syncus-cream px-4 text-sm text-syncus-blue outline-none transition focus:border-syncus-green"
                  required
                  value={form.companyName}
                  onChange={(event) => updateField("companyName", event.target.value)}
                />
              </label>
            )}
            <label className="sm:col-span-2">
              <span className="mb-1.5 block text-xs font-bold text-syncus-blue/55">Email Address</span>
              <input
                className="min-h-11 w-full rounded-xl border-2 border-syncus-blue/20 bg-syncus-cream px-4 text-sm text-syncus-blue outline-none transition focus:border-syncus-green"
                required
                type="email"
                value={form.email}
                onChange={(event) => updateField("email", event.target.value)}
              />
            </label>
            <label>
              <span className="mb-1.5 block text-xs font-bold text-syncus-blue/55">Password</span>
              <span className="flex min-h-11 items-center rounded-xl border-2 border-syncus-blue/20 px-4 transition focus-within:border-syncus-green">
                <input
                  className="min-w-0 flex-1 bg-transparent text-sm text-syncus-blue outline-none"
                  required
                  type={showPassword ? "text" : "password"}
                  value={form.password}
                  onChange={(event) => updateField("password", event.target.value)}
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
            <label>
              <span className="mb-1.5 block text-xs font-bold text-syncus-blue/55">Confirm Password</span>
              <input
                className="min-h-11 w-full rounded-xl border-2 border-syncus-blue/20 bg-syncus-cream px-4 text-sm text-syncus-blue outline-none transition focus:border-syncus-green"
                required
                type={showPassword ? "text" : "password"}
                value={form.confirmPassword}
                onChange={(event) => updateField("confirmPassword", event.target.value)}
              />
            </label>
          </div>

          {(error || success) && (
            <p className={`mt-4 rounded-lg px-4 py-3 text-sm font-bold ${error ? "bg-red-50 text-red-700" : "bg-syncus-green/10 text-syncus-green"}`}>
              {error || success}
            </p>
          )}

          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <button
              className="min-h-12 rounded-xl bg-syncus-green px-7 text-sm font-bold text-syncus-cream transition hover:-translate-y-0.5 hover:bg-syncus-blue disabled:cursor-not-allowed disabled:opacity-60"
              disabled={submitting}
              type="submit"
            >
              {submitting ? "Creating account..." : "Create Account"}
            </button>
            <Link className="text-sm font-bold text-syncus-blue underline decoration-syncus-green underline-offset-4 transition hover:text-syncus-green" to="/">
              Browse jobs first
            </Link>
          </div>
        </form>
      </section>
    </main>
  );
}
