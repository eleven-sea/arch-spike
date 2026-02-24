import { useEffect, useState } from 'react';

export default function ProgressRing({
  pct = 0,
  size = 84,
  stroke = 6,
  color = 'var(--accent)',
  trackColor = 'var(--border)',
  label,
  sublabel,
}) {
  const [animPct, setAnimPct] = useState(0);

  useEffect(() => {
    const raf = requestAnimationFrame(() => setAnimPct(pct));
    return () => cancelAnimationFrame(raf);
  }, [pct]);

  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (Math.min(animPct, 100) / 100) * circ;

  return (
    <div className="progress-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)', display: 'block' }}>
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke={trackColor} strokeWidth={stroke}
        />
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke={color} strokeWidth={stroke}
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="butt"
          style={{ transition: 'stroke-dashoffset 0.9s cubic-bezier(0.16, 1, 0.3, 1)' }}
        />
      </svg>
      <div className="progress-ring-inner">
        <span className="progress-ring-pct">
          {Math.round(animPct)}<small>%</small>
        </span>
        {sublabel && <span className="progress-ring-sub">{sublabel}</span>}
      </div>
    </div>
  );
}
