import { useState, useCallback } from 'react';
import { api } from '../../api/client';
import { useAsync } from '../../hooks/useAsync';
import { useToast } from '../../contexts/ToastContext';
import Modal from '../ui/Modal';
import DatePicker from '../ui/DatePicker';
import Badge from '../ui/Badge';
import ProgressRing from '../ui/ProgressRing';
import StatCard from '../ui/StatCard';
import Spinner from '../ui/Spinner';

const EMPTY_EX = { name: '', sets: 3, reps: 10, rest_seconds: 60 };

function CreatePlanModal({ open, onClose, onSubmit, loading }) {
  const [form, setForm] = useState({
    member_id: '', coach_id: '', name: '', starts_at: '', ends_at: '',
  });

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...form,
      member_id: Number(form.member_id),
      coach_id: Number(form.coach_id),
    });
  };

  const handleClose = () => {
    setForm({ member_id: '', coach_id: '', name: '', starts_at: '', ends_at: '' });
    onClose();
  };

  return (
    <Modal open={open} onClose={handleClose} title="NEW TRAINING PLAN" width={520}>
      <form onSubmit={handleSubmit} className="form-section">
        <div className="form-section-title">Participants</div>
        <div className="form-grid">
          <div className="form-field">
            <label className="form-label">Member ID *</label>
            <input
              required type="number" min={1}
              value={form.member_id}
              onChange={e => set('member_id', e.target.value)}
              placeholder="e.g. 3"
              autoFocus
            />
          </div>
          <div className="form-field">
            <label className="form-label">Coach ID *</label>
            <input
              required type="number" min={1}
              value={form.coach_id}
              onChange={e => set('coach_id', e.target.value)}
              placeholder="e.g. 1"
            />
          </div>
        </div>

        <div className="form-section-title">Plan Details</div>
        <div className="form-grid">
          <div className="form-field form-full">
            <label className="form-label">Plan Name *</label>
            <input
              required
              value={form.name}
              onChange={e => set('name', e.target.value)}
              placeholder="e.g. Summer Shred 2025"
            />
          </div>
          <div className="form-field">
            <label className="form-label">Start Date *</label>
            <DatePicker
              value={form.starts_at}
              onChange={v => set('starts_at', v)}
              placeholder="Pick start date"
            />
          </div>
          <div className="form-field">
            <label className="form-label">End Date *</label>
            <DatePicker
              value={form.ends_at}
              onChange={v => set('ends_at', v)}
              placeholder="Pick end date"
            />
          </div>
        </div>

        <div className="btn-row" style={{ justifyContent: 'flex-end', marginTop: 4 }}>
          <button type="button" className="btn btn-ghost" onClick={handleClose} disabled={loading}>
            Cancel
          </button>
          <button
            type="submit"
            className="btn btn-primary btn-lg"
            disabled={loading || !form.starts_at || !form.ends_at}
          >
            {loading && <Spinner size={14} color="#000" />}
            Create Plan
          </button>
        </div>
      </form>
    </Modal>
  );
}

