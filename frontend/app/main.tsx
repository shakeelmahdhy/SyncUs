import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router';
import './styles.css';
import { ApplicationsPage } from './pages/ApplicationsPage';
import { JobDetailPage } from './pages/JobsDetailPage';
import { LandingPage } from './pages/LandingPage';
import { ProfilePage } from './pages/ProfilePage';
import { SiteFooter, SiteNav } from './shared/components';
import TalentPoolPage from './pages/TalentPoolPage';
import DashboardPage from './pages/DashboardPage';
import { HiringTeamPage } from './pages/employer/HiringTeamPage';
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
          <Route path="/talent-pool" element={<TalentPoolPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/hiring-team" element={<HiringTeamPage />} />
          <Route path="*" element={<LandingPage />} />
        </Routes>
        <SiteFooter />
      </div>
    </BrowserRouter>
  </React.StrictMode>
);
