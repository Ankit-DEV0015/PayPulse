
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  fetchTransaction,
  predictRecovery,
  recommendRetry
} from '../services/api'

type Transaction = {
  transaction_id: string
  customer_id: string
  transaction_amount: number
  currency: string
  payment_method: string
  failure_reason: string
  attempt_number: number
  recovered: number
}

type Prediction = {
  transaction_id: string
  recovery_probability: number
  model_version: string
  explanation?: string
}

type Retry = {
  transaction_id: string
  recommended_action: string
  expected_net_benefit: number
  explanation: string
}

const formatMoney = (amount: number, currency = 'INR') => {
  try {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency,
      maximumFractionDigits: 2
    }).format(amount)
  } catch {
    return `${amount.toFixed(2)} ${currency}`
  }
}

export default function TransactionDetail() {
  const { id } = useParams<{ id: string }>()
  const [tx, setTx] = useState<Transaction | null>(null)
  const [prediction, setPrediction] = useState<Prediction | null>(null)
  const [retry, setRetry] = useState<Retry | null>(null)
  const [loading, setLoading] = useState(true)
  const [errors, setErrors] = useState<string[]>([])

  useEffect(() => {
    if (!id) {
      setLoading(false)
      return
    }

    let active = true

    setLoading(true)
    setErrors([])
    setTx(null)
    setPrediction(null)
    setRetry(null)

    const load = async () => {
      try {
        const response = await fetchTransaction(id)
        if (!active) return
        setTx(response.data)
      } catch {
        if (active) {
          setErrors(['Unable to load transaction details.'])
        }
        return
      }

      const results = await Promise.allSettled([
        predictRecovery(id),
        recommendRetry(id)
      ])

      if (!active) return

      if (results[0].status === 'fulfilled') {
        setPrediction(results[0].value.data)
      } else {
        setErrors(prev => [...prev, 'Recovery prediction unavailable.'])
      }

      if (results[1].status === 'fulfilled') {
        setRetry(results[1].value.data)
      } else {
        setErrors(prev => [...prev, 'Retry recommendation unavailable.'])
      }
    }

    load().finally(() => {
      if (active) setLoading(false)
    })

    return () => {
      active = false
    }
  }, [id])

  return (
    <div className="page">
      <Link to="/" className="back-link">← Back to overview</Link>

      <div className="page-heading">
        <div>
          <div className="eyebrow">TRANSACTION INTELLIGENCE</div>
          <h1>Payment details<span className="title-dot">.</span></h1>
          <p>Understand payment failures and recovery recommendations.</p>
        </div>
      </div>

      {loading && <div className="panel loading">Loading details...</div>}

      {errors.map(error => (
        <div className="alert" key={error}>{error}</div>
      ))}

      {!loading && !tx && (
        <div className="panel empty">Transaction not available.</div>
      )}

      {tx && (
        <>
          <div className="detail-hero panel">
            <div>
              <div className="metric-label">TRANSACTION ID</div>
              <h2 className="mono">{tx.transaction_id}</h2>
              <span className={`outcome ${tx.recovered ? 'success' : 'pending'}`}>
                ● {tx.recovered ? 'Recovered' : 'Not recovered'}
              </span>
            </div>
            <div>
              <div className="metric-label">PAYMENT AMOUNT</div>
              <div className="hero-amount">
                {formatMoney(tx.transaction_amount, tx.currency)}
              </div>
            </div>
          </div>

          <div className="detail-grid">
            <section className="panel">
              <div className="panel-heading">
                <div>
                  <h2>Payment information</h2>
                  <p>Transaction details from your API</p>
                </div>
              </div>

              <dl className="details-list">
                <div><dt>Customer</dt><dd>{tx.customer_id}</dd></div>
                <div><dt>Payment method</dt><dd>{tx.payment_method}</dd></div>
                <div><dt>Failure reason</dt><dd>{tx.failure_reason}</dd></div>
                <div><dt>Attempt number</dt><dd>{tx.attempt_number}</dd></div>
                <div>
                  <dt>Recorded recovery</dt>
                  <dd>{tx.recovered ? 'Yes' : 'No'}</dd>
                </div>
              </dl>
            </section>

            <section className="panel">
              <div className="panel-heading">
                <div>
                  <h2>ML recovery prediction</h2>
                  <p>Estimated chance of successful recovery</p>
                </div>
              </div>

              {prediction ? (
                <>
                  <div className="prediction-number">
                    {(prediction.recovery_probability * 100).toFixed(1)}
                    <span>%</span>
                  </div>

                  <div className="progress">
                    <span style={{
                      width: `${Math.max(0, Math.min(100,
                        prediction.recovery_probability * 100))}%`
                    }} />
                  </div>

                  <div className="detail-meta">
                    Model version: {prediction.model_version}
                  </div>

                  {prediction.explanation && (
                    <p className="explanation">{prediction.explanation}</p>
                  )}

                  <p className="fineprint">
                    A prediction is not a confirmed payment outcome.
                  </p>
                </>
              ) : (
                <p className="muted">Prediction data unavailable.</p>
              )}
            </section>
          </div>

          <section className="panel retry-panel">
            <div className="panel-heading">
              <div>
                <h2>Recommended retry strategy</h2>
                <p>Decision engine output for this transaction</p>
              </div>
              <span className="chip">Decision support</span>
            </div>

            {retry ? (
              <div className="retry-content">
                <div>
                  <div className="metric-label">RECOMMENDED ACTION</div>
                  <div className="action-name">
                    {retry.recommended_action.replace(/_/g, ' ')}
                  </div>
                  <p className="explanation">{retry.explanation}</p>
                </div>

                <div className="benefit">
                  <div className="metric-label">EXPECTED NET BENEFIT</div>
                  <strong>
                    {formatMoney(retry.expected_net_benefit, tx.currency)}
                  </strong>
                  <small>
                    Estimated economic value, not a refund or
                    guaranteed recovery.
                  </small>
                </div>
              </div>
            ) : (
              <p className="muted">Retry recommendation unavailable.</p>
            )}
          </section>

          <section className="panel">
            <div className="panel-heading">
              <div>
                <h2>Model explainability</h2>
                <p>SHAP visualizations from your ML pipeline</p>
              </div>
            </div>

            <div className="shap-grid">
              {[
                ['global_feature_importance.png', 'Global feature importance'],
                ['shap_beeswarm.png', 'SHAP beeswarm plot']
              ].map(([file, label]) => (
                <div key={file}>
                  <img
                    src={`/shap/${file}`}
                    alt={label}
                    onError={event => {
                      event.currentTarget.style.display = 'none'
                      event.currentTarget.nextElementSibling
                        ?.classList.remove('hidden')
                    }}
                  />
                  <div className="shap-missing hidden">
                    Image not generated yet
                  </div>
                  <small>{label}</small>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  )
}