function AddSessionModal({ open, onClose, onSubmit, loading }) {
  const [form, setForm] = useState({ name: '', scheduled_date: '', exercises: [{ ...EMPTY_EX }] });

  const setField = (k, v) => setForm(f => ({ ...f, [k]: v }));
  const setEx = (i, k, v) => setForm(f => ({
    ...f,
    exercises: f.exercises.map((e, idx) => idx === i ? { ...e, [k]: v } : e),
  }));
  const addEx = () => setForm(f => ({ ...f, exercises: [...f.exercises, { ...EMPTY_EX }] }));
  const removeEx = (i) => setForm(f => ({ ...f, exercises: f.exercises.filter((_, idx) => idx !== i) }));

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...form,
      exercises: form.exercises.map(ex => ({
        ...ex,
        sets: Number(ex.sets),
        reps: Number(ex.reps),
        rest_seconds: Number(ex.rest_seconds),
      })),
    });
  };

  const handleClose = () => {
    setForm({ name: '', scheduled_date: '', exercises: [{ ...EMPTY_EX }] });
    onClose();
  };

  return (
    <Modal open={open} onClose={handleClose} title="ADD SESSION" width={600}>
      <form onSubmit={handleSubmit} className="form-section">
        <div className="form-grid">
          <div className="form-field">
            <label className="form-label">Session Name *</label>
            <input
              required
              value={form.name}
              onChange={e => setField('name', e.target.value)}
              placeholder="e.g. Leg Day A"
              autoFocus
            />
          </div>
          <div className="form-field">
            <label className="form-label">Scheduled Date *</label>
            <DatePicker
              value={form.scheduled_date}
              onChange={v => setField('scheduled_date', v)}
              placeholder="Pick a date"
            />
          </div>
        </div>

        <div className="form-section-title">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Exercises ({form.exercises.length})</span>
            <button type="button" className="btn btn-secondary btn-sm" onClick={addEx}>
              + Add Exercise
            </button>
          </div>
        </div>

        <div className="ex-editor">
          {/* Header row */}
          <div className="ex-row" style={{ paddingBottom: 4, borderBottom: '1px solid var(--border)' }}>
            <span className="form-label" style={{ fontSize: 9 }}>Exercise Name</span>
            <span className="form-label" style={{ fontSize: 9, textAlign: 'center' }}>Sets</span>
            <span className="form-label" style={{ fontSize: 9, textAlign: 'center' }}>Reps</span>
            <span className="form-label" style={{ fontSize: 9, textAlign: 'center' }}>Rest (s)</span>
            <span />
          </div>

          {form.exercises.map((ex, i) => (
            <div key={i} className="ex-row">
              <input
                required
                placeholder="e.g. Barbell Squat"
                value={ex.name}
                onChange={e => setEx(i, 'name', e.target.value)}
              />
              <input
                type="number" min={1} max={99}
                value={ex.sets}
                onChange={e => setEx(i, 'sets', e.target.value)}
                style={{ textAlign: 'center' }}
              />
              <input
                type="number" min={1} max={999}
                value={ex.reps}
                onChange={e => setEx(i, 'reps', e.target.value)}
                style={{ textAlign: 'center' }}
              />
              <input
                type="number" min={0} max={600}
                value={ex.rest_seconds}
                onChange={e => setEx(i, 'rest_seconds', e.target.value)}
                style={{ textAlign: 'center' }}
              />
              <button
                type="button"
                className="btn-icon btn-icon--danger"
                onClick={() => removeEx(i)}
                disabled={form.exercises.length === 1}
                aria-label="Remove exercise"
              >
                <svg viewBox="0 0 10 10" fill="none" width="9">
                  <path d="M1 1l8 8M9 1L1 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                </svg>
              </button>
            </div>
          ))}
        </div>

        <div className="btn-row" style={{ justifyContent: 'flex-end' }}>
          <button type="button" className="btn btn-ghost" onClick={handleClose} disabled={loading}>
            Cancel
          </button>
          <button
            type="submit"
            className="btn btn-primary btn-lg"
            disabled={loading || !form.scheduled_date}
          >
            {loading && <Spinner size={14} color="#000" />}
            Add Session
          </button>
        </div>
      </form>
    </Modal>
  );
}

