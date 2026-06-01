import { useEffect, useMemo, useState } from "react";
import { MapPin, Search, UserRound } from "lucide-react";
import { searchCandidates, type CandidateSearchResult } from "../../lib/api";
import { EmployerShell } from "./EmployerShell";

function matchLabel(score: number) {
  if (score >= 90) return "Recommended";
  if (score >= 80) return "Strong Match";
  return "Good Match";
}

function titleCaseSkill(skill: string) {
  return skill
    .split(/[\s_-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function EmployerTalentPoolPage() {
  const [search, setSearch] = useState("");
  const [selectedSkill, setSelectedSkill] = useState("All");
  const [candidates, setCandidates] = useState<CandidateSearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [shortlisted, setShortlisted] = useState<string[]>([]);

  useEffect(() => {
    let isMounted = true;
    const timer = window.setTimeout(() => {
      setLoading(true);
      setError(null);

      const skills =
        selectedSkill !== "All" ? [selectedSkill.toLowerCase()] : search.trim() ? search.trim().split(/\s+/) : undefined;

      searchCandidates({ skills, page_size: 50 })
        .then((response) => {
          if (!isMounted) return;
          setCandidates(response.results);
          setTotal(response.total);
        })
        .catch((err) => {
          if (!isMounted) return;
          setCandidates([]);
          setTotal(0);
          setError(err instanceof Error ? err.message : "Could not load candidates.");
        })
        .finally(() => {
          if (isMounted) setLoading(false);
        });
    }, 300);

    return () => {
      isMounted = false;
      window.clearTimeout(timer);
    };
  }, [search, selectedSkill]);

  const skillOptions = useMemo(() => {
    const values = new Set<string>();
    for (const candidate of candidates) {
      for (const skill of candidate.skills) {
        values.add(titleCaseSkill(skill));
      }
    }
    return ["All", ...[...values].sort()];
  }, [candidates]);

  const filteredCandidates = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return candidates;

    return candidates.filter((candidate) => {
      const haystack = [
        candidate.full_name,
        candidate.major ?? "",
        candidate.location ?? "",
        ...candidate.skills,
      ]
        .join(" ")
        .toLowerCase();
      return haystack.includes(query);
    });
  }, [candidates, search]);

  const averageMatch = useMemo(() => {
    if (filteredCandidates.length === 0) return 0;
    const scores = filteredCandidates.map((c) => c.profile_completeness ?? 0);
    return Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length);
  }, [filteredCandidates]);

  const toggleShortlist = (id: string) => {
    setShortlisted((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
  };

  return (
    <EmployerShell>
      <header className="mb-8">
        <h1 className="font-serif text-[clamp(2.35rem,4vw,3.8rem)] leading-none text-syncus-blue">
          Talent Pool
        </h1>
        <p className="mt-3 max-w-2xl text-base font-medium text-syncus-blue/58">
          Search the candidate pool by skills and profile data from the discovery API.
        </p>
        {error && <p className="mt-3 text-sm font-bold text-red-600">{error}</p>}
      </header>

      <section className="mb-8 grid gap-4 sm:grid-cols-3">
        <article className="rounded-2xl border-2 border-syncus-blue/20 bg-syncus-cream p-6 shadow-card">
          <p className="text-sm font-bold text-syncus-blue/55">Total candidates</p>
          <p className="mt-2 text-4xl font-black text-syncus-blue">{loading ? "—" : total}</p>
        </article>
        <article className="rounded-2xl border-2 border-syncus-blue/20 bg-syncus-cream p-6 shadow-card">
          <p className="text-sm font-bold text-syncus-blue/55">Showing</p>
          <p className="mt-2 text-4xl font-black text-syncus-green">{loading ? "—" : filteredCandidates.length}</p>
        </article>
        <article className="rounded-2xl border-2 border-syncus-blue/20 bg-syncus-cream p-6 shadow-card">
          <p className="text-sm font-bold text-syncus-blue/55">Avg. profile completeness</p>
          <p className="mt-2 text-4xl font-black text-syncus-blue">{loading ? "—" : `${averageMatch}%`}</p>
        </article>
      </section>

      <section className="rounded-2xl border-2 border-syncus-blue bg-syncus-cream p-5 shadow-card sm:p-7">
        <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <h2 className="font-serif text-3xl leading-none text-syncus-blue">Candidates</h2>
          <div className="flex flex-col gap-3 sm:flex-row">
            <label className="flex min-h-11 min-w-[240px] items-center gap-3 rounded-xl border-2 border-syncus-blue/20 px-4">
              <Search size={18} className="text-syncus-blue/50" />
              <input
                className="min-w-0 flex-1 bg-transparent text-sm font-bold text-syncus-blue outline-none"
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search candidates..."
                type="search"
                value={search}
              />
            </label>
            <select
              className="min-h-11 rounded-xl border-2 border-syncus-blue/20 bg-syncus-cream px-4 text-sm font-bold text-syncus-blue outline-none"
              onChange={(event) => setSelectedSkill(event.target.value)}
              value={selectedSkill}
            >
              {skillOptions.map((skill) => (
                <option key={skill} value={skill}>
                  {skill === "All" ? "All skills" : skill}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid gap-4">
          {loading && (
            <p className="rounded-xl border-2 border-dashed border-syncus-blue/25 px-4 py-10 text-center text-sm font-bold text-syncus-blue/55">
              Loading candidates...
            </p>
          )}

          {!loading &&
            filteredCandidates.map((candidate) => {
              const match = candidate.profile_completeness ?? 0;
              const role = candidate.major ?? "Candidate";
              const education = candidate.education_level
                ? `${titleCaseSkill(candidate.education_level)}${candidate.major ? ` · ${candidate.major}` : ""}`
                : candidate.major ?? "Education not listed";

              return (
                <article
                  key={candidate.candidate_id}
                  className="grid gap-4 rounded-xl border-2 border-syncus-blue/20 p-5 md:grid-cols-[auto_minmax(0,1fr)_auto] md:items-start"
                >
                  <span className="grid h-12 w-12 place-items-center rounded-xl bg-syncus-blue/10 text-syncus-blue">
                    <UserRound size={22} />
                  </span>
                  <div>
                    <h3 className="text-xl font-black text-syncus-blue">{candidate.full_name}</h3>
                    <p className="mt-1 text-sm font-medium text-syncus-blue/65">{role}</p>
                    {candidate.location && (
                      <p className="mt-1 flex items-center gap-1 text-sm font-medium text-syncus-blue/50">
                        <MapPin size={14} />
                        {candidate.location}
                      </p>
                    )}
                    <p className="mt-1 text-sm font-medium text-syncus-blue/50">{education}</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {candidate.skills.slice(0, 8).map((skill) => (
                        <span
                          key={skill}
                          className="rounded-full bg-syncus-green/10 px-3 py-1 text-xs font-bold text-syncus-green"
                        >
                          {titleCaseSkill(skill)}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <span className="rounded-full bg-syncus-lime px-4 py-2 text-sm font-black text-syncus-blue">
                      {match}% profile
                    </span>
                    <span className="text-xs font-bold text-syncus-blue/50">{matchLabel(match)}</span>
                    <button
                      className={`mt-2 min-h-10 rounded-lg px-4 text-sm font-black transition ${
                        shortlisted.includes(candidate.candidate_id)
                          ? "bg-syncus-green text-syncus-cream"
                          : "border-2 border-syncus-blue text-syncus-blue hover:bg-syncus-blue hover:text-syncus-cream"
                      }`}
                      onClick={() => toggleShortlist(candidate.candidate_id)}
                      type="button"
                    >
                      {shortlisted.includes(candidate.candidate_id) ? "Shortlisted" : "Shortlist"}
                    </button>
                  </div>
                </article>
              );
            })}

          {!loading && filteredCandidates.length === 0 && (
            <p className="rounded-xl border-2 border-dashed border-syncus-blue/25 px-4 py-10 text-center text-sm font-bold text-syncus-blue/55">
              No candidates found. Try another skill filter or search term.
            </p>
          )}
        </div>
      </section>
    </EmployerShell>
  );
}
