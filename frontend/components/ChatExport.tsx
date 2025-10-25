import React, { useState } from 'react'
import { useStore } from '../lib/store'

interface ChatExportProps {
  chatId: string
  className?: string
}

export function ChatExport({ chatId, className = '' }: ChatExportProps) {
  const { exportChat, exportAllChats } = useStore()
  const [isExporting, setIsExporting] = useState(false)

  const handleExport = async () => {
    setIsExporting(true)
    try {
      const markdown = await exportChat(chatId)
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
      downloadMarkdown(markdown, `graphmind-conversation-${timestamp}.md`)
    } catch (error) {
      console.error('Export failed:', error)
      alert('Export failed. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <button
      onClick={handleExport}
      disabled={isExporting}
      className={`px-3 py-1 text-sm bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
    >
      {isExporting ? 'Exporting...' : 'Export Chat'}
    </button>
  )
}

interface ExportAllProps {
  className?: string
}

export function ExportAll({ className = '' }: ExportAllProps) {
  const { exportAllChats } = useStore()
  const [isExporting, setIsExporting] = useState(false)

  const handleExportAll = async () => {
    setIsExporting(true)
    try {
      const markdown = await exportAllChats()
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
      downloadMarkdown(markdown, `graphmind-full-export-${timestamp}.md`)
    } catch (error) {
      console.error('Export failed:', error)
      alert('Export failed. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <button
      onClick={handleExportAll}
      disabled={isExporting}
      className={`px-3 py-1 text-sm bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
    >
      {isExporting ? 'Exporting...' : 'Export All Chats'}
    </button>
  )
}

function downloadMarkdown(content: string, filename: string) {
  const blob = new Blob([content], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}