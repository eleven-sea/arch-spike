import { useState } from 'react';
import Modal from '../ui/Modal';
import Badge from '../ui/Badge';
import DatePicker from '../ui/DatePicker';
import Spinner from '../ui/Spinner';

const GOAL_ICONS = {
  LOSE_WEIGHT:  '⚖',
  BUILD_MUSCLE: '💪',
  ENDURANCE:    '🏃',
  FLEXIBILITY:  '🤸',
};

const INITIAL_GOAL = { goal_type: 'LOSE_WEIGHT', description: '', target_date: '' };

export default function MemberDetailModal({ member, open, onClose, onDelete, onAddGoal, loading }) {
  const [goalForm, setGoalForm] = useState(INITIAL_GOAL);
  const [addingGoal, setAddingGoal] = useState(false);

  if (!member) return null;

  const setGoal = (key, value) => setGoalForm(f => ({ ...f, [key]: value }));

  const handleAddGoal = async (e) => {
    e.preventDefault();
    const body = { ...goalForm };
    if (!body.target_date) delete body.target_date;
    await onAddGoal(member.id, body);
    setGoalForm(INITIAL_GOAL);
    setAddingGoal(false);
  };

  const handleDelete = () => {
    if (confirm(`Delete member ${member.first_name} ${member.last_name}?`)) {
      onDelete(member.id);
      onClose();
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={`${member.first_name} ${member.last_name}`.toUpperCase()} width={560}>
      <div className="form-section">

        {/* Identity */}
        <div className="form-section-title">Profile</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <div>
            <div className="form-label">Email</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
              {member.email}
            </div>
          </div>
          <div>
            <div className="form-label">Phone</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
              {member.phone || '—'}
            </div>
          </div>
          <div>
            <div className="form-label">Fitness Level</div>
            <div style={{ marginTop: 4 }}><Badge>{member.fitness_level}</Badge></div>
          </div>
          <div>
            <div className="form-label">Membership</div>
            <div style={{ marginTop: 4, display: 'flex', gap: 6, alignItems: 'center' }}>
              <Badge>{member.membership_tier}</Badge>
              {member.active_plan_id && (
                <span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--cyan)' }}>
                  Plan #{member.active_plan_id}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Goals */}
        <div className="form-section-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Goals ({member.goals?.length ?? 0})</span>
          {!addingGoal && (
            <button
              className="btn btn-sm btn-secondary"
              onClick={() => setAddingGoal(true)}
              style={{ textTransform: 'none', letterSpacing: 0, fontWeight: 500 }}
            >
              + Add Goal
            </button>
          )}
        </div>

        {(!member.goals || member.goals.length === 0) && !addingGoal && (
          <div style={{ color: 'var(--text-dim)', fontSize: 12, fontStyle: 'italic', padding: '8px 0' }}>
            No goals yet.
          </div>
        )}

        {member.goals?.map((g, i) => (
          <div key={i} className="goal-item">
            <div className="goal-item-icon">{GOAL_ICONS[g.goal_type] ?? '🎯'}</div>
            <div className="goal-item-body">
              <div className="goal-type">{g.goal_type.replace(/_/g, ' ')}</div>
              {g.description && <div className="goal-desc">{g.description}</div>}
              {g.target_date && <div className="goal-date">Target: {g.target_date.slice(0, 10)}</div>}
            </div>
            <Badge>{g.goal_type}</Badge>
          </div>
        ))}

        {addingGoal && (
          <form onSubmit={handleAddGoal} className="form-section" style={{ background: 'var(--surface)', padding: 14, border: '1px solid var(--border)' }}>
            <div className="form-grid">
              <div className="form-field">
                <label className="form-label">Goal Type</label>
                <select value={goalForm.goal_type} onChange={e => setGoal('goal_type', e.target.value)}>
                  {['LOSE_WEIGHT', 'BUILD_MUSCLE', 'ENDURANCE', 'FLEXIBILITY'].map(v => (
                    <option key={v} value={v}>{v.replace(/_/g, ' ')}</option>
                  ))}
                </select>
              </div>
              <div className="form-field">
                <label className="form-label">Target Date</label>
                <DatePicker
                  value={goalForm.target_date}
                  onChange={v => setGoal('target_date', v)}
                  placeholder="Optional"
                />
              </div>
              <div className="form-field form-full">
                <label className="form-label">Description</label>
                <input
                  value={goalForm.description}
                  onChange={e => setGoal('description', e.target.value)}
                  placeholder="e.g. Lose 10kg by summer"
                />
              </div>
            </div>
            <div className="btn-row" style={{ justifyContent: 'flex-end' }}>
              <button type="button" className="btn btn-ghost btn-sm" onClick={() => setAddingGoal(false)}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary btn-sm" disabled={loading}>
                {loading && <Spinner size={12} color="#000" />}
                Add Goal
              </button>
            </div>
          </form>
        )}

        {/* Footer actions */}
        <div className="btn-row" style={{ justifyContent: 'space-between', marginTop: 4 }}>
          <button className="btn btn-danger btn-sm" onClick={handleDelete} disabled={loading}>
            Delete Member
          </button>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>
            Close
          </button>
        </div>

      </div>
    </Modal>
  );
}
