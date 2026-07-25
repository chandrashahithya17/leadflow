import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Team() {
  const [users, setUsers] = useState([])
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('member')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  function load() {
    api.listUsers().then(setUsers).catch((err) => setError(err.message))
  }

  useEffect(load, [])

  async function handleCreate(e) {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      await api.createUser({ email, password, role })
      setEmail('')
      setPassword('')
      setRole('member')
      load()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <h1 className="page-title">Team</h1>
      <p className="page-sub">Manage who has access to the pipeline.</p>

      <div className="detail-grid">
        <div>
          <table className="lead-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Role</th>
                <th>Joined</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.email}</td>
                  <td>{u.role}</td>
                  <td>{new Date(u.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <p className="section-label">Add team member</p>
          <form onSubmit={handleCreate}>
            <div className="field">
              <label htmlFor="new-email">Email</label>
              <input id="new-email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div className="field">
              <label htmlFor="new-password">Temporary password</label>
              <input
                id="new-password"
                type="text"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="new-role">Role</label>
              <select id="new-role" value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="member">Member</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            {error && <div className="error-text">{error}</div>}
            <button className="btn btn-signal" type="submit" disabled={saving} style={{ width: '100%' }}>
              {saving ? 'Adding…' : 'Add member'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
