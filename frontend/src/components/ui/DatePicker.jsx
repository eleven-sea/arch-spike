import { useState, useRef, useEffect } from 'react';
import './DatePicker.css';

const WEEKDAYS = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];
const MONTHS = [
  'January','February','March','April','May','June',
  'July','August','September','October','November','December',
];

function parseISO(str) {
  if (!str) return null;
  const d = new Date(str + 'T00:00:00');
  return isNaN(d.getTime()) ? null : d;
}

function toISO(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function formatDisplay(date) {
  return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

function getFirstWeekday(year, month) {
  // 0 = Monday
  return (new Date(year, month, 1).getDay() + 6) % 7;
}

function getDaysInMonth(year, month) {
  return new Date(year, month + 1, 0).getDate();
}

export default function DatePicker({ value, onChange, placeholder = 'Pick a date' }) {
  const today = new Date();
  const selected = parseISO(value);

  const [open, setOpen] = useState(false);
  const [viewYear, setViewYear] = useState(selected?.getFullYear() ?? today.getFullYear());
  const [viewMonth, setViewMonth] = useState(selected?.getMonth() ?? today.getMonth());

  const containerRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  const prevMonth = () => {
    if (viewMonth === 0) { setViewYear(y => y - 1); setViewMonth(11); }
    else setViewMonth(m => m - 1);
  };

  const nextMonth = () => {
    if (viewMonth === 11) { setViewYear(y => y + 1); setViewMonth(0); }
    else setViewMonth(m => m + 1);
  };

  const selectDay = (day) => {
    onChange(toISO(new Date(viewYear, viewMonth, day)));
    setOpen(false);
  };

  const clear = (e) => {
    e.stopPropagation();
    onChange('');
  };

  const goToday = () => {
    setViewYear(today.getFullYear());
    setViewMonth(today.getMonth());
    selectDay(today.getDate());
  };

  const firstWeekday = getFirstWeekday(viewYear, viewMonth);
  const daysInMonth = getDaysInMonth(viewYear, viewMonth);
  const cells = [
    ...Array(firstWeekday).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ];

  const isSelected = (day) =>
    day && selected &&
    selected.getFullYear() === viewYear &&
    selected.getMonth() === viewMonth &&
    selected.getDate() === day;

  const isToday = (day) =>
    day &&
    today.getFullYear() === viewYear &&
    today.getMonth() === viewMonth &&
    today.getDate() === day;

  return (
    <div className="dp" ref={containerRef}>
      <button
        type="button"
        className={`dp-trigger ${open ? 'dp-trigger--open' : ''} ${value ? 'dp-trigger--filled' : ''}`}
        onClick={() => setOpen(o => !o)}
      >
        <svg className="dp-icon" viewBox="0 0 16 16" fill="none" width="14" height="14">
          <rect x="1.5" y="3" width="13" height="11.5" rx="1" stroke="currentColor" strokeWidth="1.4"/>
          <path d="M1.5 7h13" stroke="currentColor" strokeWidth="1.4"/>
          <path d="M5 1.5v3M11 1.5v3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
        </svg>
        <span className={value ? 'dp-value' : 'dp-placeholder'}>
          {value ? formatDisplay(selected) : placeholder}
        </span>
        {value && (
          <span className="dp-clear" onClick={clear} role="button" aria-label="Clear date">
            <svg viewBox="0 0 10 10" fill="none" width="10" height="10">
              <path d="M1.5 1.5l7 7M8.5 1.5l-7 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </span>
        )}
        <svg className={`dp-chevron ${open ? 'dp-chevron--up' : ''}`} viewBox="0 0 10 6" fill="none" width="10">
          <path d="M1 1l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>

      {open && (
        <div className="dp-popup">
          <div className="dp-header">
            <button type="button" className="dp-nav-btn" onClick={prevMonth} aria-label="Previous month">
              <svg viewBox="0 0 8 12" fill="none" width="8" height="12">
                <path d="M7 1L1 6l6 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            <span className="dp-month">{MONTHS[viewMonth]} {viewYear}</span>
            <button type="button" className="dp-nav-btn" onClick={nextMonth} aria-label="Next month">
              <svg viewBox="0 0 8 12" fill="none" width="8" height="12">
                <path d="M1 1l6 5-6 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>

          <div className="dp-grid">
            {WEEKDAYS.map(d => (
              <div key={d} className="dp-weekday">{d}</div>
            ))}
            {cells.map((day, i) => (
              <button
                key={i}
                type="button"
                className={[
                  'dp-day',
                  !day ? 'dp-day--empty' : '',
                  isSelected(day) ? 'dp-day--selected' : '',
                  isToday(day) ? 'dp-day--today' : '',
                ].filter(Boolean).join(' ')}
                onClick={() => day && selectDay(day)}
                disabled={!day}
                tabIndex={day ? 0 : -1}
              >
                {day}
              </button>
            ))}
          </div>

          <div className="dp-footer">
            <button type="button" className="dp-today-btn" onClick={goToday}>Today</button>
          </div>
        </div>
      )}
    </div>
  );
}
