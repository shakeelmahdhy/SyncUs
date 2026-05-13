import { Send } from "lucide-react";
import { SyncUsMark } from "./SyncUsMark";

export function SiteFooter() {
  return (
    <footer className="bg-syncus-blue text-syncus-cream">
      <div className="mx-auto grid max-w-[1280px] gap-10 px-8 py-16 md:grid-cols-[1.2fr_1fr_1fr_1.25fr]">
        <div>
          <SyncUsMark />
          <p className="mt-5 max-w-[250px] text-sm leading-relaxed text-white/78">
            Syncing candidates and employers to find the perfect combination.
          </p>
        </div>
        <div>
          <h3 className="text-xl font-bold">Platform</h3>
          <ul className="mt-4 grid gap-3 text-sm text-white/78">
            <li>Job Search</li>
            <li>AI Matchmaker</li>
            <li>For Employers</li>
            <li>Talent Pool</li>
          </ul>
        </div>
        <div>
          <h3 className="text-xl font-bold">Resources</h3>
          <ul className="mt-4 grid gap-3 text-sm text-white/78">
            <li>Career Design</li>
            <li>Recruiter Tips</li>
            <li>Success Stories</li>
            <li>Contact Support</li>
          </ul>
        </div>
        <div>
          <h3 className="text-xl font-bold">Newsletter</h3>
          <p className="mt-4 text-sm leading-relaxed text-white/78">
            Get the latest jobs and matching insights.
          </p>
          <form className="mt-5 flex gap-2" onSubmit={(event) => event.preventDefault()}>
            <input
              className="min-h-11 min-w-0 flex-1 rounded-xl bg-syncus-cream px-4 text-sm text-syncus-blue outline-none"
              placeholder="Email address"
              type="email"
            />
            <button
              className="grid h-11 w-11 place-items-center rounded-xl border border-syncus-cream text-syncus-cream transition hover:bg-syncus-green"
              type="submit"
              aria-label="Subscribe"
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      </div>
      <div className="mx-auto flex max-w-[1280px] flex-col gap-4 border-t border-white/25 px-8 py-6 text-xs text-white/75 md:flex-row md:items-center md:justify-between">
        <span>© SyncUs AI</span>
        <div className="flex flex-wrap gap-6">
          <span>Privacy Policy</span>
          <span>Terms of Service</span>
          <span>Cookie Policy</span>
          <span>Accessibility</span>
        </div>
      </div>
    </footer>
  );
}
