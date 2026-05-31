import { useState } from "react";
import { EmployerShell } from "./EmployerShell";

const candidates = [
  {
    name: "Sarah Johnson",
    role: "Frontend Developer",
    location: "Sydney, NSW",
    education: "Bachelor of Computer Science",
    skills: ["React", "TypeScript", "UI/UX"],
    match: 95,
    status: "Recommended",
  },
  {
    name: "Michael Lee",
    role: "UI/UX Designer",
    location: "Wollongong, NSW",
    education: "Bachelor of IT",
    skills: ["Figma", "Product Design", "Wireframing"],
    match: 89,
    status: "Strong Match",
  },
  {
    name: "Aisha Khan",
    role: "Backend Developer",
    location: "Sydney, NSW",
    education: "Master of Computer Science",
    skills: ["Python", "FastAPI", "PostgreSQL"],
    match: 84,
    status: "Good Match",
  },
];

export function EmployerTalentPoolPage() {
  const [search, setSearch] = useState("");
  const [selectedSkill, setSelectedSkill] = useState("All");
  const [shortlisted, setShortlisted] = useState<string[]>([]);

  const filteredCandidates = candidates.filter((candidate) => {
    const matchesSearch =
      candidate.name.toLowerCase().includes(search.toLowerCase()) ||
      candidate.role.toLowerCase().includes(search.toLowerCase()) ||
      candidate.skills.join(" ").toLowerCase().includes(search.toLowerCase());

    const matchesSkill =
      selectedSkill === "All" || candidate.skills.includes(selectedSkill);

    return matchesSearch && matchesSkill;
  });

  const toggleShortlist = (name: string) => {
    setShortlisted((prev) =>
      prev.includes(name)
        ? prev.filter((item) => item !== name)
        : [...prev, name]
    );
  };

  return (
    <EmployerShell>
    <div className="bg-[#F8FAF5]">
      <h1 className="text-5xl font-bold text-[#1D2B53] mb-8">
        Talent Pool Dashboard
      </h1>

      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-2xl shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-600">Total Candidates</h3>
          <p className="text-4xl font-bold text-[#1D2B53] mt-4">128</p>
        </div>

        <div className="bg-white rounded-2xl shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-600">Interview Ready</h3>
          <p className="text-4xl font-bold text-green-600 mt-4">42</p>
        </div>

        <div className="bg-white rounded-2xl shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-600">AI Match Average</h3>
          <p className="text-4xl font-bold text-blue-600 mt-4">89%</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-lg p-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-semibold text-[#1D2B53]">
            Top Candidates
          </h2>

          <div className="flex gap-3">
            <input
              type="text"
              placeholder="Search candidates..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="border rounded-xl px-4 py-2 w-64"
            />

            <select
              value={selectedSkill}
              onChange={(e) => setSelectedSkill(e.target.value)}
              className="border rounded-xl px-4 py-2"
            >
              <option>All</option>
              <option>React</option>
              <option>TypeScript</option>
              <option>Figma</option>
              <option>Python</option>
              <option>FastAPI</option>
            </select>
          </div>
        </div>

        <div className="space-y-6">
          {filteredCandidates.map((candidate) => (
            <div
              key={candidate.name}
              className="border-2 border-gray-200 rounded-2xl p-6 hover:shadow-lg transition"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-2xl font-bold text-[#1D2B53]">
                    {candidate.name}
                  </h3>

                  <p className="text-gray-600 mt-1">{candidate.role}</p>
                  <p className="text-sm text-gray-500 mt-1">{candidate.location}</p>
                  <p className="text-sm text-gray-500 mt-1">
                    {candidate.education}
                  </p>

                  <div className="flex gap-2 mt-4">
                    {candidate.skills.map((skill) => (
                      <span
                        key={skill}
                        className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="text-right">
                  <div className="bg-blue-100 text-blue-700 px-4 py-2 rounded-full font-semibold mb-3">
                    {candidate.match}% Match
                  </div>

                  <p className="text-sm text-gray-500 mb-4">
                    {candidate.status}
                  </p>

                  <div className="flex gap-2">
                    <button className="bg-[#1D2B53] text-white px-4 py-2 rounded-xl">
                      View Profile
                    </button>

                    <button
                      onClick={() => toggleShortlist(candidate.name)}
                      className="bg-green-600 text-white px-4 py-2 rounded-xl"
                    >
                      {shortlisted.includes(candidate.name)
                        ? "Shortlisted"
                        : "Shortlist"}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {filteredCandidates.length === 0 && (
            <p className="text-gray-500 text-center py-8">
              No candidates found.
            </p>
          )}
        </div>
      </div>
    </div>
    </EmployerShell>
  );
}

export default EmployerTalentPoolPage;
