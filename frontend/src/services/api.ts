import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1', // proxied to FastAPI during dev
})

export const fetchTransactions = (params?: any) =>
  api.get('/transactions', { params })

export const fetchTransaction = (id: string) =>
  api.get(`/transactions/${id}`)

export const predictRecovery = (transactionId: string) =>
  api.post('/predictions', { transaction_id: transactionId })

export const recommendRetry = (transactionId: string) =>
  api.post('/retries', { transaction_id: transactionId })
