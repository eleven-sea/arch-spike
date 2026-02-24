import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '../../api/client';
import { useAsync } from '../../hooks/useAsync';
import { useToast } from '../../contexts/ToastContext';
import StatCard from '../ui/StatCard';
import Spinner from '../ui/Spinner';
import MemberCard from './MemberCard';
import CreateMemberModal from './CreateMemberModal';
import MemberDetailModal from './MemberDetailModal';

export default function MembersTab({ onCountChange }) {
  const { loading, error, run, getLastError } = useAsync();
  const toast = useToast();

  const [members, setMembers] = useState([]);
  const [search, setSearch] = useState('');
  const [filterTier, setFilterTier] = useState('');
  const [filterLevel, setFilterLevel] = useState('');
  const [createOpen, setCreateOpen] = useState(false);
  const [detailMember, setDetailMember] = useState(null);

  // Use ref so onCountChange never triggers load re-creation / infinite loop
  const countRef = useRef(onCountChange);
  useEffect(() => { countRef.current = onCountChange; });

  const load = useCallback(async () => {
    const data = await run(() => api.getMembers());
    if (data) {
      setMembers(data);
      countRef.current?.(data.length);
    }
  }, [run]); // ← stable: no onCountChange in deps

  useEffect(() => { load(); }, [load]);

  const handleCreate = async (formData) => {
    const data = await run(() => api.createMember(formData));
    if (data) {
      toast.success(`${data.first_name} ${data.last_name} added.`);
      setCreateOpen(false);
      load();
    } else {
      const err = getLastError();
      if (err) toast.error(err);
    }
  };

  const handleDelete = async (id) => {
    const ok = await run(() => api.deleteMember(id));
    if (ok) {
      toast.success(`Member #${id} deleted.`);
      if (detailMember?.id === id) setDetailMember(null);
      load();
    }
  };

  const handleAddGoal = async (memberId, goalData) => {
    const data = await run(() => api.addGoal(memberId, goalData));
    if (data) {
      toast.success('Goal added successfully.');
      setDetailMember(data);
      setMembers(prev => prev.map(m => m.id === data.id ? data : m));
    } else {
      const err = getLastError();
      if (err) toast.error(err);
    }
  };

  const filtered = members.filter(m => {
    const q = search.toLowerCase();
    const nameMatch = `${m.first_name} ${m.last_name} ${m.email}`.toLowerCase().includes(q);
    const tierMatch = !filterTier || m.membership_tier === filterTier;
    const levelMatch = !filterLevel || m.fitness_level === filterLevel;
    return nameMatch && tierMatch && levelMatch;
  });

  const byTier  = (t) => members.filter(m => m.membership_tier === t).length;
  const withPlan = members.filter(m => m.active_plan_id).length;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Members</h1>
          <p className="page-subtitle">{members.length} total · {withPlan} with active plan</p>
        </div>
        <div className="page-actions">
          {loading && <Spinner />}
          <button className="btn btn-secondary btn-sm" onClick={load} disabled={loading}>
            <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
              <path d="M12 7A5 5 0 1 1 2.4 4.5M2 2v3h3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Refresh
          </button>
          <button className="btn btn-primary" onClick={() => setCreateOpen(true)}>
            + Add Member
          </button>
        </div>
      </div>

      {error && <div className="error-block">{error}</div>}

      <div className="stats-row">
        <StatCard label="Total" value={members.length} accent />
        <StatCard label="Free" value={byTier('FREE')} color="var(--text-dim)" />
        <StatCard label="Premium" value={byTier('PREMIUM')} color="var(--cyan)" />
        <StatCard label="VIP" value={byTier('VIP')} color="var(--warning)" />
        <StatCard label="With Plan" value={withPlan} color="var(--success)" />
      </div>

      <div className="toolbar">
        <div className="search-wrap">
          <svg className="search-icon" viewBox="0 0 16 16" fill="none" width="14" height="14">
            <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.4"/>
            <path d="M11 11l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <input
            className="search-input"
            placeholder="Search by name or email…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <select style={{ width: 'auto' }} value={filterTier} onChange={e => setFilterTier(e.target.value)}>
          <option value="">All tiers</option>
          {['FREE', 'PREMIUM', 'VIP'].map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <select style={{ width: 'auto' }} value={filterLevel} onChange={e => setFilterLevel(e.target.value)}>
          <option value="">All levels</option>
          {['BEGINNER', 'INTERMEDIATE', 'ADVANCED'].map(l => <option key={l} value={l}>{l}</option>)}
        </select>
      </div>

      {filtered.length === 0 && !loading && (
        <div className="empty-state">
          <div className="empty-icon">👤</div>
          <div className="empty-text">
            {members.length === 0 ? 'No members yet' : 'No matches found'}
          </div>
          {members.length === 0 && (
            <div className="empty-sub">Click "Add Member" to get started</div>
          )}
        </div>
      )}

      <div className="cards-grid">
        {filtered.map(m => (
          <MemberCard
            key={m.id}
            member={m}
            onSelect={setDetailMember}
            onDelete={handleDelete}
            disabled={loading}
          />
        ))}
      </div>

      <CreateMemberModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onSubmit={handleCreate}
        loading={loading}
      />

      <MemberDetailModal
        member={detailMember}
        open={!!detailMember}
        onClose={() => setDetailMember(null)}
        onDelete={handleDelete}
        onAddGoal={handleAddGoal}
        loading={loading}
      />
    </div>
  );
}
