export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

export class ApiClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async request(path, options = {}) {
    const res = await fetch(`${this.baseUrl}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    if (res.status === 204) return null;
    const data = await res.json();
    if (!res.ok) {
      const detail = data?.detail ?? data;
      const msg = typeof detail === 'string' ? detail : JSON.stringify(detail, null, 2);
      throw new ApiError(msg, res.status, data);
    }
    return data;
  }

  // ─── Members ────────────────────────────────────────────────────────────────
  // Trailing slashes on collection endpoints to avoid FastAPI 307 redirects
  getMembers()             { return this.request('/members/'); }
  getMember(id)            { return this.request(`/members/${id}`); }
  createMember(body)       { return this.request('/members/', { method: 'POST', body: JSON.stringify(body) }); }
  async deleteMember(id)   { await this.request(`/members/${id}`, { method: 'DELETE' }); return true; }
  addGoal(memberId, body)  { return this.request(`/members/${memberId}/goals`, { method: 'POST', body: JSON.stringify(body) }); }

  // ─── Coaches ─────────────────────────────────────────────────────────────
  getCoaches(specialization) {
    const qs = specialization ? `?specialization=${specialization}` : '';
    return this.request(`/coaches/${qs}`);
  }
  getCoach(id)            { return this.request(`/coaches/${id}`); }
  createCoach(body)       { return this.request('/coaches/', { method: 'POST', body: JSON.stringify(body) }); }
  async deleteCoach(id)   { await this.request(`/coaches/${id}`, { method: 'DELETE' }); return true; }
  matchCoach(memberId)    { return this.request(`/coaches/match?member_id=${memberId}`); }

  // ─── Plans ───────────────────────────────────────────────────────────────
  createPlan(body)         { return this.request('/plans/', { method: 'POST', body: JSON.stringify(body) }); }
  getPlan(id)              { return this.request(`/plans/${id}`); }
  activatePlan(id)         { return this.request(`/plans/${id}/activate`, { method: 'POST' }); }
  getPlanProgress(id)      { return this.request(`/plans/${id}/progress`); }
  addSession(planId, body) {
    return this.request(`/plans/${planId}/sessions`, { method: 'POST', body: JSON.stringify(body) });
  }
  completeSession(planId, sessionId, body) {
    return this.request(`/plans/${planId}/sessions/${sessionId}/complete`, {
      method: 'POST', body: JSON.stringify(body),
    });
  }
}

export const api = new ApiClient();
