import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Briefcase, CheckCircle2, MapPin, Search, SlidersHorizontal, Sparkles } from "lucide-react";
import { useNavigate } from "react-router";
import { fetchRecommendedRoles, type RecommendedRole } from "../lib/jobs";

const scoreBands = ["All", "90+", "80+", "70+"] as const;
type ScoreBand = (typeof scoreBands)[number];

function bandMatches(job: RecommendedRole, band: ScoreBand) {
  if (band === "All") return true;
  return job.matchScore >= Number(band.replace("+", ""));
}

export function RecommendationsPage() {
  const navigate = useNavigate();
  const [roles, setRoles] = useState<RecommendedRole[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [scoreBand, setScoreBand] = useState<ScoreBand>("All");
  const [savedIds, setSavedIds] = useState<string[]>([]);

  useEffect(() => {
    let isMounted = true;

    fetchRecommendedRoles()
      .then((items) => {
        if (!isMounted) return;
        setRoles(items);
        setSavedIds((current) => current.filter((jobId) => items.some((item) => item.jobId === jobId)));
        setError(null);
      })
      .catch((err) => {
        if (!isMounted) return;
        setRoles([]);
        setError(err instanceof Error ? err.message : "Could not load recommendations.");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const recommendedJobs = useMemo(() => {
    const normalisedQuery = query.trim().toLowerCase();

    return roles
      .filter((job) => job.matchScore >= 70)
      .filter((job) => {
        const matchesQuery =
          !normalisedQuery ||
          [job.title, job.company, job.location, job.category, ...job.skills]
            .join(" ")
            .toLowerCase()
            .includes(normalisedQuery);

        return matchesQuery && bandMatches(job, scoreBand);
      })
      .sort((left, right) => right.matchScore - left.matchScore);
  }, [query, roles, scoreBand]);

  const topScore = recommendedJobs[0]?.matchScore ?? 0;

  return (
    <main className="mx-auto max-w-[1180px] px-5 py-10 text-syncus-blue sm:px-8">
      <header className="mb-8 grid gap-6 lg:grid-cols-[1fr_340px] lg:items-end">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full bg-syncus-lime px-4 py-2 text-xs font-black uppercase tracking-[0.12em] text-syncus-blue">
            <Sparkles size={15} />
            Matched roles
          </span>
          <h1 className="mt-5 font-serif text-[clamp(2.5rem,5vw,4.5rem)] leading-none text-syncus-blue">
            Recommendations
          </h1>
          <p className="mt-4 max-w-2xl text-base font-medium text-syncus-blue/62">
            Roles ranked by skills, work preferences, location fit, and your profile from the matching API.
          </p>
        </div>

        <section className="rounded-2xl border-2 border-syncus-blue/20 bg-syncus-cream p-5 shadow-card">
          <p className="text-sm font-bold text-syncus-blue/60">Best current match</p>
          <p className="mt-2 text-5xl font-black leading-none text-syncus-green">{loading ? "—" : `${topScore}%`}</p>
          <p className="mt-2 text-sm font-medium text-syncus-blue/55">
            {recommendedJobs[0]?.title ?? (loading ? "Loading..." : "No matching roles found")}
          </p>
        </section>
      </header>

      {error && (
        <p className="mb-6 rounded-lg bg-red-50 px-4 py-3 text-sm font-bold text-red-700">{error}</p>
      )}

      <section className="mb-7 grid gap-3 rounded-2xl border-2 border-syncus-green/30 bg-syncus-cream p-4 shadow-card lg:grid-cols-[1fr_auto]">
        <label className="flex min-h-12 items-center gap-3 rounded-xl bg-syncus-green/12 px-4 text-syncus-green">
          <Search size={18} />
          <input
            className="min-w-0 flex-1 bg-transparent text-sm font-bold outline-none placeholder:text-syncus-green/60"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search recommended roles, skills, or companies..."
            type="search"
            value={query}
          />
        </label>

        <div className="flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center gap-2 px-1 text-sm font-bold text-syncus-blue/60">
            <SlidersHorizontal size={16} />
            Match
          </span>
          {scoreBands.map((band) => (
            <button
              className={`min-h-10 rounded-lg border-2 px-4 text-sm font-black transition ${
                scoreBand === band
                  ? "border-syncus-blue bg-syncus-blue text-syncus-cream"
                  : "border-syncus-blue/30 text-syncus-blue hover:border-syncus-blue"
              }`}
              key={band}
              onClick={() => setScoreBand(band)}
              type="button"
            >
              {band}
            </button>
          ))}
        </div>
      </section>

      <section className="grid gap-5">
        {loading && (
          <p className="rounded-2xl border-2 border-dashed border-syncus-green p-12 text-center text-sm font-bold text-syncus-blue/55">
            Loading recommendations...
          </p>
        )}

        {!loading &&
          recommendedJobs.map((job) => {
            const isSaved = savedIds.includes(job.jobId);

            return (
              <article
                className="rounded-2xl border-2 border-syncus-green bg-syncus-cream p-5 shadow-card transition hover:-translate-y-0.5 hover:shadow-syncus"
                key={job.jobId}
              >
                <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
                  <div className="flex gap-4">
                    <span className="grid h-14 w-14 shrink-0 place-items-center rounded-xl bg-syncus-green text-syncus-cream">
                      <Briefcase size={24} />
                    </span>
                    <div>
                      <h2 className="text-2xl font-bold leading-tight text-syncus-green">{job.title}</h2>
                      <p className="mt-1 flex flex-wrap items-center gap-1 text-sm font-bold text-syncus-blue/65">
                        {job.company}
                        <span>·</span>
                        <MapPin size={14} />
                        {job.location}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-2 lg:justify-end">
                    <span className="rounded-full bg-syncus-lime px-4 py-2 text-sm font-black text-syncus-blue">
                      {job.matchScore}% match
                    </span>
                    <button
                      className={`rounded-full border-2 px-4 py-2 text-sm font-black transition ${
                        isSaved
                          ? "border-syncus-green bg-syncus-green text-syncus-cream"
                          : "border-syncus-green text-syncus-green hover:bg-syncus-green hover:text-syncus-cream"
                      }`}
                      onClick={() =>
                        setSavedIds((current) =>
                          current.includes(job.jobId)
                            ? current.filter((id) => id !== job.jobId)
                            : [...current, job.jobId]
                        )
                      }
                      type="button"
                    >
                      {isSaved ? "Saved" : "Save"}
                    </button>
                  </div>
                </div>

                <p className="mt-5 max-w-3xl text-sm leading-relaxed text-syncus-blue/70">{job.description}</p>

                <div className="mt-5 flex flex-col gap-4 border-t border-syncus-green/25 pt-4 lg:flex-row lg:items-center lg:justify-between">
                  <div className="flex flex-wrap gap-2">
                    {[job.workMode, job.salary, job.category, ...job.skills.slice(0, 3)].map((tag) => (
                      <span className="rounded-full bg-syncus-blue/10 px-3 py-1 text-xs font-bold text-syncus-blue" key={tag}>
                        {tag}
                      </span>
                    ))}
                  </div>
                  <button
                    className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-syncus-blue px-6 text-sm font-black text-syncus-cream transition hover:bg-syncus-green"
                    onClick={() => navigate(`/jobs/${job.jobId}`)}
                    type="button"
                  >
                    View role
                    <ArrowRight size={16} />
                  </button>
                </div>
              </article>
            );
          })}

        {!loading && recommendedJobs.length === 0 && (
          <section className="rounded-2xl border-2 border-dashed border-syncus-green p-12 text-center text-syncus-blue">
            <CheckCircle2 className="mx-auto mb-3 text-syncus-green" size={34} />
            <p className="text-xl font-bold">No recommendations match those filters</p>
            <p className="mt-2 text-sm font-medium text-syncus-blue/55">
              Complete your profile or clear filters to see more matched roles.
            </p>
          </section>
        )}
      </section>
    </main>
  );
}
