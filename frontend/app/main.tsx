import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Navigate, Route, Routes, useLocation } from 'react-router';
import './styles.css';
import { ApplicationsPage } from './pages/ApplicationsPage';
import { EmployerDashboardPage } from './pages/employer/DashboardPage';
import { EmployerAnalyticsPage } from './pages/employer/AnalyticsPage';
import { HiringTeamPage } from './pages/employer/HiringTeamPage';
import { EmployerLoginPage } from './pages/employer/LoginPage';
import { EmployerPostJobPage } from './pages/employer/PostJobPage';
import { RequireEmployer } from './pages/employer/RequireEmployer';
import { EmployerReviewApplicationsPage } from './pages/employer/ReviewApplicationsPage';
import { EmployerTalentPoolPage } from './pages/employer/TalentPoolPage';
import { JobDetailPage } from './pages/JobsDetailPage';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { ProfilePage } from './pages/ProfilePage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { RegistrationPage } from './pages/RegistrationPage';
import { RequireAuth } from './pages/RequireAuth';
import { SiteFooter, SiteNav } from './shared/components';

function AppRoutes() {
  const location = useLocation();
  const isEmployerRoute = location.pathname.startsWith('/employer');

  return (
    <div className="min-h-screen bg-syncus-cream text-syncus-blue">
      {!isEmployerRoute && <SiteNav />}
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/jobs" element={<Navigate replace to="/#jobs" />} />
        <Route path="/matches" element={<Navigate replace to="/recommendations" />} />
        <Route
          path="/applications"
          element={
            <RequireAuth>
              <ApplicationsPage />
            </RequireAuth>
          }
        />
        <Route path="/jobs/:id" element={<JobDetailPage />} />
        <Route
          path="/profile"
          element={
            <RequireAuth>
              <ProfilePage />
            </RequireAuth>
          }
        />
        <Route
          path="/recommendations"
          element={
            <RequireAuth>
              <RecommendationsPage />
            </RequireAuth>
          }
        />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegistrationPage />} />
        <Route path="/employer/login" element={<EmployerLoginPage />} />
        <Route path="/employer" element={<Navigate replace to="/employer/dashboard" />} />
        <Route path="/employer/applications" element={<Navigate replace to="/employer/review-applications" />} />
        <Route
          path="/employer/dashboard"
          element={
            <RequireEmployer>
              <EmployerDashboardPage />
            </RequireEmployer>
          }
        />
        <Route
          path="/employer/post-job"
          element={
            <RequireEmployer>
              <EmployerPostJobPage />
            </RequireEmployer>
          }
        />
        <Route
          path="/employer/review-applications"
          element={
            <RequireEmployer>
              <EmployerReviewApplicationsPage />
            </RequireEmployer>
          }
        />
        <Route
          path="/employer/talent-pool"
          element={
            <RequireEmployer>
              <EmployerTalentPoolPage />
            </RequireEmployer>
          }
        />
        <Route
          path="/employer/hiring-team"
          element={
            <RequireEmployer>
              <HiringTeamPage />
            </RequireEmployer>
          }
        />
        <Route
          path="/employer/analytics"
          element={
            <RequireEmployer>
              <EmployerAnalyticsPage />
            </RequireEmployer>
          }
        />
        <Route path="*" element={<LandingPage />} />
      </Routes>
      {!isEmployerRoute && <SiteFooter />}
    </div>
  );
}

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  </React.StrictMode>
);
