import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router';
import './styles.css';
import { ApplicationsPage } from './pages/ApplicationsPage';
import { EmployerDashboardPage } from './pages/employer/DashboardPage';
import { EmployerPostJobPage } from './pages/employer/PostJobPage';
import { EmployerReviewApplicationsPage } from './pages/employer/ReviewApplicationsPage';
import { JobDetailPage } from './pages/JobsDetailPage';
import { LandingPage } from './pages/LandingPage';
import { ProfilePage } from './pages/ProfilePage';
import { RegistrationPage } from './pages/RegistrationPage';
import { SiteFooter, SiteNav } from './shared/components';
createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <div className="min-h-screen bg-syncus-cream text-syncus-blue">
        <SiteNav />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/applications" element={<ApplicationsPage />} />
          <Route path="/jobs/:id" element={<JobDetailPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/register" element={<RegistrationPage />} />
          <Route path="/employer/dashboard" element={<EmployerDashboardPage />} />
          <Route path="/employer/post-job" element={<EmployerPostJobPage />} />
          <Route path="/employer/review-applications" element={<EmployerReviewApplicationsPage />} />
          <Route path="*" element={<LandingPage />} />
        </Routes>
        <SiteFooter />
      </div>
    </BrowserRouter>
  </React.StrictMode>
);
