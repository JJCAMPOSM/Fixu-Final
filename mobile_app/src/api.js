const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://167.172.144.30:8080';

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

export const createTicket = (token, { title, body, priority, building, classroom, equipment_type, photo_base64 }) =>
  request('/tickets', { method: 'POST', token, body: { title, body, priority, building, classroom, equipment_type, photo_base64 } });

export const uploadResolutionPhoto = (token, ticketId, photo_base64) =>
  request(`/tickets/${ticketId}/resolution-photo`, { method: 'POST', token, body: { photo_base64 } });

export const cancelTicket = (token, ticketId) =>
  request(`/tickets/${ticketId}/cancel`, { method: 'POST', token });

export const updateTicketStatus = (token, ticketId, status) =>
  request(`/tickets/${ticketId}/status`, { method: 'POST', token, body: { status } });

export const submitFeedback = (token, ticketId, calificacion, comentario) =>
  request(`/tickets/${ticketId}/feedback`, { method: 'POST', token, body: { calificacion, comentario } });

export const listNotifications = (token) => request('/notifications', { token });

export const forgotPassword = (email) =>
  request('/forgot-password', { method: 'POST', body: { email } });

export const resetPassword = (resetToken, new_password) =>
  request('/reset-password', { method: 'POST', body: { token: resetToken, new_password } });

export const changePassword = (token, current_password, new_password) =>
  request('/change-password', { method: 'POST', token, body: { current_password, new_password } });

export const listMaintenance = (token, month) =>
  request(`/maintenance${month ? `?month=${month}` : ''}`, { token });

export const getMaintenanceDetail = (token, taskId) => request(`/maintenance/${taskId}`, { token });

export const toggleChecklistItem = (token, taskId, itemId) =>
  request(`/maintenance/${taskId}/checklist/${itemId}/toggle`, { method: 'POST', token });
