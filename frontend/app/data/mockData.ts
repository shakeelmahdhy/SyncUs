export interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  types: string[];
  respondsWithin: string;
  description: string;
  fullDescription: string;
  requirements: string[];
  recommended: boolean;
  postedDate: string;
  salary: string;
  experience: string;
  matchScore: number;
  applicants: number;
  interviews: number;
  skills: string[];
  category: string;
  workType: "Full-Time" | "Part-Time" | "Casual" | "Contract";
  locationMode: "Remote" | "On-site" | "Hybrid";
}

export interface Application {
  id: number;
  jobId: number;
  title: string;
  company: string;
  location: string;
  status: "Applied" | "Viewed" | "Interviewing" | "Shortlisted" | "Rejected" | "Withdrawn";
  appliedDate: string;
  matchScore: number;
  resume: string;
  notes: string;
}

export interface Candidate {
  id: number;
  name: string;
  role: string;
  location: string;
  experience: string;
  skills: string[];
  matchScore: number;
  education: string;
  availability: string;
  savedToPool: boolean;
  applicationStatus?: string;
}

export interface TeamMember {
  id: number;
  name: string;
  email: string;
  role: string;
  accessLevel: "Admin" | "Reviewer" | "Interviewer";
  jobsAssigned: string[];
  joinedDate: string;
  avatar: string;
}

export const jobs: Job[] = [
  {
    id: 1,
    title: "Senior Product Designer",
    company: "ThisCompany",
    location: "Sydney, NSW",
    types: ["Remote", "Full-Time"],
    respondsWithin: "<3 days",
    description: "We're looking for a talented Senior Product Designer to lead our design team...",
    fullDescription: "Join our fast-growing team as a Senior Product Designer. You'll lead the design process from conception to delivery, working closely with engineering and product management to create beautiful, functional user experiences. You'll be responsible for establishing and maintaining our design system, conducting user research, and mentoring junior designers.",
    requirements: ["5+ years of UX/UI design experience", "Proficiency in Figma and prototyping tools", "Strong portfolio showcasing end-to-end design work", "Experience with design systems at scale", "Excellent communication and collaboration skills"],
    recommended: true,
    postedDate: "2 days ago",
    salary: "$120,000 – $150,000",
    experience: "5+ years",
    matchScore: 95,
    applicants: 128,
    interviews: 12,
    skills: ["Figma", "User Research", "Prototyping", "Design Systems", "UX Writing"],
    category: "Design",
    workType: "Full-Time",
    locationMode: "Remote",
  },
  {
    id: 2,
    title: "Lead Frontend Engineer (React)",
    company: "AnotherCompany",
    location: "Sydney, NSW",
    types: ["Remote", "Full-Time"],
    respondsWithin: "<3 days",
    description: "We're looking for a React expert to lead our frontend engineering team...",
    fullDescription: "We are seeking an experienced Lead Frontend Engineer to architect and build high-performance React applications. You'll be driving technical decisions, mentoring a team of 4 engineers, and collaborating directly with design and product to ship world-class features.",
    requirements: ["6+ years of frontend development experience", "Deep expertise in React and TypeScript", "Experience with modern build tools (Vite, Webpack)", "Track record of leading technical teams", "Strong understanding of web performance optimisation"],
    recommended: true,
    postedDate: "2 days ago",
    salary: "$130,000 – $160,000",
    experience: "6+ years",
    matchScore: 88,
    applicants: 84,
    interviews: 5,
    skills: ["React", "TypeScript", "Next.js", "Node.js", "GraphQL"],
    category: "Engineering",
    workType: "Full-Time",
    locationMode: "Remote",
  },
  {
    id: 3,
    title: "Marketing Operations Manager",
    company: "RandomCompany",
    location: "Wollongong, NSW",
    types: ["Remote", "Full-Time"],
    respondsWithin: "<3 days",
    description: "We're looking for a data-driven Marketing Operations Manager...",
    fullDescription: "We need a Marketing Operations Manager to own our marketing technology stack, manage campaigns across channels, and deliver actionable insights to the business. You'll work cross-functionally with sales and product to drive pipeline and revenue growth.",
    requirements: ["3+ years in marketing operations", "Proficiency with HubSpot or Marketo", "Strong analytical skills and data-driven mindset", "Experience with CRM systems and marketing automation", "Excellent project management skills"],
    recommended: true,
    postedDate: "2 days ago",
    salary: "$90,000 – $110,000",
    experience: "3+ years",
    matchScore: 72,
    applicants: 56,
    interviews: 0,
    skills: ["HubSpot", "Marketo", "Salesforce", "SQL", "Analytics"],
    category: "Marketing",
    workType: "Full-Time",
    locationMode: "Remote",
  },
  {
    id: 4,
    title: "UX Researcher",
    company: "DesignCo",
    location: "Melbourne, VIC",
    types: ["Hybrid", "Full-Time"],
    respondsWithin: "<5 days",
    description: "We're seeking a passionate UX Researcher to uncover user insights...",
    fullDescription: "As a UX Researcher, you will plan and conduct qualitative and quantitative research studies, synthesise findings, and communicate insights to cross-functional teams. You'll play a key role in shaping product strategy and ensuring our products meet user needs.",
    requirements: ["3+ years of UX research experience", "Expertise in qualitative and quantitative research methods", "Experience with usability testing tools", "Strong data analysis skills", "Excellent written and verbal communication"],
    recommended: false,
    postedDate: "5 days ago",
    salary: "$95,000 – $115,000",
    experience: "3+ years",
    matchScore: 80,
    applicants: 42,
    interviews: 3,
    skills: ["User Research", "Usability Testing", "Data Analysis", "Survey Design", "Figma"],
    category: "Design",
    workType: "Full-Time",
    locationMode: "Hybrid",
  },
  {
    id: 5,
    title: "DevOps Engineer",
    company: "CloudBase",
    location: "Brisbane, QLD",
    types: ["On-site", "Full-Time"],
    respondsWithin: "<7 days",
    description: "Looking for a skilled DevOps Engineer to manage our cloud infrastructure...",
    fullDescription: "Join CloudBase as a DevOps Engineer to design and maintain scalable cloud infrastructure on AWS. You'll implement CI/CD pipelines, automate deployment workflows, monitor system performance, and ensure high availability of our services.",
    requirements: ["4+ years in DevOps or SRE role", "Strong AWS or GCP expertise", "Experience with Kubernetes and Docker", "Proficiency in infrastructure as code (Terraform)", "Strong scripting skills (Python, Bash)"],
    recommended: false,
    postedDate: "1 week ago",
    salary: "$115,000 – $140,000",
    experience: "4+ years",
    matchScore: 60,
    applicants: 31,
    interviews: 2,
    skills: ["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD"],
    category: "Engineering",
    workType: "Full-Time",
    locationMode: "On-site",
  },
  {
    id: 6,
    title: "Product Manager",
    company: "GrowthLab",
    location: "Sydney, NSW",
    types: ["Hybrid", "Full-Time"],
    respondsWithin: "<2 days",
    description: "We're looking for a strategic Product Manager to drive our core product...",
    fullDescription: "GrowthLab is looking for an experienced Product Manager to own our flagship product roadmap. You'll define strategy, work with designers and engineers to ship great features, and use data to drive decisions. You'll be the glue between business goals and user needs.",
    requirements: ["4+ years of product management experience", "Strong analytical and data skills", "Experience with agile development methodologies", "Excellent stakeholder management skills", "Track record of shipping impactful products"],
    recommended: true,
    postedDate: "3 days ago",
    salary: "$125,000 – $155,000",
    experience: "4+ years",
    matchScore: 85,
    applicants: 97,
    interviews: 8,
    skills: ["Product Strategy", "Roadmapping", "Data Analysis", "Agile", "Stakeholder Management"],
    category: "Product",
    workType: "Full-Time",
    locationMode: "Hybrid",
  },
];

