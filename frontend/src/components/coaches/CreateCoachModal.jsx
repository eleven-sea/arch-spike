import { useState } from 'react';
import Modal from '../ui/Modal';
import Spinner from '../ui/Spinner';

const ALL_SPECS = ['STRENGTH', 'CARDIO', 'YOGA', 'CROSSFIT', 'NUTRITION'];

const INITIAL = {
  first_name: '', last_name: '', email: '', bio: '',
  tier: 'STANDARD', specializations: [], max_clients: 10,
};

export default function CreateCoachModal({ open, onClose, onSubmit, loading }) {
  const [form, setForm] = useState(INITIAL);

  const set = (key, value) => setForm(f => ({ ...f, [key]: value }));

  const toggleSpec = (s) => setForm(f => ({
    ...f,
    specializations: f.specializations.includes(s)
      ? f.specializations.filter(x => x !== s)
      : [...f.specializations, s],
  }));

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ ...form, max_clients: Number(form.max_clients) });
  };

  const handleClose = () => {
    setForm(INITIAL);
    onClose();
  };

  return (
    <Modal open={open} onClose={handleClose} title="NEW COACH" width={560}>
      <form onSubmit={handleSubmit} className="form-section">
        <div className="form-section-title">Personal Info</div>

        <div className="form-grid">
          <div className="form-field">
            <label className="form-label">First Name *</label>
            <input
              required
              value={form.first_name}
              onChange={e => set('first_name', e.target.value)}
              placeholder="Sarah"
              autoFocus
            />
          </div>
          <div className="form-field">
            <label className="form-label">Last Name *</label>
            <input
              required
              value={form.last_name}
              onChange={e => set('last_name', e.target.value)}
              placeholder="Connor"
            />
          </div>
          <div className="form-field">
            <label className="form-label">Email *</label>
            <input
              required
              type="email"
              value={form.email}
              onChange={e => set('email', e.target.value)}
              placeholder="coach@gym.com"
            />
          </div>
          <div className="form-field">
            <label className="form-label">Max Clients</label>
            <input
              type="number"
              min={1}
              max={100}
              value={form.max_clients}
              onChange={e => set('max_clients', e.target.value)}
            />
          </div>
          <div className="form-field form-full">
            <label className="form-label">Bio</label>
            <textarea
              value={form.bio}
              onChange={e => set('bio', e.target.value)}
              placeholder="Short bio or speciality description…"
            />
          </div>
        </div>

        <div className="form-section-title">Settings</div>

        <div className="form-grid">
          <div className="form-field">
            <label className="form-label">Tier</label>
            <select value={form.tier} onChange={e => set('tier', e.target.value)}>
              {['STANDARD', 'VIP'].map(v => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>
          <div className="form-field form-full">
            <label className="form-label">Specializations</label>
            <div className="checkbox-wrap">
              {ALL_SPECS.map(s => (
                <label
                  key={s}
                  className={`checkbox-tag ${form.specializations.includes(s) ? 'checkbox-tag--checked' : ''}`}
                >
                  <input
                    type="checkbox"
                    checked={form.specializations.includes(s)}
                    onChange={() => toggleSpec(s)}
                  />
                  {s}
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="btn-row" style={{ justifyContent: 'flex-end', marginTop: 4 }}>
          <button type="button" className="btn btn-ghost" onClick={handleClose} disabled={loading}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
            {loading && <Spinner size={14} color="#000" />}
            Create Coach
          </button>
        </div>
      </form>
    </Modal>
  );
}
