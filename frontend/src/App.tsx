
import {
  BrowserRouter,
  Routes,
  Route,
  NavLink,
  Link,
  Outlet,
  useNavigate,
  useLocation,
} from 'react-router-dom'

import Dashboard from './pages/Dashboard'
import TransactionDetail from './pages/TransactionDetail'
import Signup from './pages/Signup'
import UploadTransactions from './pages/UploadTransactions'
import DataSources from './pages/DataSources'

function WorkspaceLayout() {
  const navigate = useNavigate()
  const location = useLocation()

  // Navigate to a section of the dashboard
  const goToSection = (sectionId: string) => {
    navigate('/')

    setTimeout(() => {
      document.getElementById(sectionId)?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      })
    }, 100)
  }

  return (
    <div className="shell">
      {/* SIDEBAR */}
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
          {/* DASHBOARD */}
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `nav-link ${isActive ? 'active' : ''}`
            }
          >
            <span>◫</span>
            Overview
          </NavLink>

          {/* TRANSACTIONS */}
          <button
            type="button"
            className="nav-link"
            onClick={() => goToSection('transactions')}
          >
            <span>⇄</span>
            Transactions
          </button>

          {/* ANALYTICS */}
          <button
            type="button"
            className="nav-link"
            onClick={() => goToSection('insights')}
          >
            <span>◈</span>
            Analytics
          </button>

          {/* DATA SOURCES */}
          <NavLink
            to="/data-sources"
            className={({ isActive }) =>
              `nav-link ${isActive ? 'active' : ''}`
            }
          >
            <span>⚡</span>
            Data Sources
          </NavLink>

          {/* DIRECT UPLOAD */}
          <NavLink
            to="/upload"
            className={({ isActive }) =>
              `nav-link ${isActive ? 'active' : ''}`
            }
          >
            <span>⇧</span>
            Upload Transactions
          </NavLink>

          {/* SIGNUP */}
          <NavLink
            to="/signup"
            className={({ isActive }) =>
              `nav-link ${isActive ? 'active' : ''}`
            }
          >
            <span>♙</span>
            Create Account
          </NavLink>
        </nav>

        <div className="sidebar-bottom">
          <div className="side-note">
            <span className="status-dot" />
            Payment intelligence platform
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

      {/* MAIN WORKSPACE */}
      <div className="workspace">
        <header className="topbar">
          <span className="breadcrumbs">
            Workspace <span>/</span>{' '}
            {location.pathname === '/'
              ? 'Overview'
              : location.pathname === '/data-sources'
              ? 'Data Sources'
              : location.pathname === '/upload'
              ? 'Upload Transactions'
              : 'Payment Intelligence'}
          </span>

          <div className="top-actions">
            <span className="live-pill">
              <span className="status-dot" />
              API Mode
            </span>

            <Link
              to="/signup"
              className="avatar small"
              title="Create account"
            >
              PP
            </Link>
          </div>
        </header>

        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* PUBLIC SIGNUP PAGE */}
        <Route
          path="/signup"
          element={<Signup />}
        />

        {/* MAIN PAYPULSE WORKSPACE */}
        <Route element={<WorkspaceLayout />}>
          {/* OVERVIEW */}
          <Route
            path="/"
            element={<Dashboard />}
          />

          {/* TRANSACTION DETAILS */}
          <Route
            path="/transactions/:id"
            element={<TransactionDetail />}
          />

          {/* CONNECT GATEWAY OR UPLOAD */}
          <Route
            path="/data-sources"
            element={<DataSources />}
          />

          {/* CSV / EXCEL UPLOAD */}
          <Route
            path="/upload"
            element={<UploadTransactions />}
          />
        </Route>

        {/* FALLBACK */}
        <Route
          path="*"
          element={
            <div className="min-h-screen flex flex-col items-center justify-center">
              <h1>404 — Page Not Found</h1>

              <Link to="/" className="btn btn-primary">
                Back to Dashboard
              </Link>
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}
