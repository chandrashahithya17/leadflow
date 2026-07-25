import React from 'react'
import { Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './AuthContext.jsx'
import PublicCaptureForm from './pages/PublicCaptureForm.jsx'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import LeadDetail from './pages/LeadDetail.jsx'
import Team from './pages/Team.jsx'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="app-main">Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  return children
}

function AdminRoute({ children }) {
  const { isAdmin, loading } = useAuth()
  if (loading) return <div className="app-main">Loading…</div>
  if (!isAdmin) return <Navigate to="/" replace />
  return children
}

function Header() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <header className="app-header">
      <Link to={user ? '/' : '/apply'} className="brand">
        Lead<span className="brand-mark">Flow</span>
      </Link>
      <nav className="header-nav">
        {user ? (
          <>
            <Link to="/">Pipeline</Link>
            {user.role === 'admin' && <Link to="/team">Team</Link>}
            <span className="user-chip">
              {user.email}
              <span className="role-badge">{user.role}</span>
            </span>
            <button
              className="btn-ghost btn"
              onClick={() => {
                logout()
                navigate('/login')
              }}
            >
              Sign out
            </button>
          </>
        ) : (
          <>
            <Link to="/apply">Submit a lead</Link>
            <Link to="/login" className="btn btn-signal">
              Team sign in
            </Link>
          </>
        )}
      </nav>
    </header>
  )
}

function Footer() {
  return (
    <footer className="app-footer">
      Built for{' '}
      <a href="https://digitalheroesco.com" target="_blank" rel="noreferrer">
        Digital Heroes Training Task
      </a>
    </footer>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Header />
      <main className="app-main">
        <Routes>
          <Route path="/apply" element={<PublicCaptureForm />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/leads/:id"
            element={
              <ProtectedRoute>
                <LeadDetail />
              </ProtectedRoute>
            }
          />
          <Route
            path="/team"
            element={
              <ProtectedRoute>
                <AdminRoute>
                  <Team />
                </AdminRoute>
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/apply" replace />} />
        </Routes>
      </main>
      <Footer />
    </AuthProvider>
  )
}