export const applications: Application[] = [
  {
    id: 1,
    jobId: 1,
    title: "Senior Product Designer",
    company: "ThisCompany",
    location: "Sydney, NSW",
    status: "Interviewing",
    appliedDate: "Apr 15, 2026",
    matchScore: 95,
    resume: "Product_Designer_Resume_v3.pdf",
    notes: "Interview scheduled for Oct 24 at 10:00 AM AEST",
  },
  {
    id: 2,
    jobId: 2,
    title: "Lead Frontend Engineer (React)",
    company: "AnotherCompany",
    location: "Sydney, NSW",
    status: "Applied",
    appliedDate: "Apr 20, 2026",
    matchScore: 88,
    resume: "Frontend_Engineer_Resume.pdf",
    notes: "",
  },
  {
    id: 3,
    jobId: 3,
    title: "Marketing Operations Manager",
    company: "RandomCompany",
    location: "Wollongong, NSW",
    status: "Viewed",
    appliedDate: "Apr 18, 2026",
    matchScore: 72,
    resume: "General_Resume_2026.pdf",
    notes: "Application viewed by recruiter",
  },
  {
    id: 4,
    jobId: 6,
    title: "Product Manager",
    company: "GrowthLab",
    location: "Sydney, NSW",
    status: "Shortlisted",
    appliedDate: "Apr 10, 2026",
    matchScore: 85,
    resume: "Product_Designer_Resume_v3.pdf",
    notes: "Top 10 candidates",
  },
  {
    id: 5,
    jobId: 4,
    title: "UX Researcher",
    company: "DesignCo",
    location: "Melbourne, VIC",
    status: "Rejected",
    appliedDate: "Apr 5, 2026",
    matchScore: 80,
    resume: "Product_Designer_Resume_v3.pdf",
    notes: "Position filled internally",
  },
];

