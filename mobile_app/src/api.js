const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8080';

async function request(path, { method = 'GET', token, body } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_URL}/mobile${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.error || data.detail || `Error ${res.status}`);
  }
  return data;
}

export const login = (email, password) =>
  request('/login', { method: 'POST', body: { email, password } });

export const register = (name, email, password) =>
  request('/register', { method: 'POST', body: { name, email, password } });

export const me = (token) => request('/me', { token });

export const logout = (token) => request('/logout', { method: 'POST', token });

export const listTickets = (token) => request('/tickets', { token });

export const createTicket = (token, { title, body, priority, photo_base64 }) =>
  request('/tickets', { method: 'POST', token, body: { title, body, priority, photo_base64 } });

export const uploadResolutionPhoto = (token, ticketId, photo_base64) =>
  request(`/tickets/${ticketId}/resolution-photo`, { method: 'POST', token, body: { photo_base64 } });
