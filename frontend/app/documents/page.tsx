'use client'

import { useEffect, useState } from 'react'
import { useStore } from '@/lib/store'
import { Sidebar } from '@/components/Sidebar'
import { Header } from '@/components/Header'
import { LoginForm } from '@/components/LoginForm'
import { 
  DocumentTextIcon,
  TrashIcon,
  ArrowUpTrayIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import { formatDistanceToNow } from 'date-fns'

interface Document {
  doc_id: string
  filename: string
  chunks: number
  type: string
  size: number
  uploaded_at: string
  ingested: boolean
}

function DocumentsContent() {
  const { authToken } = useStore()
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [ingesting, setIngesting] = useState(false)
  const [error, setError] = useState('')

  const loadDocuments = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await fetch(`/api/documents`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setDocuments(data.documents || [])
      } else {
        const errorText = await response.text()
        throw new Error(`Failed to load documents: ${response.status} ${errorText}`)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents')
      console.error('Load documents error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (authToken) {
      loadDocuments()
    }
  }, [authToken])

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    setUploading(true)
    setError('')

    try {
      for (const file of Array.from(files)) {
        const formData = new FormData()
        formData.append('file', file)

        const response = await fetch('/api/documents/upload', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authToken}`
          },
          body: formData
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || `Failed to upload ${file.name}`)
        }
      }

      // Reload documents list
      await loadDocuments()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
      // Reset input
      e.target.value = ''
    }
  }

  const handleIngest = async () => {
    setIngesting(true)
    setError('')

    try {
      const response = await fetch('/api/documents/ingest', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ force_reindex: true })
      })

      if (response.ok) {
        const data = await response.json()
        alert(`✅ Ingestion started!\n\n${data.message}\n\n${data.note || 'Documents will be available for RAG queries once complete.'}`)
        
        // Reload documents after a delay
        setTimeout(() => loadDocuments(), 5000)
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(errorData.detail || `Failed to start ingestion (${response.status})`)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ingestion failed')
    } finally {
      setIngesting(false)
    }
  }

  const handleDelete = async (docId: string) => {
    if (!confirm(`Delete ${docId}? This will remove it from the database and filesystem.`)) {
      return
    }

    try {
      const response = await fetch(`/api/documents/${encodeURIComponent(docId)}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })

      if (response.ok) {
        await loadDocuments()
      } else {
        throw new Error('Failed to delete document')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Documents</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage your RAG knowledge base
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <label className="btn btn-primary cursor-pointer">
            <input
              type="file"
              multiple
              accept=".pdf,.mp4,.webm,.avi,.mov,.xlsx,.xls,.docx,.doc,.txt"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
            />
            <ArrowUpTrayIcon className="h-5 w-5 mr-2" />
            {uploading ? 'Uploading...' : 'Upload Files'}
          </label>

          <button
            onClick={handleIngest}
            disabled={ingesting || documents.length === 0}
            className="btn btn-secondary"
          >
            <ArrowPathIcon className={`h-5 w-5 mr-2 ${ingesting ? 'animate-spin' : ''}`} />
            {ingesting ? 'Ingesting...' : 'Ingest All'}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-700 dark:text-red-300 text-sm">{error}</p>
        </div>
      )}

      {/* Documents List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">Loading documents...</span>
        </div>
      ) : documents.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600">
          <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No documents yet</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Upload documents to build your RAG knowledge base
          </p>
          <label className="btn btn-primary cursor-pointer inline-flex items-center">
            <input
              type="file"
              multiple
              accept=".pdf,.mp4,.webm,.avi,.mov,.xlsx,.xls,.docx,.doc,.txt"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
            />
            <ArrowUpTrayIcon className="h-5 w-5 mr-2" />
            Upload Your First Document
          </label>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Document
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Uploaded
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {documents.map((doc) => (
                <tr key={doc.doc_id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-3" />
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {doc.filename}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {doc.type.toUpperCase()}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {doc.ingested ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                        <CheckCircleIcon className="h-4 w-4 mr-1" />
                        Ingested ({doc.chunks} chunks)
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400">
                        <ClockIcon className="h-4 w-4 mr-1" />
                        Pending
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {formatBytes(doc.size)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {formatDistanceToNow(new Date(doc.uploaded_at), { addSuffix: true })}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleDelete(doc.doc_id)}
                      className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Info Box */}
      <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <h3 className="text-sm font-medium text-blue-900 dark:text-blue-300 mb-2">
          📚 How it works
        </h3>
        <ul className="text-sm text-blue-700 dark:text-blue-400 space-y-1">
          <li>1. <strong>Upload</strong> documents (PDF, videos, Word, Excel, etc.)</li>
          <li>2. Click <strong>Ingest All</strong> to process and chunk documents</li>
          <li>3. Use <strong>RAG mode</strong> in chat to query your knowledge base</li>
          <li>4. Documents are stored locally and processed with AI embeddings</li>
        </ul>
      </div>
    </div>
  )
}

export default function DocumentsPage() {
  const { isAuthenticated, checkAuth, login, logout } = useStore()
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    const authenticated = checkAuth()
    setIsChecking(false)
  }, [checkAuth])

  const handleLogin = (token: string, user: any) => {
    login(token, user)
  }

  const handleLogout = () => {
    logout()
  }

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <LoginForm onLogin={handleLogin} />
  }

  return (
    <div className="h-screen flex bg-gray-50 dark:bg-gray-900">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header onLogout={handleLogout} />
        <div className="flex-1 overflow-y-auto">
          <DocumentsContent />
        </div>
      </div>
    </div>
  )
}

