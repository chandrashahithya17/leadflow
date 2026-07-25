import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

const STATUSES = ['new', 'contacted', 'qualified', 'won', 'lost']

function StagePill({ status }) {
  return <span className={`stage-pill stage-${status}`}>{status}</span>
}

export default function Dashboard() {
  const [leads, setLeads] = useState([])
  const [users, setUsers] = useState([])
  const [total, setTotal] = useState(0)
  const [pages, setPages] = useState(1)
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState('')
  const [assigneeFilter, setAssigneeFilter] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.listUsers().then(setUsers).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    setError('')
    api
      .listLeads({
        page,
        page_size: 10,
        status: statusFilter || undefined,
        assigned_to_id: assigneeFilter || undefined,
        search: search || undefined,
      })
      .then((res) => {
        setLeads(res.items)
        setTotal(res.total)
        setPages(res.pages)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [page, statusFilter, assigneeFilter, search])

  return (
    <div>
      <h1 className="page-title">Pipeline</h1>
      <p className="page-sub">{total} lead{total === 1 ? '' : 's'} in the system.</p>

      <div className="toolbar">
        <div className="field">
          <label htmlFor="search">Search</label>
          <input
            id="search"
            placeholder="Name, email, company…"
            value={search}
            onChange={(e) => {
              setPage(1)
              setSearch(e.target.value)
            }}
          />
        </div>
        <div className="field">
          <label htmlFor="status">Status</label>
          <select
            id="status"
            value={statusFilter}
            onChange={(e) => {
              setPage(1)
              setStatusFilter(e.target.value)
            }}
          >
            <option value="">All</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="assignee">Assigned to</label>
          <select
            id="assignee"
            value={assigneeFilter}
            onChange={(e) => {
              setPage(1)
              setAssigneeFilter(e.target.value)
            }}
          >
            <option value="">Anyone</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.email}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="error-text">{error}</div>}

      {loading ? (
        <p>Loading…</p>
      ) : leads.length === 0 ? (
        <div className="empty-state card">No leads match these filters yet.</div>
      ) : (
        <>
          <table className="lead-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Company</th>
                <th>Status</th>
                <th>Assigned to</th>
                <th>Received</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => (
                <tr key={lead.id}>
                  <td>
                    <Link className="row-link" to={`/leads/${lead.id}`}>
                      {lead.name}
                    </Link>
                    <div style={{ color: 'var(--ink-soft)', fontSize: '0.8rem' }}>{lead.email}</div>
                  </td>
                  <td>{lead.company || '—'}</td>
                  <td>
                    <StagePill status={lead.status} />
                  </td>
                  <td>{lead.assigned_to_email || '—'}</td>
                  <td>{new Date(lead.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="pagination">
            <span className="count">
              Page {page} of {pages}
            </span>
            <button className="btn-ghost btn" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              Previous
            </button>
            <button className="btn-ghost btn" disabled={page >= pages} onClick={() => setPage((p) => p + 1)}>
              Next
            </button>
          </div>
        </>
      )}
    </div>
  )
}
