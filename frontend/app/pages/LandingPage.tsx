import { useMemo, useState } from 'react';
import { Briefcase, CheckCircle2, ChevronLeft, ChevronRight, Filter, MapPin, Search, X } from 'lucide-react';
import { useNavigate } from 'react-router';
import { Job, jobs } from '../data/mockData';
import { SiteFooter, SiteNav } from '../shared/components';

const jobTypes = ['Full-Time', 'Part-Time', 'Casual', 'Contract'];
const locationModes = ['On-site', 'Remote', 'Hybrid'];
const JOBS_PER_PAGE = 3;

function normalise(value: string) {
  return value.toLowerCase().replace(/\s+/g, '').replace(/-/g, '');
}

function FilterCheckbox({ label, checked, onChange }: { label: string; checked: boolean; onChange: () => void }) {
  return (
    <label className="flex cursor-pointer items-center gap-2 text-sm font-medium text-syncus-green">
      <input className="h-3.5 w-3.5 accent-syncus-green" type="checkbox" checked={checked} onChange={onChange} />
      <span>{label}</span>
    </label>
  );
}

function JobCard({ job, onApply }: { job: Job; onApply: () => void }) {
  return (
    <article className="rounded-2xl border-2 border-syncus-green bg-syncus-cream p-5 shadow-card transition duration-200 hover:-translate-y-1 hover:shadow-syncus">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex gap-4">
          <div className="grid h-14 w-14 shrink-0 place-items-center rounded-xl bg-syncus-green text-syncus-cream">
            <Briefcase size={25} />
          </div>
          <div>
            <h3 className="text-2xl font-medium leading-tight text-syncus-green">{job.title}</h3>
            <p className="mt-1 text-base font-medium text-syncus-blue">{job.company} · {job.location}</p>
          </div>
        </div>
        <div className="flex shrink-0 items-start gap-3 sm:flex-col sm:items-end">
          {job.recommended && <span className="rounded-full bg-syncus-blue px-4 py-1 text-xs font-bold text-syncus-cream">Recommended</span>}
          <span className="text-xs font-bold text-syncus-blue">{job.postedDate}</span>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        {[job.locationMode, job.workType, `Responds within ${job.respondsWithin}`].map((tag) => (
          <span key={tag} className="rounded-md bg-syncus-blue/35 px-3 py-1.5 text-xs font-bold text-white">{tag}</span>
        ))}
      </div>

      <div className="mt-5 border-t border-syncus-green/25 pt-4">
        <p className="text-sm italic text-syncus-green">{job.description}</p>
        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap gap-2">
            {job.skills.slice(0, 4).map((skill) => (
              <span key={skill} className="rounded-full border border-syncus-green/45 px-3 py-1 text-xs font-medium text-syncus-green">{skill}</span>
            ))}
          </div>
          <button className="min-h-9 rounded-lg bg-syncus-blue px-8 text-sm font-bold text-syncus-cream transition hover:bg-syncus-green" type="button" onClick={onApply}>
            Quick Apply
          </button>
        </div>
      </div>
    </article>
  );
}

