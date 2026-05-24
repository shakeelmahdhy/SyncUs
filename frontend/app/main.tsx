import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes, useLocation } from 'react-router';
import './styles.css';
import { ApplicationsPage } from './pages/ApplicationsPage';
import { EmployerDashboardPage } from './pages/employer/DashboardPage';
import { EmployerLoginPage } from './pages/employer/LoginPage';
import { EmployerPostJobPage } from './pages/employer/PostJobPage';
import { RequireEmployer } from './pages/employer/RequireEmployer';
import { EmployerReviewApplicationsPage } from './pages/employer/ReviewApplicationsPage';
import { JobDetailPage } from './pages/JobsDetailPage';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { ProfilePage } from './pages/ProfilePage';
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
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegistrationPage />} />
        <Route path="/employer/login" element={<EmployerLoginPage />} />
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
