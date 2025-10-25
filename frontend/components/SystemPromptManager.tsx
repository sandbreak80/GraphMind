import React, { useState, useEffect } from 'react'
import { useStore } from '../lib/store'
import { SystemPromptEditor } from './SystemPromptEditor'

interface SystemPromptManagerProps {
  isOpen: boolean
  onClose: () => void
}

interface PromptInfo {
  mode: string
  current_version: string
  versions: string[]
  prompt: string
  created_at: string | null
  hash: string | null
}

export function SystemPromptManager({ isOpen, onClose }: SystemPromptManagerProps) {
  const { authToken } = useStore()
  const [prompts, setPrompts] = useState<PromptInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [editingMode, setEditingMode] = useState<string | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      loadPrompts()
    }
  }, [isOpen])

  const loadPrompts = async () => {
    try {
      setLoading(true)
      setError('')
      
      const response = await fetch('/api/system-prompts', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        const promptList = await Promise.all(
          Object.keys(data.prompts).map(async (mode) => {
            // Load the current active prompt (custom or default)
            const promptResponse = await fetch(`/api/user-prompts/${mode}`, {
              headers: {
                'Authorization': `Bearer ${authToken}`
              }
            })
            if (promptResponse.ok) {
              const promptData = await promptResponse.json()
              // Extract the actual prompt text from the response
              let promptText = ''
              if (typeof promptData.prompt === 'string') {
                promptText = promptData.prompt
              } else if (promptData.prompt && typeof promptData.prompt === 'object' && promptData.prompt.prompt) {
                promptText = promptData.prompt.prompt
              }
              
              return {
                mode,
                current_version: promptData.is_default ? 'default' : 'custom',
                versions: ['default', 'custom'],
                prompt: promptText,
                hash: promptData.prompt?.hash || null
              }
            }
            return null
          })
        )
        setPrompts(promptList.filter((prompt): prompt is PromptInfo => prompt !== null))
      } else {
        setError('Failed to load prompts')
      }
    } catch (err) {
      setError('Failed to load prompts')
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (mode: string) => {
    setEditingMode(mode)
  }

  const handleCloseEditor = () => {
    setEditingMode(null)
    loadPrompts() // Refresh the list
  }

  const getModeDisplayName = (mode: string) => {
    const modeMap: { [key: string]: string } = {
      'rag_only': 'RAG Only',
      'web_search_only': 'Web Search Only',
      'obsidian_only': 'Obsidian Only',
      'comprehensive_research': 'Comprehensive Research'
    }
    return modeMap[mode] || mode
  }

  const getModeDescription = (mode: string) => {
    const descriptions: { [key: string]: string } = {
      'rag_only': 'Document-based responses from PDFs, video transcripts, and processed content',
      'web_search_only': 'Real-time web search results for current market information',
      'obsidian_only': 'Personal knowledge base integration for personalized advice',
      'comprehensive_research': 'Combined document and web search for comprehensive analysis'
    }
    return descriptions[mode] || 'System prompt for this mode'
  }

  if (!isOpen) return null

  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-6xl max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
              System Prompt Management
            </h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl"
            >
              ✕
            </button>
          </div>

          {loading && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Loading prompts...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4 mb-6">
              <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
            </div>
          )}

          {!loading && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {prompts.map((prompt) => (
                <div key={prompt.mode} className="border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                        {getModeDisplayName(prompt.mode)}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {getModeDescription(prompt.mode)}
                      </p>
                    </div>
                    <span className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                      {prompt.current_version}
                    </span>
                  </div>

                  <div className="mb-4">
                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      Preview:
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-3 text-sm text-gray-800 dark:text-gray-200 max-h-32 overflow-y-auto">
                      {prompt.prompt.substring(0, 200)}
                      {prompt.prompt.length > 200 && '...'}
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-4">
                    <span>{prompt.prompt.length} characters</span>
                    <span>{prompt.prompt.split(' ').length} words</span>
                    {prompt.hash && (
                      <span className="font-mono text-xs">#{prompt.hash}</span>
                    )}
                  </div>

                  <button
                    onClick={() => handleEdit(prompt.mode)}
                    className="w-full px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    Edit Prompt
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              <h4 className="font-medium mb-2">About System Prompts:</h4>
              <ul className="list-disc list-inside space-y-1">
                <li>System prompts define how the AI behaves in each chat mode</li>
                <li>You can customize prompts to match your trading style and preferences</li>
                <li>Changes are saved per user and override the default prompts</li>
                <li>Use the "Reset to Default" option to restore original prompts</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {editingMode && (
        <SystemPromptEditor
          mode={editingMode}
          isOpen={true}
          onClose={handleCloseEditor}
        />
      )}
    </>
  )
}