export function LandingPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [location, setLocation] = useState('');
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [selectedModes, setSelectedModes] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [showApplyModal, setShowApplyModal] = useState(false);

  const filtered = useMemo(() => {
    return jobs.filter((job) => {
      const query = search.trim().toLowerCase();
      const locationQuery = location.trim().toLowerCase();
      const matchesSearch = !query || [job.title, job.company, job.description, job.category, ...job.skills].some((value) => value.toLowerCase().includes(query));
      const matchesLocation = !locationQuery || job.location.toLowerCase().includes(locationQuery);
      const matchesType = selectedTypes.length === 0 || selectedTypes.some((type) => normalise(type) === normalise(job.workType));
      const matchesMode = selectedModes.length === 0 || selectedModes.some((mode) => normalise(mode) === normalise(job.locationMode));
      return matchesSearch && matchesLocation && matchesType && matchesMode;
    });
  }, [location, search, selectedModes, selectedTypes]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / JOBS_PER_PAGE));
  const visiblePage = Math.min(currentPage, totalPages);
  const paged = filtered.slice((visiblePage - 1) * JOBS_PER_PAGE, visiblePage * JOBS_PER_PAGE);

  const toggleType = (type: string) => {
    setSelectedTypes((current) => (current.includes(type) ? current.filter((item) => item !== type) : [...current, type]));
    setCurrentPage(1);
  };

  const toggleMode = (mode: string) => {
    setSelectedModes((current) => (current.includes(mode) ? current.filter((item) => item !== mode) : [...current, mode]));
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setSelectedTypes([]);
    setSelectedModes([]);
    setLocation('');
    setSearch('');
    setCurrentPage(1);
  };

  return (
    <div className="min-h-screen overflow-hidden bg-syncus-cream text-syncus-blue">
      <SiteNav />

      <main className="relative">
        <div className="pointer-events-none absolute left-[-8%] top-[40px] h-[640px] w-[520px] rounded-[46%] bg-syncus-green/15 blur-3xl" />
        <div className="pointer-events-none absolute left-[28%] top-[130px] h-[430px] w-[360px] rotate-[-17deg] rounded-[38%] bg-syncus-green/12 blur-3xl" />
        <div className="pointer-events-none absolute right-[10%] top-[260px] h-[360px] w-[360px] rounded-full bg-syncus-lime/10 blur-3xl" />

        <section className="relative mx-auto max-w-[1260px] px-5 pb-20 pt-20 text-center sm:px-8 lg:pt-24">
          <h1 className="mx-auto max-w-[980px] font-serif text-[clamp(3rem,7vw,6.6rem)] leading-[0.96] tracking-normal">
            <span className="block bg-gradient-to-r from-syncus-lime via-syncus-green to-syncus-blue bg-clip-text text-transparent">Syncing You</span>
            <span className="block bg-gradient-to-r from-syncus-lime via-syncus-green to-syncus-blue bg-clip-text text-transparent">With The Perfect Role</span>
          </h1>
          <p className="mt-8 text-lg font-medium text-syncus-blue">Find Your Perfect Match.</p>

          <form className="mx-auto mt-5 flex max-w-[720px] flex-col gap-2 rounded-2xl border-2 border-syncus-green bg-syncus-cream p-2 shadow-syncus sm:flex-row" onSubmit={(event) => event.preventDefault()}>
            <label className="flex min-h-12 flex-1 items-center gap-3 rounded-xl bg-syncus-green/15 px-4 text-syncus-green">
              <Search size={18} />
              <input
                className="min-w-0 flex-1 bg-transparent text-sm font-medium outline-none placeholder:text-syncus-green/70"
                type="search"
                placeholder="Search job descriptions, skills, or titles..."
                value={search}
                onChange={(event) => { setSearch(event.target.value); setCurrentPage(1); }}
              />
            </label>
            <button className="min-h-12 rounded-xl bg-syncus-green px-9 text-base font-bold text-syncus-cream transition hover:-translate-y-0.5 hover:bg-syncus-blue" type="submit">
              Search
            </button>
          </form>
        </section>

        <section id="jobs" className="relative mx-auto grid max-w-[1180px] gap-10 px-5 pb-28 sm:px-8 lg:grid-cols-[300px_1fr] lg:items-start">
          <aside className="rounded-2xl border-2 border-syncus-green bg-syncus-cream p-6 shadow-card lg:sticky lg:top-28">
            <div className="mb-6 flex items-center gap-3 text-syncus-green">
              <Filter size={20} />
              <h2 className="text-xl font-bold">Quick Filters</h2>
            </div>

            <div className="mb-6">
              <p className="mb-2 text-sm font-bold text-syncus-green">Location</p>
              <label className="flex min-h-10 items-center gap-2 rounded-xl border-2 border-syncus-green px-3 text-syncus-green">
                <MapPin size={15} />
                <input
                  className="min-w-0 flex-1 bg-transparent text-xs font-medium outline-none placeholder:text-syncus-green/65"
                  placeholder="Sydney, NSW, Australia..."
                  value={location}
                  onChange={(event) => { setLocation(event.target.value); setCurrentPage(1); }}
                />
              </label>
            </div>

            <div className="mb-6">
              <p className="mb-3 text-sm font-bold text-syncus-green">Job Type</p>
              <div className="grid grid-cols-2 gap-x-4 gap-y-3">
                {jobTypes.map((type) => <FilterCheckbox key={type} label={type} checked={selectedTypes.includes(type)} onChange={() => toggleType(type)} />)}
              </div>
            </div>

            <div>
              <p className="mb-3 text-sm font-bold text-syncus-green">Work Mode</p>
              <div className="grid grid-cols-2 gap-x-4 gap-y-3">
                {locationModes.map((mode) => <FilterCheckbox key={mode} label={mode} checked={selectedModes.includes(mode)} onChange={() => toggleMode(mode)} />)}
              </div>
            </div>

            {(selectedTypes.length > 0 || selectedModes.length > 0 || location || search) && (
              <button className="mt-6 flex items-center gap-1 text-xs font-bold text-syncus-green underline underline-offset-4" type="button" onClick={clearFilters}>
                <X size={13} /> Clear all filters
              </button>
            )}
          </aside>

          <section>
            <h2 className="mb-8 text-[clamp(2rem,4vw,3.1rem)] font-serif leading-none text-syncus-green">Active Job Postings ({filtered.length})</h2>
            <div className="grid gap-6">
              {paged.length > 0 ? paged.map((job) => <JobCard key={job.id} job={job} onApply={() => setShowApplyModal(true)} />) : (
                <div className="rounded-2xl border-2 border-dashed border-syncus-green px-6 py-16 text-center text-syncus-green">
                  <p className="text-xl font-bold">No jobs match your filters</p>
                  <p className="mt-2 text-sm opacity-70">Try adjusting your search criteria.</p>
                </div>
              )}
            </div>

            {filtered.length > JOBS_PER_PAGE && (
              <div className="mt-12 flex items-center justify-center gap-3">
                <button className="grid h-11 w-11 place-items-center rounded-xl border-2 border-syncus-green text-syncus-green transition hover:bg-syncus-green hover:text-syncus-cream" type="button" onClick={() => setCurrentPage((page) => Math.max(1, page - 1))} aria-label="Previous page"><ChevronLeft size={18} /></button>
                {Array.from({ length: totalPages }, (_, index) => index + 1).map((page) => (
                  <button key={page} className={`grid h-11 w-11 place-items-center rounded-xl border-2 border-syncus-green text-lg font-bold transition ${page === visiblePage ? 'bg-syncus-green text-syncus-cream' : 'text-syncus-green hover:bg-syncus-green hover:text-syncus-cream'}`} type="button" onClick={() => setCurrentPage(page)}>
                    {page}
                  </button>
                ))}
                <button className="grid h-11 w-11 place-items-center rounded-xl border-2 border-syncus-green text-syncus-green transition hover:bg-syncus-green hover:text-syncus-cream" type="button" onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))} aria-label="Next page"><ChevronRight size={18} /></button>
              </div>
            )}
          </section>
        </section>
      </main>

      <SiteFooter />

      {showApplyModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-syncus-blue/45 px-5 backdrop-blur-sm">
          <section className="w-full max-w-md rounded-3xl border-2 border-syncus-green bg-syncus-cream p-8 text-center shadow-syncus">
            <div className="mx-auto mb-5 grid h-14 w-14 place-items-center rounded-2xl bg-syncus-lime text-syncus-blue"><CheckCircle2 size={28} /></div>
            <h3 className="font-serif text-3xl text-syncus-blue">Sign in to Apply</h3>
            <p className="mt-3 text-sm leading-relaxed text-syncus-green">Create a free account or sign in to track your applications and apply to jobs.</p>
            <div className="mt-8 grid gap-3 sm:grid-cols-2">
              <button className="min-h-12 rounded-2xl bg-syncus-green px-5 text-sm font-bold text-syncus-cream transition hover:bg-syncus-blue" type="button" onClick={() => { setShowApplyModal(false); navigate('/profile'); }}>
                Create Account
              </button>
              <button className="min-h-12 rounded-2xl border-2 border-syncus-green px-5 text-sm font-bold text-syncus-green transition hover:bg-syncus-green hover:text-syncus-cream" type="button" onClick={() => setShowApplyModal(false)}>
                Sign In
              </button>
            </div>
            <button className="mt-5 text-xs font-bold text-syncus-blue/70 underline underline-offset-4" type="button" onClick={() => setShowApplyModal(false)}>
              Continue Browsing
            </button>
          </section>
        </div>
      )}
    </div>
  );
}
