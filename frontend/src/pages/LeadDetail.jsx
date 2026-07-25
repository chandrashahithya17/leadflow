import React, { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../AuthContext.jsx'

const STATUSES = ['new', 'contacted', 'qualified', 'won', 'lost']

export default function LeadDetail() {
  const { id } = useParams()
  const { user, isAdmin } = useAuth()
  const [lead, setLead] = useState(null)
  const [users, setUsers] = useState([])
  const [noteText, setNoteText] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const load = useCallback(() => {
    api.getLead(id).then(setLead).catch((err) => setError(err.message))
  }, [id])

  useEffect(() => {
    load()
    api.listUsers().then(setUsers).catch(() => {})
  }, [load])

  if (error) return <div className="error-text">{error}</div>
  if (!lead) return <p>Loading…</p>

  const isOwner = lead.assigned_to_id === user.id
  // Mirrors the server's permission rule: only an admin, or the member this
  // lead is assigned to, may change its status.
  const canChangeStatus = isAdmin || isOwner
  // Mirrors the server's rule: members may only claim an unassigned lead for
  // themselves; they cannot reassign an already-assigned lead to someone else.
  const canReassign = isAdmin || !lead.assigned_to_id

  async function handleStatusChange(newStatus) {
    setBusy(true)
    setError('')
    try {
      await api.updateLead(id, { status: newStatus })
      load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function handleAssign(userId) {
    if (!userId) return
    setBusy(true)
    setError('')
    try {
      await api.updateLead(id, { assigned_to_id: userId })
      load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function handleAddNote(e) {
    e.preventDefault()
    if (!noteText.trim()) return
    setBusy(true)
    setError('')
    try {
      await api.addNote(id, noteText)
      setNoteText('')
      load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <Link to="/" style={{ fontSize: '0.85rem' }}>
        ← Back to pipeline
      </Link>

      <h1 className="page-title" style={{ marginTop: '0.75rem' }}>
        {lead.name}
      </h1>
      <p className="page-sub">
        {lead.email} {lead.company && `· ${lead.company}`} {lead.phone && `· ${lead.phone}`}
      </p>

      {error && <div className="error-text" style={{ marginBottom: '1rem' }}>{error}</div>}

      <div className="detail-grid">
        <div>
          <div className="card" style={{ marginBottom: '1.25rem' }}>
            <p className="section-label">Original message</p>
            <p>{lead.message || <em>No message provided.</em>}</p>
          </div>

          <div className="card" style={{ marginBottom: '1.25rem' }}>
            <p className="section-label">Notes</p>
            {lead.notes.length === 0 && <p style={{ color: 'var(--ink-soft)' }}>No notes yet.</p>}
            {lead.notes.map((n) => (
              <div key={n.id} className="note-item">
                <div>{n.content}</div>
                <div className="meta">
                  {n.author_email} · {new Date(n.created_at).toLocaleString()}
                </div>
              </div>
            ))}
            <form onSubmit={handleAddNote} style={{ marginTop: '0.75rem' }}>
              <textarea
                rows={2}
                placeholder="Add a note…"
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
              />
              <button className="btn btn-signal" type="submit" disabled={busy} style={{ marginTop: '0.5rem' }}>
                Add note
              </button>
            </form>
          </div>

          <div className="card">
            <p className="section-label">Activity trail</p>
            {lead.activities.map((a) => (
              <div key={a.id} className="activity-item">
                <div>
                  <strong>{a.action.replace('_', ' ')}</strong>
                  {a.detail ? ` — ${a.detail}` : ''}
                </div>
                <div className="ts">{new Date(a.created_at).toLocaleString()}</div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="card" style={{ marginBottom: '1.25rem' }}>
            <p className="section-label">Status</p>
            <select
              value={lead.status}
              disabled={!canChangeStatus || busy}
              onChange={(e) => handleStatusChange(e.target.value)}
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
            {!canChangeStatus && (
              <p style={{ fontSize: '0.78rem', color: 'var(--ink-soft)', marginTop: '0.5rem' }}>
                Only the assigned member or an admin can change this.
              </p>
            )}
          </div>

          <div className="card">
            <p className="section-label">Assigned to</p>
            {lead.assigned_to_email ? (
              <p style={{ marginTop: 0 }}>{lead.assigned_to_email}</p>
            ) : (
              <p style={{ marginTop: 0, color: 'var(--ink-soft)' }}>Unassigned</p>
            )}

            {canReassign ? (
              isAdmin ? (
                <select disabled={busy} defaultValue="" onChange={(e) => handleAssign(e.target.value)}>
                  <option value="" disabled>
                    Assign to…
                  </option>
                  {users.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.email}
                    </option>
                  ))}
                </select>
              ) : (
                <button className="btn btn-ghost" disabled={busy} onClick={() => handleAssign(user.id)}>
                  Claim this lead
                </button>
              )
            ) : (
              <p style={{ fontSize: '0.78rem', color: 'var(--ink-soft)' }}>
                Already assigned — only an admin can reassign it.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
