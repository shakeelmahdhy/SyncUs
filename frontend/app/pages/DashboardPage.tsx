const jobs = [
  {
    title: "Frontend Developer",
    applicants: 24,
    status: "Active",
    views: 120,
  },
  {
    title: "UI/UX Designer",
    applicants: 18,
    status: "Active",
    views: 97,
  },
  {
    title: "Backend Developer",
    applicants: 31,
    status: "Closing Soon",
    views: 143,
  },
];

const interviews = [
  {
    candidate: "Sarah Johnson",
    role: "Frontend Developer",
    time: "10:00 AM",
  },
  {
    candidate: "Michael Lee",
    role: "UI/UX Designer",
    time: "1:30 PM",
  },
];

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-[#F8FAF5] px-10 py-8">
      <h1 className="text-5xl font-bold text-[#1D2B53] mt-4 mb-10">
        Dashboard
      </h1>

      <div className="grid grid-cols-4 gap-6 mb-10">

        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-600">
            Active Jobs
          </h3>

          <p className="text-4xl font-bold text-[#1D2B53] mt-4">
            6
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-600">
            Applications
          </h3>

          <p className="text-4xl font-bold text-green-600 mt-4">
            24
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-600">
            AI Matches
          </h3>

          <p className="text-4xl font-bold text-blue-600 mt-4">
            18
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-600">
            Shortlisted
          </h3>

          <p className="text-4xl font-bold text-purple-600 mt-4">
            12
          </p>
        </div>

      </div>

      <div className="grid grid-cols-2 gap-8">

        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h2 className="text-3xl font-semibold mb-6 text-[#1D2B53]">
            Active Job Postings
          </h2>

          <div className="space-y-5">
            {jobs.map((job) => (
              <div
                key={job.title}
                className="border rounded-2xl p-5 hover:shadow-md transition"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-xl font-bold text-[#1D2B53]">
                      {job.title}
                    </h3>

                    <p className="text-gray-500 mt-1">
                      {job.applicants} Applicants
                    </p>

                    <p className="text-gray-500">
                      {job.views} Views
                    </p>
                  </div>

                  <span className="bg-green-100 text-green-700 px-4 py-2 rounded-full font-medium">
                    {job.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h2 className="text-3xl font-semibold mb-6 text-[#1D2B53]">
            Upcoming Interviews
          </h2>

          <div className="space-y-4">
            {interviews.map((interview) => (
              <div
                key={interview.candidate}
                className="border rounded-2xl p-5 hover:shadow-md transition"
              >
                <h3 className="text-xl font-bold text-[#1D2B53]">
                  {interview.candidate}
                </h3>

                <p className="text-gray-600 mt-1">
                  {interview.role}
                </p>

                <p className="text-blue-600 font-medium mt-2">
                  {interview.time}
                </p>
              </div>
            ))}
          </div>
        </div>

      </div>

      <div className="bg-white rounded-2xl shadow-lg p-8 mt-8">
        <h2 className="text-3xl font-semibold mb-6 text-[#1D2B53]">
          Recent Activity
        </h2>

        <div className="space-y-4">
          <div className="border rounded-xl p-4">
            New candidate matched with Frontend Developer role
          </div>

          <div className="border rounded-xl p-4">
            3 applications received today
          </div>

          <div className="border rounded-xl p-4">
            Backend Developer posting reached 100+ views
          </div>
        </div>
      </div>
    </div>
  );
}