export const candidates: Candidate[] = [
  {
    id: 1,
    name: "Samantha Lee",
    role: "Senior Product Designer",
    location: "Sydney, NSW",
    experience: "7 years",
    skills: ["Figma", "User Research", "Prototyping", "Design Systems"],
    matchScore: 95,
    education: "BDes, University of Sydney",
    availability: "2 weeks notice",
    savedToPool: false,
    applicationStatus: "Interviewing",
  },
  {
    id: 2,
    name: "James Chen",
    role: "Full-Stack Engineer",
    location: "Melbourne, VIC",
    experience: "5 years",
    skills: ["React", "Node.js", "TypeScript", "PostgreSQL"],
    matchScore: 88,
    education: "BSc Computer Science, Monash University",
    availability: "Immediately",
    savedToPool: true,
    applicationStatus: "Applied",
  },
  {
    id: 3,
    name: "Priya Sharma",
    role: "Product Manager",
    location: "Sydney, NSW",
    experience: "6 years",
    skills: ["Product Strategy", "Agile", "Data Analysis", "Roadmapping"],
    matchScore: 82,
    education: "MBA, UNSW Business School",
    availability: "1 month notice",
    savedToPool: false,
    applicationStatus: "Shortlisted",
  },
  {
    id: 4,
    name: "Tom Nguyen",
    role: "UX Designer",
    location: "Brisbane, QLD",
    experience: "4 years",
    skills: ["Figma", "UX Research", "Wireframing", "Interaction Design"],
    matchScore: 76,
    education: "BDes, QUT",
    availability: "3 weeks notice",
    savedToPool: false,
  },
  {
    id: 5,
    name: "Emma Walsh",
    role: "Marketing Manager",
    location: "Sydney, NSW",
    experience: "5 years",
    skills: ["HubSpot", "Content Strategy", "SEO", "Analytics"],
    matchScore: 71,
    education: "BComm, University of Sydney",
    availability: "2 months notice",
    savedToPool: true,
  },
  {
    id: 6,
    name: "David Kim",
    role: "DevOps Engineer",
    location: "Perth, WA",
    experience: "8 years",
    skills: ["AWS", "Kubernetes", "Terraform", "CI/CD", "Python"],
    matchScore: 90,
    education: "BSc Computer Engineering, Curtin University",
    availability: "1 month notice",
    savedToPool: false,
  },
];

export const teamMembers: TeamMember[] = [
  {
    id: 1,
    name: "John Doe",
    email: "john.doe@thiscompany.com",
    role: "Talent Lead",
    accessLevel: "Admin",
    jobsAssigned: ["Senior Product Designer", "Lead Frontend Engineer", "Marketing Operations Manager"],
    joinedDate: "Jan 2025",
    avatar: "JD",
  },
  {
    id: 2,
    name: "Sarah Mitchell",
    email: "s.mitchell@thiscompany.com",
    role: "Hiring Manager",
    accessLevel: "Reviewer",
    jobsAssigned: ["Senior Product Designer", "Marketing Operations Manager"],
    joinedDate: "Mar 2025",
    avatar: "SM",
  },
  {
    id: 3,
    name: "Chris Baker",
    email: "c.baker@thiscompany.com",
    role: "Lead Engineer",
    accessLevel: "Interviewer",
    jobsAssigned: ["Lead Frontend Engineer"],
    joinedDate: "Apr 2026",
    avatar: "CB",
  },
  {
    id: 4,
    name: "Mia Torres",
    email: "m.torres@thiscompany.com",
    role: "Design Lead",
    accessLevel: "Interviewer",
    jobsAssigned: ["Senior Product Designer"],
    joinedDate: "Apr 2026",
    avatar: "MT",
  },
];

export const analyticsData = {
  overview: {
    totalViews: 2847,
    totalApplications: 268,
    clickToApplyRate: "9.4%",
    avgTimeToHire: "18 days",
    offersExtended: 4,
    aiMatchAvg: 94,
  },
  applicationsByJob: [
    { job: "Sr. Product Designer", applications: 128, interviews: 12, shortlisted: 28 },
    { job: "Lead Frontend Eng.", applications: 84, interviews: 5, shortlisted: 15 },
    { job: "Marketing Ops Mgr", applications: 56, interviews: 0, shortlisted: 8 },
  ],
  applicationsByWeek: [
    { week: "Week 1", applications: 45 },
    { week: "Week 2", applications: 78 },
    { week: "Week 3", applications: 92 },
    { week: "Week 4", applications: 53 },
  ],
  sourceBreakdown: [
    { source: "SyncUs AI Match", value: 45, color: "#00804d" },
    { source: "Direct Search", value: 30, color: "#1e4890" },
    { source: "Referral", value: 15, color: "#dbe64c" },
    { source: "Other", value: 10, color: "#94a3b8" },
  ],
  upcomingInterviews: [
    { id: 1, candidate: "Samantha Lee", role: "Senior Product Designer", date: "Oct 24", time: "10:00 AM AEST", type: "Video" },
    { id: 2, candidate: "Samantha Lee", role: "Senior Product Designer", date: "Oct 24", time: "2:30 PM AEST", type: "Video" },
  ],
};
