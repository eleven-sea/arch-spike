import Badge from '../ui/Badge';

export default function CoachCard({ coach, onSelect, onDelete, disabled }) {
  const utilPct = coach.max_clients > 0
    ? (coach.current_client_count / coach.max_clients) * 100
    : 0;

  const fillClass =
    utilPct >= 100 ? 'util-bar-fill--full' :
    utilPct >= 75  ? 'util-bar-fill--high' : '';

  return (
    <div
      className={`coach-card ${coach.tier === 'VIP' ? 'coach-card--vip' : ''}`}
      onClick={() => onSelect(coach)}
      role="button"
      tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && onSelect(coach)}
    >
      <div className="coach-card-top">
        <div className="avatar" style={coach.tier === 'VIP' ? { borderColor: 'rgba(255,204,60,.35)', color: 'var(--warning)' } : {}}>
          {coach.first_name?.[0] ?? '?'}{coach.last_name?.[0] ?? '?'}
        </div>
        <div className="coach-card-info">
          <div className="coach-card-name">{coach.first_name} {coach.last_name}</div>
          <div className="coach-card-email">{coach.email}</div>
        </div>
        <button
          className="btn-icon btn-icon--danger"
          onClick={e => { e.stopPropagation(); onDelete(coach.id); }}
          disabled={disabled}
          aria-label="Delete coach"
        >
          <svg viewBox="0 0 12 14" fill="none" width="11" height="13">
            <path d="M1 3h10M4 3V2h4v1M2 3l.5 9h7L10 3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>

      <div className="spec-tags">
        {coach.specializations?.length > 0
          ? coach.specializations.map(s => <span key={s} className="spec-tag">{s}</span>)
          : <span style={{ fontSize: 11, color: 'var(--text-dim)' }}>No specializations</span>
        }
      </div>

      <div className="util-bar-wrap">
        <div className="util-bar-label">
          <span>Client load</span>
          <span>{coach.current_client_count} / {coach.max_clients}</span>
        </div>
        <div className="util-bar">
          <div
            className={`util-bar-fill ${fillClass}`}
            style={{ width: `${Math.min(utilPct, 100)}%` }}
          />
        </div>
      </div>

      <div style={{ display: 'flex', gap: 5 }}>
        <Badge>{coach.tier}</Badge>
      </div>
    </div>
  );
}
