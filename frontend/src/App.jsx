import { useState, useEffect } from 'react';
import { ToastProvider } from './contexts/ToastContext';
import MembersTab from './components/members/MembersTab';
import CoachesTab from './components/coaches/CoachesTab';
import PlansTab from './components/plans/PlansTab';
import './App.css';

const TABS = [
  {
    id: 'Members',
    label: 'Members',
    icon: (
      <svg viewBox="0 0 16 16" fill="none" width="16" height="16">
        <circle cx="8" cy="5" r="3" stroke="currentColor" strokeWidth="1.4"/>
        <path d="M2 14c0-3.314 2.686-6 6-6s6 2.686 6 6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
      </svg>
    ),
  },
  {
    id: 'Coaches',
    label: 'Coaches',
    icon: (
      <svg viewBox="0 0 16 16" fill="none" width="16" height="16">
        <circle cx="6" cy="5" r="2.5" stroke="currentColor" strokeWidth="1.4"/>
        <path d="M1 13c0-2.76 2.24-5 5-5s5 2.24 5 5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
        <path d="M11 7l1.5 1.5L15 6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
  },
  {
    id: 'Plans',
    label: 'Plans',
    icon: (
      <svg viewBox="0 0 16 16" fill="none" width="16" height="16">
        <rect x="2" y="2" width="12" height="12" rx="1" stroke="currentColor" strokeWidth="1.4"/>
        <path d="M5 8l2 2 4-4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
  },
];

function useTabCounts() {
  return {};
}

export default function App() {
  const [tab, setTab] = useState('Members');
  const [counts, setCounts] = useState({});

  // Keyboard shortcuts: m = Members, c = Coaches, p = Plans
  useEffect(() => {
    const handler = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
      if (e.key === 'm') setTab('Members');
      if (e.key === 'c') setTab('Coaches');
      if (e.key === 'p') setTab('Plans');
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, []);

  return (
    <ToastProvider>
      <div className="app-layout">
        <aside className="sidebar">
          <div className="sidebar-brand">
            <div className="brand-logo">⚡</div>
            <div className="brand-text-wrap">
              <span className="brand-name">IRON</span>
              <span className="brand-sub">Training Studio</span>
            </div>
          </div>

          <nav className="sidebar-nav">
            {TABS.map(t => (
              <button
                key={t.id}
                className={`nav-item ${tab === t.id ? 'nav-item--active' : ''}`}
                onClick={() => setTab(t.id)}
                title={`${t.label} (${t.id[0].toLowerCase()})`}
              >
                <span className="nav-icon">{t.icon}</span>
                <span className="nav-label">{t.label}</span>
                {counts[t.id] != null && (
                  <span className="nav-badge">{counts[t.id]}</span>
                )}
              </button>
            ))}
          </nav>

          <div className="sidebar-footer">
            <div className="api-status">
              <span className="api-dot" />
              <span>localhost:8000</span>
            </div>
            <div style={{ marginTop: 8, fontSize: 10, color: 'var(--text-dim)', letterSpacing: '0.05em' }}>
              m · c · p shortcuts
            </div>
          </div>
        </aside>

        <main className="app-main">
          {tab === 'Members' && <MembersTab onCountChange={n => setCounts(c => ({ ...c, Members: n }))} />}
          {tab === 'Coaches' && <CoachesTab onCountChange={n => setCounts(c => ({ ...c, Coaches: n }))} />}
          {tab === 'Plans'   && <PlansTab />}
        </main>
      </div>
    </ToastProvider>
  );
}