function CompleteSessionModal({ session, onClose, onSubmit, loading }) {
  const [notes, setNotes] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(session.id, notes ? { notes } : {});
  };

  const handleClose = () => { setNotes(''); onClose(); };

  return (
    <Modal open={!!session} onClose={handleClose} title="COMPLETE SESSION" width={420}>
      <form onSubmit={handleSubmit} className="form-section">
        <div style={{ padding: '10px 12px', background: 'var(--surface)', border: '1px solid var(--border)' }}>
          <div style={{ fontWeight: 600, color: 'var(--text)' }}>{session?.name}</div>
          <div style={{ fontSize: 11, color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', marginTop: 2 }}>
            {session?.scheduled_date} · #{session?.id}
          </div>
        </div>

        <div className="form-field">
          <label className="form-label">Session Notes (optional)</label>
          <textarea
            value={notes}
            onChange={e => setNotes(e.target.value)}
            placeholder="How did it go? Any observations…"
            autoFocus
          />
        </div>

        <div className="btn-row" style={{ justifyContent: 'flex-end' }}>
          <button type="button" className="btn btn-ghost" onClick={handleClose} disabled={loading}>
            Cancel
          </button>
          <button type="submit" className="btn btn-success btn-lg" disabled={loading}>
            {loading && <Spinner size={14} color="var(--success)" />}
            Mark Complete
          </button>
        </div>
      </form>
    </Modal>
  );
}

export default function PlansTab() {
  const { loading, error, run, getLastError } = useAsync();
  const toast = useToast();

  const [plan, setPlan] = useState(null);
  const [progress, setProgress] = useState(null);
  const [planIdInput, setPlanIdInput] = useState('');
  const [createOpen, setCreateOpen] = useState(false);
  const [addSessionOpen, setAddSessionOpen] = useState(false);
  const [completingSession, setCompletingSession] = useState(null);

  const loadPlan = useCallback(async (id) => {
    const pid = id ?? planIdInput;
    if (!pid) return;
    const data = await run(() => api.getPlan(pid));
    if (data) {
      setPlan(data);
      setProgress(null);
    } else {
      const err = getLastError();
      if (err) toast.error(err);
    }
  }, [run, planIdInput, getLastError, toast]);

  const handleCreate = async (formData) => {
    const data = await run(() => api.createPlan(formData));
    if (data) {
      toast.success(`Plan "${data.name}" created (ID: ${data.id}).`);
      setPlan(data);
      setPlanIdInput(String(data.id));
      setCreateOpen(false);
    } else {
      const err = getLastError();
      if (err) toast.error(err);
    }
  };

  const handleActivate = async () => {
    if (!plan) return;
    const data = await run(() => api.activatePlan(plan.id));
    if (data) {
      setPlan(data);
      toast.success(`Plan "${data.name}" activated.`);
    } else {
      const err = getLastError();
      if (err) toast.error(err);
    }
  };

  const handleProgress = async () => {
    if (!plan) return;
    const data = await run(() => api.getPlanProgress(plan.id));
    if (data) {
      setProgress(data);
    } else {
      const err = getLastError();
      if (err) toast.error(err);
    }
  };

  const handleAddSession = async (sessionData) => {
    const data = await run(() => api.addSession(plan.id, sessionData));
    if (data) {
      setPlan(data);
      setAddSessionOpen(false);
      toast.success('Session added.');
    } else {
      const err = getLastError();
      if (err) toast.error(err);
    }
  };

  const handleCompleteSession = async (sessionId, body) => {
    const data = await run(() => api.completeSession(plan.id, sessionId, body));
    if (data) {
      setPlan(data);
      setCompletingSession(null);
      toast.success('Session completed!');
      // Auto-fetch progress after completing
      const prog = await run(() => api.getPlanProgress(plan.id));
      if (prog) setProgress(prog);
    } else {
      const err = getLastError();
      if (err) toast.error(err);
    }
  };

  const pendingCount  = plan?.sessions?.filter(s => s.status === 'PENDING').length ?? 0;
  const doneCount     = plan?.sessions?.filter(s => s.status === 'COMPLETED').length ?? 0;
  const totalSessions = plan?.sessions?.length ?? 0;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Plans</h1>
          {plan && (
            <p className="page-subtitle">
              {plan.name} · {plan.status} · Member #{plan.member_id} → Coach #{plan.coach_id}
            </p>
          )}
        </div>
        <div className="page-actions">
          {loading && <Spinner />}
          <button className="btn btn-primary" onClick={() => setCreateOpen(true)}>
            + Create Plan
          </button>
        </div>
      </div>

      {error && <div className="error-block">{error}</div>}

      {/* Plan lookup / actions */}
      <div style={{
        background: 'var(--card)',
        border: '1px solid var(--border)',
        padding: '14px 16px',
        display: 'flex',
        flexWrap: 'wrap',
        gap: 10,
        alignItems: 'flex-end',
      }}>
        <div className="form-field" style={{ flex: '0 0 140px' }}>
          <label className="form-label">Plan ID</label>
          <input
            type="number"
            min={1}
            placeholder="e.g. 5"
            value={planIdInput}
            onChange={e => setPlanIdInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && loadPlan()}
          />
        </div>
        <div className="btn-row">
          <button
            className="btn btn-secondary"
            onClick={() => loadPlan()}
            disabled={loading || !planIdInput}
          >
            Load
          </button>
          <button
            className="btn btn-primary"
            onClick={handleActivate}
            disabled={loading || !plan || plan.status !== 'DRAFT'}
          >
            Activate
          </button>
          <button
            className="btn btn-secondary"
            onClick={handleProgress}
            disabled={loading || !plan}
          >
            Refresh Progress
          </button>
          {plan && plan.status === 'ACTIVE' && (
            <button
              className="btn btn-success"
              onClick={() => setAddSessionOpen(true)}
              disabled={loading}
            >
              + Add Session
            </button>
          )}
          {plan && plan.status === 'DRAFT' && (
            <button
              className="btn btn-success"
              onClick={() => setAddSessionOpen(true)}
              disabled={loading}
            >
              + Add Session
            </button>
          )}
        </div>
      </div>

      {/* Plan detail */}
      {plan && (
        <div className="plan-detail">
          <div className="plan-detail-header">
            <div className="plan-detail-meta">
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                <h2 className="plan-detail-title">{plan.name}</h2>
                <Badge>{plan.status}</Badge>
                <span className="id-chip">#{plan.id}</span>
              </div>
              <div className="plan-detail-info" style={{ marginTop: 6 }}>
                {plan.starts_at} → {plan.ends_at}
                &nbsp;·&nbsp; Member #{plan.member_id}
                &nbsp;·&nbsp; Coach #{plan.coach_id}
              </div>
            </div>

            {/* Progress ring */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
              {progress && (
                <ProgressRing
                  pct={progress.completion_pct}
                  size={84}
                  stroke={6}
                  color={progress.completion_pct >= 100 ? 'var(--success)' : 'var(--accent)'}
                  sublabel="done"
                />
              )}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <StatCard label="Sessions" value={totalSessions} />
                <StatCard label="Done" value={doneCount} color="var(--success)" />
                <StatCard label="Pending" value={pendingCount} color="var(--warning)" />
              </div>
            </div>
          </div>

          {plan.sessions?.length === 0 && (
            <div className="empty-state" style={{ padding: '24px 0' }}>
              <div className="empty-icon">📋</div>
              <div className="empty-text">No sessions yet</div>
              <div className="empty-sub">
                {plan.status === 'DRAFT' || plan.status === 'ACTIVE'
                  ? 'Use "+ Add Session" to schedule workouts'
                  : 'This plan has no sessions'}
              </div>
            </div>
          )}

          {plan.sessions?.length > 0 && (
            <div className="sessions-list">
              {plan.sessions.map(s => (
                <div
                  key={s.id}
                  className={`session-item ${s.status === 'COMPLETED' ? 'session-item--completed' : ''}`}
                >
                  {/* Status indicator */}
                  <div style={{
                    width: 28,
                    height: 28,
                    border: `2px solid ${s.status === 'COMPLETED' ? 'var(--success)' : 'var(--border-hover)'}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flex: '0 0 auto',
                    color: s.status === 'COMPLETED' ? 'var(--success)' : 'var(--text-dim)',
                    fontSize: 12,
                  }}>
                    {s.status === 'COMPLETED' ? '✓' : '○'}
                  </div>

                  <div className="session-item-info">
                    <div className="session-item-name">
                      <span>{s.name}</span>
                      <Badge>{s.status}</Badge>
                      <span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
                        {s.scheduled_date}
                      </span>
                    </div>

                    {s.notes && (
                      <div className="session-item-notes">"{s.notes}"</div>
                    )}

                    {s.exercises?.length > 0 && (
                      <div className="session-exercises">
                        {s.exercises.map((ex, i) => (
                          <span key={i} className="ex-chip">
                            {ex.name} · {ex.sets}×{ex.reps} · {ex.rest_seconds}s
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {s.status === 'PENDING' && plan.status === 'ACTIVE' && (
                    <button
                      className="btn btn-success btn-sm"
                      onClick={() => setCompletingSession(s)}
                      disabled={loading}
                      style={{ flexShrink: 0 }}
                    >
                      Complete
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {!plan && (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <div className="empty-text">No plan loaded</div>
          <div className="empty-sub">Enter a Plan ID and click Load, or create a new plan</div>
        </div>
      )}

      {/* Modals */}
      <CreatePlanModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onSubmit={handleCreate}
        loading={loading}
      />

      <AddSessionModal
        open={addSessionOpen}
        onClose={() => setAddSessionOpen(false)}
        onSubmit={handleAddSession}
        loading={loading}
      />

      <CompleteSessionModal
        session={completingSession}
        onClose={() => setCompletingSession(null)}
        onSubmit={handleCompleteSession}
        loading={loading}
      />
    </div>
  );
}
