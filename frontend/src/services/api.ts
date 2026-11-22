
import axios from 'axios'

const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_URL ||
    '/api/v1',
  timeout: 60000,
})

export const fetchTransactions = (params?: any) =>
  api.get('/transactions', { params })

export const fetchTransaction = (id: string) =>
  api.get(`/transactions/${encodeURIComponent(id)}`)

export const predictRecovery = (transactionId: string) =>
  api.post('/predictions', {
    transaction_id: transactionId,
  })

export const recommendRetry = (transactionId: string) =>
  api.post('/retries', {
    transaction_id: transactionId,
  })
