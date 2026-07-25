import React, { useState } from 'react'
import { api } from '../api'

const initial = { name: '', email: '', phone: '', company: '', message: '' }

export default function PublicCaptureForm() {
  const [form, setForm] = useState(initial)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      await api.submitPublicLead(form)
      setSubmitted(true)
      setForm(initial)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="form-narrow">
      <h1 className="page-title">Talk to our team</h1>
      <p className="page-sub">Tell us a bit about what you need — we'll follow up shortly.</p>

      {submitted && (
        <div className="success-banner">
          Thanks — your message reached our team. We'll be in touch soon.
        </div>
      )}

      <form onSubmit={handleSubmit} className="card">
        <div className="field">
          <label htmlFor="name">Name</label>
          <input id="name" required value={form.name} onChange={(e) => update('name', e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            required
            value={form.email}
            onChange={(e) => update('email', e.target.value)}
          />
        </div>
        <div className="field">
          <label htmlFor="company">Company</label>
          <input id="company" value={form.company} onChange={(e) => update('company', e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="phone">Phone</label>
          <input id="phone" value={form.phone} onChange={(e) => update('phone', e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="message">What are you looking for?</label>
          <textarea
            id="message"
            rows={4}
            value={form.message}
            onChange={(e) => update('message', e.target.value)}
          />
        </div>

        {error && <div className="error-text">{error}</div>}

        <button className="btn btn-signal" type="submit" disabled={saving} style={{ width: '100%' }}>
          {saving ? 'Sending…' : 'Send'}
        </button>
      </form>
    </div>
  )
}
