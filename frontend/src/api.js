const API_BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/$/, '');

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': options.body instanceof FormData ? undefined : 'application/json',
      ...(options.headers || {})
    }
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Request failed');
  }
  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  register: (email, password) =>
    request('/auth/register', {
      method: 'POST',
      body: new URLSearchParams({ email, password })
    }),
  login: async (email, password) =>
    request('/auth/login', {
      method: 'POST',
      body: new URLSearchParams({ email, password })
    }),
  refresh: (refreshToken) =>
    request('/auth/refresh', {
      method: 'POST',
      body: new URLSearchParams({ refresh_token: refreshToken })
    }),
  listReports: (token) =>
    request('/reports', {
      headers: { Authorization: `Bearer ${token}` }
    }),
  getReport: (id, token) =>
    request(`/reports/${id}`, {
      headers: { Authorization: `Bearer ${token}` }
    }),
  deleteReport: (id, token) =>
    request(`/reports/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    }),
  upload: (file, token) => {
    const formData = new FormData();
    formData.append('file', file);
    return request('/upload', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    });
  }
};
