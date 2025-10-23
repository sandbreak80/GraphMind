import React, { useState, useEffect } from 'react'
import { useStore } from '../lib/store'
import { apiClient } from '../lib/api'

interface SystemPromptEditorProps {
  mode: string
  isOpen: boolean
  onClose: () => void
}

export function SystemPromptEditor({ mode, isOpen, onClose }: SystemPromptEditorProps) {
  const { authToken } = useStore()
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [validation, setValidation] = useState<any>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen && mode) {
      loadPrompt()
    }
  }, [isOpen, mode])

  const loadPrompt = async () => {
    try {
      setLoading(true)
      setError('')
      
      // Load system prompt
      const response = await fetch(`/api/system-prompts/${mode}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setPrompt(data.prompt || '')
      } else {
        setError('Failed to load prompt')
      }
    } catch (err) {
      setError('Failed to load prompt')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setError('')
      
      const response = await fetch(`/api/user-prompts/${mode}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ prompt })
      })
      
      if (response.ok) {
        const data = await response.json()
        setValidation(data.validation)
        onClose()
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to save prompt')
      }
    } catch (err) {
      setError('Failed to save prompt')
    } finally {
      setSaving(false)
    }
  }

  const handleReset = async () => {
    try {
      setSaving(true)
      setError('')
      
      const response = await fetch(`/api/user-prompts/${mode}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      if (response.ok) {
        loadPrompt() // Reload default prompt
      } else {
        setError('Failed to reset prompt')
      }
    } catch (err) {
      setError('Failed to reset prompt')
    } finally {
      setSaving(false)
    }
  }

  const validatePrompt = (text: string) => {
    const issues = []
    const warnings = []
    
    if (text.length < 50) {
      issues.push('Prompt is too short (minimum 50 characters)')
    } else if (text.length > 2000) {
      warnings.push('Prompt is very long (over 2000 characters)')
    }
    
    const requiredSections = ['role', 'guidelines', 'format']
    for (const section of requiredSections) {
      if (!text.toLowerCase().includes(section)) {
        warnings.push(`Consider including '${section}' section`)
      }
    }
    
    return { valid: issues.length === 0, issues, warnings, length: text.length }
  }

  const currentValidation = validatePrompt(prompt)

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Edit System Prompt - {mode.replace('_', ' ').toUpperCase()}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            ✕
          </button>
        </div>

        {loading && (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-2 text-gray-600 dark:text-gray-400">Loading prompt...</p>
          </div>
        )}

        {!loading && (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                System Prompt
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="w-full h-96 p-3 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Enter system prompt..."
              />
              <div className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                {prompt.length} characters, {prompt.split(' ').length} words
              </div>
            </div>

            {/* Validation Results */}
            {currentValidation && (
              <div className="mb-4">
                {currentValidation.issues.length > 0 && (
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-3 mb-2">
                    <h4 className="text-sm font-medium text-red-800 dark:text-red-200 mb-1">Issues:</h4>
                    <ul className="text-sm text-red-700 dark:text-red-300 list-disc list-inside">
                      {currentValidation.issues.map((issue: string, index: number) => (
                        <li key={index}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {currentValidation.warnings.length > 0 && (
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md p-3 mb-2">
                    <h4 className="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-1">Suggestions:</h4>
                    <ul className="text-sm text-yellow-700 dark:text-yellow-300 list-disc list-inside">
                      {currentValidation.warnings.map((warning: string, index: number) => (
                        <li key={index}>{warning}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-3 mb-4">
                <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
              </div>
            )}

            <div className="flex justify-end space-x-3">
              <button
                onClick={handleReset}
                disabled={saving}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50"
              >
                Reset to Default
              </button>
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving || !currentValidation.valid}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving ? 'Saving...' : 'Save Prompt'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}