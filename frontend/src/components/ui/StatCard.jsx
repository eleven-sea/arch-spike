export default function StatCard({ label, value, sub, accent = false, icon, color }) {
  return (
    <div className={`stat-card ${accent ? 'stat-card--accent' : ''}`} style={color ? { '--stat-accent': color } : undefined}>
      {icon && <div className="stat-icon">{icon}</div>}
      <div className="stat-value">{value ?? '—'}</div>
      <div className="stat-label">{label}</div>
      {sub != null && <div className="stat-sub">{sub}</div>}
    </div>
  );
}
