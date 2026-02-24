import { useState } from 'react';
import Modal from '../ui/Modal';
import DatePicker from '../ui/DatePicker';
import Spinner from '../ui/Spinner';

const INITIAL = {
  first_name: '', last_name: '', email: '', phone: '',
  fitness_level: 'BEGINNER', membership_tier: 'FREE', membership_valid_until: '',
};

export default function CreateMemberModal({ open, onClose, onSubmit, loading }) {
  const [form, setForm] = useState(INITIAL);

  const set = (key, value) => setForm(f => ({ ...f, [key]: value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    const body = { ...form };
    if (!body.membership_valid_until) delete body.membership_valid_until;
    onSubmit(body);
  };

  const handleClose = () => {
    setForm(INITIAL);
    onClose();
  };

  return (
    <Modal open={open} onClose={handleClose} title="NEW MEMBER" width={540}>
      <form onSubmit={handleSubmit} className="form-section">
        <div className="form-section-title">Personal Info</div>

        <div className="form-grid">
          <div className="form-field">
            <label className="form-label">First Name *</label>
            <input
              required
              value={form.first_name}
              onChange={e => set('first_name', e.target.value)}
              placeholder="John"
              autoFocus
            />
          </div>
          <div className="form-field">
            <label className="form-label">Last Name *</label>
            <input
              required
              value={form.last_name}
              onChange={e => set('last_name', e.target.value)}
              placeholder="Doe"
            />
          </div>
          <div className="form-field">
            <label className="form-label">Email *</label>
            <input
              required
              type="email"
              value={form.email}
              onChange={e => set('email', e.target.value)}
              placeholder="john@example.com"
            />
          </div>
          <div className="form-field">
            <label className="form-label">Phone</label>
            <input
              value={form.phone}
              onChange={e => set('phone', e.target.value)}
              placeholder="+48 123 456 789"
            />
          </div>
        </div>

        <div className="form-section-title">Membership</div>

        <div className="form-grid">
          <div className="form-field">
            <label className="form-label">Fitness Level</label>
            <select value={form.fitness_level} onChange={e => set('fitness_level', e.target.value)}>
              {['BEGINNER', 'INTERMEDIATE', 'ADVANCED'].map(v => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
          </div>
          <div className="form-field">
            <label className="form-label">Membership Tier</label>
            <select value={form.membership_tier} onChange={e => set('membership_tier', e.target.value)}>
              {['FREE', 'PREMIUM', 'VIP'].map(v => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
          </div>
          <div className="form-field form-full">
            <label className="form-label">Valid Until</label>
            <DatePicker
              value={form.membership_valid_until}
              onChange={v => set('membership_valid_until', v)}
              placeholder="No expiry date"
            />
          </div>
        </div>

        <div className="btn-row" style={{ justifyContent: 'flex-end', marginTop: 4 }}>
          <button type="button" className="btn btn-ghost" onClick={handleClose} disabled={loading}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
            {loading ? <Spinner size={14} color="#000" /> : null}
            Create Member
          </button>
        </div>
      </form>
    </Modal>
  );
}
