
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import TransactionDetail from './pages/TransactionDetail'

export default function App() {
  return (
    <BrowserRouter>
      <div className="shell">
        <aside className="sidebar">
          <div className="brand">
            <span className="brand-mark">↗</span>
            <span>
              Pay<span className="accent">Pulse</span>
              <small>RECOVERY INTELLIGENCE</small>
            </span>
          </div>

          <div className="nav-caption">WORKSPACE</div>

          <nav>
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `nav-link ${isActive ? 'active' : ''}`
              }
            >
              <span>◫</span> Overview
            </NavLink>

            <a className="nav-link" href="/#transactions">
              <span>⇄</span> Transactions
            </a>

            <a className="nav-link" href="/#insights">
              <span>◈</span> Insights
            </a>
          </nav>

          <div className="sidebar-bottom">
            <div className="side-note">
              <span className="status-dot" />
              API-powered analytics
            </div>
            <div className="avatar-line">
              <span className="avatar">PP</span>
              <div>
                <strong>PayPulse</strong>
                <small>Development workspace</small>
              </div>
            </div>
          </div>
        </aside>

        <div className="workspace">
          <header className="topbar">
            <span className="breadcrumbs">
              Workspace <span>/</span> Payment intelligence
            </span>
            <div className="top-actions">
              <span className="live-pill">
                <span className="status-dot" /> API mode
              </span>
              <span className="avatar small">PP</span>
            </div>
          </header>

          <main className="content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route
                path="/transactions/:id"
                element={<TransactionDetail />}
              />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}
