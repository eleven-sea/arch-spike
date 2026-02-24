import Badge from '../ui/Badge';

const TIER_BORDER = {
  FREE:    'var(--text-dim)',
  PREMIUM: 'var(--cyan)',
  VIP:     'var(--warning)',
};

export default function MemberCard({ member, onSelect, onDelete, disabled }) {
  const accentColor = TIER_BORDER[member.membership_tier] ?? 'var(--text-dim)';

  return (
    <div
      className="member-card"
      style={{ borderLeftColor: accentColor }}
      onClick={() => onSelect(member)}
      role="button"
      tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && onSelect(member)}
    >
      <div className="member-card-top">
        <div className="avatar">
          {member.first_name?.[0] ?? '?'}{member.last_name?.[0] ?? '?'}
        </div>
        <div className="member-card-info">
          <div className="member-card-name">{member.first_name} {member.last_name}</div>
          <div className="member-card-email">{member.email}</div>
        </div>
        <button
          className="btn-icon btn-icon--danger"
          onClick={e => { e.stopPropagation(); onDelete(member.id); }}
          disabled={disabled}
          aria-label="Delete member"
        >
          <svg viewBox="0 0 12 14" fill="none" width="11" height="13">
            <path d="M1 3h10M4 3V2h4v1M2 3l.5 9h7L10 3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>

      <div className="member-card-badges">
        <Badge>{member.fitness_level}</Badge>
        <Badge>{member.membership_tier}</Badge>
      </div>

      <div className="member-card-meta">
        {(member.goals?.length ?? 0) > 0 && (
          <span>{member.goals.length} goal{member.goals.length !== 1 ? 's' : ''}</span>
        )}
        {member.active_plan_id && (
          <span className="member-meta-plan">Plan #{member.active_plan_id}</span>
        )}
        {member.phone && <span>{member.phone}</span>}
      </div>
    </div>
  );
}
