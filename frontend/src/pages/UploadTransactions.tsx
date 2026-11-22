
import { useRef, useState } from 'react'
import type { ChangeEvent, DragEvent } from 'react'
import axios from 'axios'
import {
  uploadTransactionFile,
} from '../services/uploads'
import type { UploadPreview } from '../services/uploads'
import './UploadTransactions.css'

const MAX_FILE_SIZE = 10 * 1024 * 1024
const ALLOWED_EXTENSIONS = ['csv', 'xlsx', 'xls']

export default function UploadTransactions() {
  const inputRef = useRef<HTMLInputElement>(null)

  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [result, setResult] = useState<UploadPreview | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [dragging, setDragging] = useState(false)

  function selectFile(file?: File) {
    if (!file) return

    setError('')
    setResult(null)

    const extension = file.name.split('.').pop()?.toLowerCase()

    if (!extension || !ALLOWED_EXTENSIONS.includes(extension)) {
      setSelectedFile(null)
      setError('Please select a CSV, XLSX or XLS file.')
      return
    }

    if (file.size > MAX_FILE_SIZE) {
      setSelectedFile(null)
      setError('The maximum file size is 10 MB.')
      return
    }

    setSelectedFile(file)
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    selectFile(event.target.files?.[0])
    event.target.value = ''
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault()
    setDragging(false)
    selectFile(event.dataTransfer.files[0])
  }

  async function handleUpload() {
    if (!selectedFile || loading) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await uploadTransactionFile(selectedFile)
      setResult(response)
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(
          typeof err.response?.data?.detail === 'string'
            ? err.response.data.detail
            : 'Upload failed. Check your backend connection.'
        )
      } else {
        setError('Unable to process this file.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="upload-page">
      <div className="upload-heading">
        <div>
          <p className="upload-eyebrow">DATA IMPORT</p>
          <h1>Upload Transactions</h1>
          <p>
            Import payment records and preview your data
            before running transaction analysis.
          </p>
        </div>
      </div>

      <div className="upload-panel">
        <div
          className={`upload-dropzone ${dragging ? 'dragging' : ''}`}
          onDragOver={(event) => {
            event.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
        >
          <div className="upload-symbol">⇧</div>
          <h2>Drop your transaction file here</h2>
          <p>CSV, XLSX or XLS — maximum 10 MB</p>

          <input
            ref={inputRef}
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileChange}
            hidden
          />

          <button
            type="button"
            className="upload-browse"
            onClick={() => inputRef.current?.click()}
          >
            Browse files
          </button>
        </div>

        {selectedFile && (
          <div className="upload-selected">
            <div>
              <strong>{selectedFile.name}</strong>
              <p>
                {(selectedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>

            <button
              type="button"
              className="upload-submit"
              disabled={loading}
              onClick={handleUpload}
            >
              {loading ? 'Uploading...' : 'Upload & Preview'}
            </button>
          </div>
        )}

        {error && (
          <div className="upload-error" role="alert">
            {error}
          </div>
        )}
      </div>

      {result && (
        <div className="upload-results">
          <div className="upload-result-header">
            <div>
              <p className="upload-eyebrow">UPLOAD COMPLETE</p>
              <h2>Dataset Preview</h2>
              <p>{result.filename}</p>
            </div>
            <span className="upload-success">File read successfully</span>
          </div>

          <div className="upload-stats">
            <div className="upload-stat">
              <span>Total rows</span>
              <strong>{result.row_count.toLocaleString()}</strong>
            </div>
            <div className="upload-stat">
              <span>Detected columns</span>
              <strong>{result.columns.length}</strong>
            </div>
            <div className="upload-stat">
              <span>File type</span>
              <strong>{result.file_type.toUpperCase()}</strong>
            </div>
          </div>

          <div className="upload-table-wrapper">
            <table className="upload-table">
              <thead>
                <tr>
                  {result.columns.map((column, index) => (
                    <th key={`${column}-${index}`}>{column}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.preview.map((row, index) => (
                  <tr key={index}>
                    {result.columns.map((column, columnIndex) => (
                      <td key={`${column}-${columnIndex}`}>
                        {row[column] == null
                          ? '—'
                          : String(row[column])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="upload-footnote">
            Showing the first {result.preview.length} rows.
            This is a preview only; the dataset has not yet
            been saved or analyzed.
          </p>
        </div>
      )}
    </div>
  )
}
