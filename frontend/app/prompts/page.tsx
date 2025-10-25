'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useStore } from '@/lib/store'
import { Sidebar } from '@/components/Sidebar'
import { Header } from '@/components/Header'
import { LoginForm } from '@/components/LoginForm'
import toast from 'react-hot-toast'
import { 
  PencilIcon, 
  ArrowPathIcon, 
  CheckIcon, 
  XMarkIcon 
} from '@heroicons/react/24/outline'

const PROMPT_MODES = [
  { id: 'rag_only', name: 'RAG Only', description: 'Search document knowledge base', icon: '📄' },
  { id: 'obsidian_only', name: 'Obsidian Only', description: 'Search personal notes', icon: '📚' },
  { id: 'web_only', name: 'Web Search', description: 'Search the web for information', icon: '🌐' },
  { id: 'research', name: 'Comprehensive Research', description: 'Deep research combining all sources', icon: '🔍' },
]

export default function PromptsPage() {
  const router = useRouter()
  const { authToken, isAuthenticated, checkAuth, login, logout } = useStore()
  const [isChecking, setIsChecking] = useState(true)
  const [loading, setLoading] = useState(false)
  const [prompts, setPrompts] = useState<Record<string, string>>({})
  const [editingMode, setEditingMode] = useState<string | null>(null)
  const [editValue, setEditValue] = useState('')
  
  useEffect(() => {
    const authenticated = checkAuth()
    setIsChecking(false)
    
    if (authenticated) {
      loadPrompts()
    }
  }, [checkAuth])
  
  const loadPrompts = async () => {
    try {
      setLoading(true)
      const loadedPrompts: Record<string, string> = {}
      
      for (const mode of PROMPT_MODES) {
        const response = await fetch(`/api/user-prompts/${mode.id}`, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          loadedPrompts[mode.id] = data.prompt || ''
        }
      }
      
      setPrompts(loadedPrompts)
    } catch (error) {
      console.error('Failed to load prompts:', error)
      toast.error('Failed to load prompts')
    } finally {
      setLoading(false)
    }
  }
  
  const handleEdit = (mode: string) => {
    setEditingMode(mode)
    setEditValue(prompts[mode] || '')
  }
  
  const handleSave = async () => {
    if (!editingMode) return
    
    try {
      const response = await fetch(`/api/user-prompts/${editingMode}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ prompt: editValue })
      })
      
      if (response.ok) {
        setPrompts(prev => ({ ...prev, [editingMode]: editValue }))
        setEditingMode(null)
        toast.success('Prompt saved successfully')
      } else {
        toast.error('Failed to save prompt')
      }
    } catch (error) {
      toast.error('Failed to save prompt')
      console.error('Save error:', error)
    }
  }
  
  const handleReset = async (mode: string) => {
    if (!confirm('Reset this prompt to default?')) return
    
    try {
      const response = await fetch(`/api/user-prompts/${mode}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      if (response.ok) {
        await loadPrompts()
        toast.success('Prompt reset to default')
      } else {
        toast.error('Failed to reset prompt')
      }
    } catch (error) {
      toast.error('Failed to reset prompt')
      console.error('Reset error:', error)
    }
  }

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
        
        {/* Main Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-6xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">System Prompts</h1>
              <p className="text-gray-600 dark:text-gray-400">Customize system prompts for each operating mode</p>
            </div>
            
            {loading ? (
              <div className="text-center py-12">
                <ArrowPathIcon className="w-8 h-8 text-primary-500 dark:text-primary-400 animate-spin mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400">Loading prompts...</p>
              </div>
            ) : (
              <div className="space-y-6">
                {PROMPT_MODES.map((mode) => (
                  <div
                    key={mode.id}
                    className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{mode.icon}</span>
                        <div>
                          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">{mode.name}</h2>
                          <p className="text-gray-600 dark:text-gray-400 text-sm">{mode.description}</p>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        {editingMode === mode.id ? (
                          <>
                            <button
                              onClick={handleSave}
                              className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                            >
                              <CheckIcon className="w-4 h-4" />
                              <span>Save</span>
                            </button>
                            <button
                              onClick={() => setEditingMode(null)}
                              className="flex items-center space-x-2 px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors"
                            >
                              <XMarkIcon className="w-4 h-4" />
                              <span>Cancel</span>
                            </button>
                          </>
                        ) : (
                          <>
                            <button
                              onClick={() => handleEdit(mode.id)}
                              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
                            >
                              <PencilIcon className="w-4 h-4" />
                              <span>Edit</span>
                            </button>
                            <button
                              onClick={() => handleReset(mode.id)}
                              className="flex items-center space-x-2 px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-lg transition-colors"
                            >
                              <ArrowPathIcon className="w-4 h-4" />
                              <span>Reset</span>
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                    
                    {editingMode === mode.id ? (
                      <textarea
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        rows={10}
                        className="w-full px-4 py-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
                        placeholder="Enter system prompt..."
                      />
                    ) : (
                      <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                        <pre className="text-gray-700 dark:text-gray-300 text-sm whitespace-pre-wrap font-mono">
                          {prompts[mode.id] || 'No custom prompt set - using default'}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
