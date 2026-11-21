
import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchTransactions } from '../services/api'

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

const money = (amount: number, currency: string) => {
  try {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency || 'INR',
      maximumFractionDigits: 0
    }).format(amount)
  } catch {
    return `${amount.toFixed(0)} ${currency}`
  }
}

export default function Dashboard() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('all')
  const [sort, setSort] = useState('recent')
  const [page, setPage] = useState(1)

  const reload = () => {
    setLoading(true)
    setError('')

    fetchTransactions()
      .then(res => {
        setTransactions(Array.isArray(res.data) ? res.data : [])
      })
      .catch(() => {
        setError('Could not connect to the PayPulse API. Start FastAPI on port 8000.')
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    reload()
  }, [])

  const stats = useMemo(() => {
    const total = transactions.length
    const recovered = transactions.filter(t => Boolean(t.recovered)).length

    return {
      total,
      recovered,
      failed: total - recovered,
      rate: total ? (recovered / total) * 100 : 0
    }
  }, [transactions])

  const reasons = useMemo(() => {
    const counts: Record<string, number> = {}

    transactions.forEach(t => {
      const reason = t.failure_reason || 'Unknown'
      counts[reason] = (counts[reason] || 0) + 1
    })

    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
  }, [transactions])

  const filtered = useMemo(() => {
    const search = query.toLowerCase()

    return transactions
      .filter(t => {
        if (filter === 'recovered' && !t.recovered) return false
        if (filter === 'unrecovered' && t.recovered) return false

        return [
          t.transaction_id,
          t.customer_id,
          t.payment_method,
          t.failure_reason
        ].some(value =>
          String(value || '').toLowerCase().includes(search)
        )
      })
      .sort((a, b) => {
        if (sort === 'amount') {
          return b.transaction_amount - a.transaction_amount
        }
        if (sort === 'attempts') {
          return b.attempt_number - a.attempt_number
        }
        return 0
      })
  }, [transactions, filter, query, sort])

  const pageSize = 10
  const pages = Math.max(1, Math.ceil(filtered.length / pageSize))
  const currentPage = Math.min(page, pages)
  const shown = filtered.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  )

  const downloadCSV = () => {
    const columns: (keyof Transaction)[] = [
      'transaction_id',
      'customer_id',
      'transaction_amount',
      'currency',
      'payment_method',
      'failure_reason',
      'attempt_number',
      'recovered'
    ]

    const escapeCSV = (value: unknown) =>
      '"' + String(value ?? '').replace(/"/g, '""') + '"'

    const csv = [
      columns.join(','),
      ...filtered.map(tx =>
        columns.map(key => escapeCSV(tx[key])).join(',')
      )
    ].join('\r\n')

    const url = URL.createObjectURL(
      new Blob([csv], { type: 'text/csv;charset=utf-8' })
    )

    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = 'paypulse-transactions.csv'
    anchor.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">PAYMENT OPERATIONS</div>
          <h1>
            Recovery overview<span className="title-dot">.</span>
          </h1>
          <p>
            Understand failed payments, monitor outcomes, and
            prioritize smarter recovery.
          </p>
        </div>

        <button className="btn btn-primary" onClick={reload}>
          ↻ Refresh data
        </button>
      </div>

      {error && (
        <div className="alert">
          <strong>Connection unavailable</strong>
          <p>{error}</p>
          <button className="btn btn-outline" onClick={reload}>
            Try again
          </button>
        </div>
      )}

      <div className="stats-grid">
        <div className="metric">
          <div className="metric-label">Total transactions <span>⇄</span></div>
          <strong>{loading ? '—' : stats.total.toLocaleString()}</strong>
          <small>Transactions returned by API</small>
        </div>

        <div className="metric">
          <div className="metric-label">
            Recovered transactions <span className="green">↗</span>
          </div>
          <strong>{loading ? '—' : stats.recovered.toLocaleString()}</strong>
          <small>Recorded successful recoveries</small>
        </div>

        <div className="metric">
          <div className="metric-label">
            Recovery rate <span className="green">◎</span>
          </div>
          <strong>{loading ? '—' : `${stats.rate.toFixed(1)}%`}</strong>
          <small>Recovered / total transactions</small>
        </div>

        <div className="metric">
          <div className="metric-label">
            Unrecovered transactions <span className="amber">!</span>
          </div>
          <strong>{loading ? '—' : stats.failed.toLocaleString()}</strong>
          <small>Not marked as recovered</small>
        </div>
      </div>

      <div className="insights-grid" id="insights">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Recovery performance</h2>
              <p>Recorded outcomes in your dataset</p>
            </div>
            <span className="chip">All records</span>
          </div>

          <div className="performance">
            <div
              className="donut"
              style={{
                background: `conic-gradient(
                  #54ddae ${stats.rate}%,
                  #24324c ${stats.rate}% 100%
                )`
              }}
            >
              <div>
                <strong>{stats.rate.toFixed(1)}%</strong>
                <small>recovered</small>
              </div>
            </div>

            <div className="legend">
              <div>
                <span className="legend-dot green-bg" />
                Recovered
                <strong>{stats.recovered.toLocaleString()}</strong>
              </div>
              <div>
                <span className="legend-dot slate-bg" />
                Not recovered
                <strong>{stats.failed.toLocaleString()}</strong>
              </div>
              <p>
                These are recorded outcomes, not predicted
                payments or guaranteed refunds.
              </p>
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Top failure reasons</h2>
              <p>Most frequent payment failure causes</p>
            </div>
            <span className="chip">Top 5</span>
          </div>

          <div className="reason-list">
            {reasons.length ? (
              reasons.map(([reason, count]) => (
                <div className="reason" key={reason}>
                  <div>
                    <span title={reason}>{reason}</span>
                    <strong>{count}</strong>
                  </div>
                  <div className="bar">
                    <span
                      style={{
                        width: `${(count / reasons[0][1]) * 100}%`
                      }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <p className="muted">No data available yet.</p>
            )}
          </div>
        </section>
      </div>

      <section className="panel table-panel" id="transactions">
        <div className="panel-heading">
          <div>
            <h2>Transaction explorer</h2>
            <p>Search and review individual payment outcomes</p>
          </div>

          <button
            className="btn btn-outline"
            disabled={!filtered.length}
            onClick={downloadCSV}
          >
            ↓ Export CSV
          </button>
        </div>

        <div className="table-controls">
          <input
            aria-label="Search transactions"
            value={query}
            onChange={e => {
              setQuery(e.target.value)
              setPage(1)
            }}
            placeholder="Search ID, customer, method, reason..."
          />

          <select
            value={filter}
            onChange={e => {
              setFilter(e.target.value)
              setPage(1)
            }}
          >
            <option value="all">All outcomes</option>
            <option value="recovered">Recovered</option>
            <option value="unrecovered">Not recovered</option>
          </select>

          <select
            value={sort}
            onChange={e => {
              setSort(e.target.value)
              setPage(1)
            }}
          >
            <option value="recent">API order</option>
            <option value="amount">Highest amount</option>
            <option value="attempts">Most attempts</option>
          </select>
        </div>

        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>TRANSACTION</th>
                <th>AMOUNT</th>
                <th>METHOD</th>
                <th>FAILURE REASON</th>
                <th>ATTEMPTS</th>
                <th>OUTCOME</th>
                <th></th>
              </tr>
            </thead>

            <tbody>
              {shown.map(tx => (
                <tr key={tx.transaction_id}>
                  <td>
                    <Link
                      className="tx-id"
                      to={`/transactions/${encodeURIComponent(tx.transaction_id)}`}
                    >
                      {tx.transaction_id.slice(0, 12)}…
                    </Link>
                    <small className="subtext">{tx.customer_id}</small>
                  </td>

                  <td className="strong">
                    {money(tx.transaction_amount, tx.currency)}
                  </td>
                  <td>{tx.payment_method}</td>
                  <td>
                    <span className="reason-text">
                      {tx.failure_reason}
                    </span>
                  </td>
                  <td>{tx.attempt_number}</td>
                  <td>
                    <span className={`outcome ${tx.recovered ? 'success' : 'pending'}`}>
                      ● {tx.recovered ? 'Recovered' : 'Not recovered'}
                    </span>
                  </td>
                  <td>
                    <Link
                      className="arrow-link"
                      to={`/transactions/${encodeURIComponent(tx.transaction_id)}`}
                    >
                      ↗
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {loading && (
            <div className="empty">Loading transactions from API...</div>
          )}

          {!loading && !shown.length && (
            <div className="empty">No matching transactions found.</div>
          )}
        </div>

        <div className="table-footer">
          <span>
            Showing {shown.length ? (currentPage - 1) * pageSize + 1 : 0}
            –{Math.min(currentPage * pageSize, filtered.length)}
            {' '}of {filtered.length} transactions
          </span>

          <div>
            <button
              className="btn btn-outline"
              disabled={currentPage <= 1}
              onClick={() => setPage(p => p - 1)}
            >
              ← Previous
            </button>

            <span className="page-count">
              {currentPage} / {pages}
            </span>

            <button
              className="btn btn-outline"
              disabled={currentPage >= pages}
              onClick={() => setPage(p => p + 1)}
            >
              Next →
            </button>
          </div>
        </div>
      </section>

      <div className="footer-note">
        PayPulse · ML-assisted payment recovery · Figures are not financial guarantees.
      </div>
    </div>
  )
}
