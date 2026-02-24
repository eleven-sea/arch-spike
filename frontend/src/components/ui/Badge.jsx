const VARIANT_MAP = {
  // Fitness levels
  BEGINNER:     'badge--beginner',
  INTERMEDIATE: 'badge--intermediate',
  ADVANCED:     'badge--advanced',
  // Membership / Coach tier
  FREE:         'badge--free',
  PREMIUM:      'badge--premium',
  VIP:          'badge--vip',
  STANDARD:     'badge--standard',
  // Plan status
  DRAFT:        'badge--draft',
  ACTIVE:       'badge--active',
  COMPLETED:    'badge--completed',
  CANCELLED:    'badge--cancelled',
  // Session status
  PENDING:      'badge--pending',
  SKIPPED:      'badge--skipped',
  // Goal types
  LOSE_WEIGHT:  'badge--goal',
  BUILD_MUSCLE: 'badge--goal',
  ENDURANCE:    'badge--goal',
  FLEXIBILITY:  'badge--goal',
};

export default function Badge({ children, variant }) {
  const cls = variant
    ? `badge ${VARIANT_MAP[variant] ?? 'badge--default'}`
    : `badge ${VARIANT_MAP[String(children)] ?? 'badge--default'}`;
  return <span className={cls}>{children}</span>;
}
