const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function getToken() {
  return localStorage.getItem('leadflow_token')
}

export function setToken(token) {
  if (token) localStorage.setItem('leadflow_token', token)
  else localStorage.removeItem('leadflow_token')
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth) {
    const token = getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  if (res.status === 204) return null

  let data = null
  try {
    data = await res.json()
  } catch {
    // no body
  }

  if (!res.ok) {
    const message = (data && data.detail) || `Request failed (${res.status})`
    const err = new Error(typeof message === 'string' ? message : JSON.stringify(message))
    err.status = res.status
    throw err
  }
  return data
}

export const api = {
  // auth
  login: (email, password) => request('/api/auth/login', { method: 'POST', body: { email, password }, auth: false }),
  me: () => request('/api/auth/me'),

  // users
  listUsers: () => request('/api/users'),
  createUser: (payload) => request('/api/users', { method: 'POST', body: payload }),

  // leads
  submitPublicLead: (payload) => request('/api/leads/public', { method: 'POST', body: payload, auth: false }),
  listLeads: (params = {}) => {
    const qs = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v !== undefined && v !== ''))
    ).toString()
    return request(`/api/leads${qs ? `?${qs}` : ''}`)
  },
  getLead: (id) => request(`/api/leads/${id}`),
  updateLead: (id, payload) => request(`/api/leads/${id}`, { method: 'PATCH', body: payload }),
  addNote: (id, content) => request(`/api/leads/${id}/notes`, { method: 'POST', body: { content } }),
}
