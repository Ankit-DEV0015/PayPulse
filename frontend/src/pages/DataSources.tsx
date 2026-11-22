
import { useState } from 'react'
import { Link } from 'react-router-dom'
import './DataSources.css'

type Gateway = 'Razorpay' | 'Stripe' | 'Cashfree' | 'PayU'

const gateways: Gateway[] = [
  'Razorpay',
  'Stripe',
  'Cashfree',
  'PayU',
]

export default function DataSources() {
  const [selectedGateway, setSelectedGateway] = useState<Gateway | null>(null)

  return (
    <div className="sources-page">
      <div className="sources-heading">
        <p className="sources-eyebrow">PAYMENT INTEGRATIONS</p>
        <h1>Connect your payment data</h1>
        <p>
          Choose how your business sends transaction data to PayPulse.
          Connect a payment gateway or upload your records manually.
        </p>
      </div>

      <div className="sources-grid">
        <section className="source-card">
          <div className="source-icon">⚡</div>
          <h2>Connect Payment Gateway</h2>
          <p>
            Automatically import payment transactions from your
            supported payment provider.
          </p>

          <div className="source-features">
            <span>✓ Automatic synchronization</span>
            <span>✓ Continuous transaction updates</span>
            <span>✓ No manual file uploads</span>
          </div>

          <button
            type="button"
            className="source-button"
            onClick={() => {
              document.getElementById('gateway-options')?.scrollIntoView({
                behavior: 'smooth',
              })
            }}
          >
            Choose payment gateway
          </button>
        </section>

        <section className="source-card">
          <div className="source-icon">⇧</div>
          <h2>Upload CSV or Excel</h2>
          <p>
            Import payment records manually if your payment gateway
            isn't supported or automatic connection is unavailable.
          </p>

          <div className="source-features">
            <span>✓ CSV, XLSX and XLS files</span>
            <span>✓ Preview transactions</span>
            <span>✓ Manual import fallback</span>
          </div>

          <Link to="/upload" className="source-button">
            Upload transactions
          </Link>
        </section>
      </div>

      <section id="gateway-options" className="gateway-section">
        <div className="gateway-heading">
          <h2>Select a payment gateway</h2>
          <p>
            Choose the payment provider your business currently uses.
          </p>
        </div>

        <div className="gateway-grid">
          {gateways.map((gateway) => (
            <button
              key={gateway}
              type="button"
              className={`gateway-card ${
                selectedGateway === gateway ? 'selected' : ''
              }`}
              onClick={() => setSelectedGateway(gateway)}
            >
              <span className="gateway-symbol">◈</span>
              <strong>{gateway}</strong>
              <span className="gateway-status">
                {selectedGateway === gateway
                  ? 'Selected'
                  : 'Select provider'}
              </span>
            </button>
          ))}
        </div>

        {selectedGateway && (
          <div className="gateway-message">
            <strong>{selectedGateway} selected</strong>
            <p>
              Gateway API authorization and automatic synchronization
              are not configured yet. We'll implement this connection
              in the backend integration phase.
            </p>
            <Link to="/upload" className="gateway-fallback">
              Use manual CSV/Excel upload instead
            </Link>
          </div>
        )}
      </section>

      <div className="sources-footer">
        <strong>One unified PayPulse dashboard</strong>
        <p>
          Whether transactions come from a gateway or a file,
          PayPulse will standardize them for analytics and
          failure-risk assessment.
        </p>
      </div>
    </div>
  )
}
