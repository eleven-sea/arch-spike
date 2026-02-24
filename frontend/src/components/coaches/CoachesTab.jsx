import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '../../api/client';
import { useAsync } from '../../hooks/useAsync';
import { useToast } from '../../contexts/ToastContext';
import StatCard from '../ui/StatCard';
import Badge from '../ui/Badge';
import Spinner from '../ui/Spinner';
import CoachCard from './CoachCard';
import CreateCoachModal from './CreateCoachModal';

const ALL_SPECS = ['STRENGTH', 'CARDIO', 'YOGA', 'CROSSFIT', 'NUTRITION'];

export default function CoachesTab({ onCountChange }) {
  const { loading, error, run, getLastError } = useAsync();
  const toast = useToast();

  const [coaches, setCoaches] = useState([]);
  const [filterSpec, setFilterSpec] = useState('');
  const [createOpen, setCreateOpen] = useState(false);
  const [selectedCoach, setSelectedCoach] = useState(null);
  const [matchMemberId, setMatchMemberId] = useState('');
  const [matchResult, setMatchResult] = useState(null);
  const [matchLoading, setMatchLoading] = useState(false);

  // Use ref so onCountChange never triggers load re-creation / infinite loop
  const countRef = useRef(onCountChange);
  useEffect(() => { countRef.current = onCountChange; });

  const load = useCallback(async (spec = filterSpec) => {
    const data = await run(() => api.getCoaches(spec || undefined));
    if (data) {
      setCoaches(data);
      countRef.current?.(data.length);
    }
  }, [run, filterSpec]); // ← stable: no onCountChange in deps

  useEffect(() => { load(); }, [load]);

  const handleCreate = async (formData) => {
    const data = await run(() => api.createCoach(formData));
    if (data) {
      toast.success(`Coach ${data.first_name} ${data.last_name} created.`);
      setCreateOpen(false);
      load();
    } else {
      const err = getLastError();
      if (err) toast.error(err);
    }
  };

  const handleDelete = async (id) => {
    const ok = await run(() => api.deleteCoach(id));
    if (ok) {
      toast.success(`Coach #${id} deleted.`);
      if (selectedCoach?.id === id) setSelectedCoach(null);
      load();
    }
  };

  const handleMatch = async () => {
    if (!matchMemberId.trim()) return;
    setMatchLoading(true);
    setMatchResult(null);
    const data = await run(() => api.matchCoach(matchMemberId));
    setMatchLoading(false);
    if (data) {
      setMatchResult(data);
      toast.info(`Best coach: ${data.first_name} ${data.last_name}`);
    } else {
      setMatchResult(null);
      const err = getLastError();
      if (err) toast.error(err);
      else toast.warning('No matching coach found.');
    }
  };

  const available = coaches.filter(c => c.current_client_count < c.max_clients).length;
  const vipCount  = coaches.filter(c => c.tier === 'VIP').length;
  const totalSlots = coaches.reduce((sum, c) => sum + (c.max_clients - c.current_client_count), 0);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Coaches</h1>
          <p className="page-subtitle">{coaches.length} total · {available} available · {totalSlots} open slots</p>
        </div>
        <div className="page-actions">
          {loading && <Spinner />}
          <button className="btn btn-secondary btn-sm" onClick={() => load()} disabled={loading}>
            <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
              <path d="M12 7A5 5 0 1 1 2.4 4.5M2 2v3h3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Refresh
          </button>
          <button className="btn btn-primary" onClick={() => setCreateOpen(true)}>
            + Add Coach
          </button>
        </div>
      </div>

      {error && <div className="error-block">{error}</div>}

      <div className="stats-row">
        <StatCard label="Total" value={coaches.length} accent />
        <StatCard label="Available" value={available} color="var(--success)" />
        <StatCard label="VIP" value={vipCount} color="var(--warning)" />
        <StatCard label="Open Slots" value={totalSlots} color="var(--cyan)" />
      </div>

      {/* Match coach panel */}
      <div style={{
        background: 'var(--card)',
        border: '1px solid var(--border)',
        padding: '14px 16px',
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'flex-end',
        gap: 12,
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
          <span className="form-label">
            <svg viewBox="0 0 16 16" fill="none" width="10" height="10" style={{ marginRight: 4 }}>
              <path d="M8 1l1.8 4.2L14 5.6l-3 2.8.7 4.1L8 10.3l-3.7 2.2.7-4.1-3-2.8 4.2-.4L8 1z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/>
            </svg>
            Match Best Coach for Member
          </span>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <input
              style={{ width: 120 }}
              placeholder="Member ID"
              value={matchMemberId}
              onChange={e => setMatchMemberId(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleMatch()}
              type="number"
              min={1}
            />
            <button
              className="btn btn-primary btn-sm"
              onClick={handleMatch}
              disabled={matchLoading || !matchMemberId.trim()}
            >
              {matchLoading ? <Spinner size={12} color="#000" /> : null}
              Find Match
            </button>
          </div>
        </div>

        {matchResult && (
          <div className="match-result" style={{ flex: 1, minWidth: 200 }}>
            <div className="avatar" style={{ borderColor: 'rgba(157,255,60,.35)' }}>
              {matchResult.first_name?.[0]}{matchResult.last_name?.[0]}
            </div>
            <div>
              <div className="match-result-label">Best Match</div>
              <div className="match-result-name">{matchResult.first_name} {matchResult.last_name}</div>
              <div className="match-result-info">
                {matchResult.specializations?.join(', ')} · {matchResult.tier}
                · {matchResult.current_client_count}/{matchResult.max_clients} clients
              </div>
            </div>
            <div style={{ marginLeft: 'auto' }}>
              <Badge>{matchResult.tier}</Badge>
            </div>
          </div>
        )}
      </div>

      {/* Spec filter chips */}
      <div className="filter-chips">
        <button
          className={`filter-chip ${filterSpec === '' ? 'filter-chip--active' : ''}`}
          onClick={() => setFilterSpec('')}
        >
          All
        </button>
        {ALL_SPECS.map(s => (
          <button
            key={s}
            className={`filter-chip ${filterSpec === s ? 'filter-chip--active' : ''}`}
            onClick={() => setFilterSpec(s)}
          >
            {s}
          </button>
        ))}
      </div>

      {coaches.length === 0 && !loading && (
        <div className="empty-state">
          <div className="empty-icon">🏋</div>
          <div className="empty-text">No coaches yet</div>
          <div className="empty-sub">Click "Add Coach" to get started</div>
        </div>
      )}

      <div className="cards-grid">
        {coaches.map(c => (
          <CoachCard
            key={c.id}
            coach={c}
            onSelect={setSelectedCoach}
            onDelete={handleDelete}
            disabled={loading}
          />
        ))}
      </div>

      {/* Simple selected coach info (no separate modal needed) */}
      {selectedCoach && (
        <div style={{
          background: 'var(--card)',
          border: '1px solid var(--border)',
          padding: 20,
          display: 'flex',
          flexDirection: 'column',
          gap: 12,
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
              <div className="avatar avatar--lg"
                style={selectedCoach.tier === 'VIP' ? { borderColor: 'rgba(255,204,60,.35)', color: 'var(--warning)' } : {}}>
                {selectedCoach.first_name?.[0]}{selectedCoach.last_name?.[0]}
              </div>
              <div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: 20, letterSpacing: '0.04em' }}>
                  {selectedCoach.first_name} {selectedCoach.last_name}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: 4 }}>
                  {selectedCoach.email}
                </div>
                <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
                  <Badge>{selectedCoach.tier}</Badge>
                  <span style={{ fontSize: 11, color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                    #{selectedCoach.id}
                  </span>
                </div>
              </div>
            </div>
            <button
              className="btn-icon"
              onClick={() => setSelectedCoach(null)}
              aria-label="Close"
            >
              <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
                <path d="M1 1l10 10M11 1L1 11" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
              </svg>
            </button>
          </div>

          {selectedCoach.bio && (
            <div style={{ fontSize: 13, color: 'var(--text-muted)', fontStyle: 'italic' }}>
              {selectedCoach.bio}
            </div>
          )}

          {selectedCoach.specializations?.length > 0 && (
            <div className="spec-tags">
              {selectedCoach.specializations.map(s => (
                <span key={s} className="spec-tag">{s}</span>
              ))}
            </div>
          )}

          <div className="btn-row">
            <button
              className="btn btn-danger btn-sm"
              onClick={() => {
                if (confirm(`Delete coach ${selectedCoach.first_name} ${selectedCoach.last_name}?`)) {
                  handleDelete(selectedCoach.id);
                  setSelectedCoach(null);
                }
              }}
              disabled={loading}
            >
              Delete Coach
            </button>
          </div>
        </div>
      )}

      <CreateCoachModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onSubmit={handleCreate}
        loading={loading}
      />
    </div>
  );
}
