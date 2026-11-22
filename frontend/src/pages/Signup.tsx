
import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import './Signup.css'

export default function Signup() {
  const [name, setName] = useState('')
  const [business, setBusiness] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [message, setMessage] = useState('')

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()

    if (password.length < 8) {
      setMessage('Password must contain at least 8 characters.')
      return
    }

    if (password !== confirmPassword) {
      setMessage('Passwords do not match.')
      return
    }

    setMessage(
      'Form validated! Account creation will be enabled after we connect the backend.'
    )
  }

  return (
    <div className="signup-page">
      <div className="signup-intro">
        <div className="signup-logo">
          <span className="signup-logo-icon">↗</span>
          Pay<span>Pulse</span>
        </div>

        <div className="signup-intro-content">
          <div className="signup-eyebrow">
            PAYMENT RECOVERY INTELLIGENCE
          </div>

          <h1>
            Recover smarter.
            <br />
            <span>Grow faster.</span>
          </h1>

          <p>
            Understand failed transactions, discover recovery
            opportunities, and make better payment decisions.
          </p>

          <div className="signup-feature">
            <span>✓</span> AI-powered recovery insights
          </div>
          <div className="signup-feature">
            <span>✓</span> Intelligent retry recommendations
          </div>
          <div className="signup-feature">
            <span>✓</span> Real-time payment analytics
          </div>
        </div>

        <div className="signup-footer">
          © 2026 PayPulse. Built for smarter payments.
        </div>
      </div>

      <div className="signup-form-side">
        <div className="signup-form-container">
          <div className="signup-topline">
            <span>NEW TO PAYPULSE?</span>
            <Link to="/">Explore dashboard →</Link>
          </div>

          <h2>Create your account</h2>
          <p className="signup-subtitle">
            Start your payment recovery journey.
          </p>

          <form onSubmit={handleSubmit}>
            <label htmlFor="fullName">Full name</label>
            <input
              id="fullName"
              type="text"
              placeholder="Enter your full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />

            <label htmlFor="business">Business name</label>
            <input
              id="business"
              type="text"
              placeholder="Enter your business name"
              value={business}
              onChange={(e) => setBusiness(e.target.value)}
              required
            />

            <label htmlFor="email">Work email</label>
            <input
              id="email"
              type="email"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="Minimum 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
              minLength={8}
              required
            />

            <label htmlFor="confirmPassword">
              Confirm password
            </label>
            <input
              id="confirmPassword"
              type="password"
              placeholder="Re-enter your password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              autoComplete="new-password"
              required
            />

            {message && (
              <p className="signup-message" role="status">
                {message}
              </p>
            )}

            <button type="submit" className="signup-submit">
              Create account →
            </button>
          </form>

          <p className="signup-bottom-text">
            Account registration is coming soon.
          </p>
        </div>
      </div>
    </div>
  )
}
