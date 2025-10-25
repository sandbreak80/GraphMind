'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useStore } from '@/lib/store'
import { Sidebar } from '@/components/Sidebar'
import { Header } from '@/components/Header'
import { LoginForm } from '@/components/LoginForm'
import toast from 'react-hot-toast'

export default function SettingsPage() {
  const router = useRouter()
  const { authToken, isAuthenticated, checkAuth, login, logout } = useStore()
  const [isChecking, setIsChecking] = useState(true)
  const [loading, setLoading] = useState(false)
  const [testingConnection, setTestingConnection] = useState(false)
  
  // Obsidian settings
  const [obsidianVaultPath, setObsidianVaultPath] = useState('')
  const [obsidianApiUrl, setObsidianApiUrl] = useState('https://localhost:27124')
  const [obsidianApiKey, setObsidianApiKey] = useState('')
  const [obsidianEnabled, setObsidianEnabled] = useState(false)
  
  useEffect(() => {
    const authenticated = checkAuth()
    setIsChecking(false)
    
    if (authenticated) {
      loadSettings()
    }
  }, [checkAuth])
  
  const loadSettings = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/settings', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setObsidianVaultPath(data.obsidian_vault_path || '')
        setObsidianApiUrl(data.obsidian_api_url || 'https://localhost:27124')
        setObsidianApiKey(data.obsidian_api_key || '')
        setObsidianEnabled(data.obsidian_enabled || false)
      }
    } catch (error) {
      console.error('Failed to load settings:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const testObsidianConnection = async () => {
    if (!obsidianApiUrl) {
      toast.error('Please enter Obsidian API URL')
      return
    }
    
    try {
      setTestingConnection(true)
      const response = await fetch('/api/settings/test-obsidian', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
          vault_path: obsidianVaultPath,
          api_url: obsidianApiUrl,
          api_key: obsidianApiKey
        })
      })
      
      const data = await response.json()
      
      if (response.ok && data.success) {
        toast.success(`Connected! Found ${data.note_count} notes`)
      } else {
        toast.error(data.message || 'Connection failed')
      }
    } catch (error) {
      toast.error('Failed to test connection')
      console.error('Connection test error:', error)
    } finally {
      setTestingConnection(false)
    }
  }
  
  const saveSettings = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
          obsidian_vault_path: obsidianVaultPath,
          obsidian_api_url: obsidianApiUrl,
          obsidian_api_key: obsidianApiKey,
          obsidian_enabled: obsidianEnabled
        })
      })
      
      if (response.ok) {
        toast.success('Settings saved successfully')
      } else {
        const data = await response.json()
        toast.error(data.message || 'Failed to save settings')
      }
    } catch (error) {
      toast.error('Failed to save settings')
      console.error('Save settings error:', error)
    } finally {
      setLoading(false)
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
          <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Settings</h1>
              <p className="text-gray-600 dark:text-gray-400">Configure your GraphMind experience</p>
            </div>
            
            {/* Obsidian Configuration */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-1">Obsidian Integration</h2>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">Connect your Obsidian vault for personal knowledge retrieval</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={obsidianEnabled}
                    onChange={(e) => setObsidianEnabled(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 dark:bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
              
              {obsidianEnabled && (
                <div className="space-y-4 mt-6">
                  {/* Vault Path */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Vault Path
                      <span className="text-gray-500 dark:text-gray-400 ml-2 font-normal">(optional)</span>
                    </label>
                    <input
                      type="text"
                      value={obsidianVaultPath}
                      onChange={(e) => setObsidianVaultPath(e.target.value)}
                      placeholder="/path/to/obsidian/vault"
                      className="w-full px-4 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  
                  {/* API URL */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Obsidian API URL
                      <span className="text-red-600 dark:text-red-400 ml-1">*</span>
                    </label>
                    <input
                      type="text"
                      value={obsidianApiUrl}
                      onChange={(e) => setObsidianApiUrl(e.target.value)}
                      placeholder="https://localhost:27124"
                      className="w-full px-4 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      The URL where your Obsidian Local REST API is running
                    </p>
                  </div>
                  
                  {/* API Key */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      API Key
                      <span className="text-gray-500 dark:text-gray-400 ml-2 font-normal">(optional)</span>
                    </label>
                    <input
                      type="password"
                      value={obsidianApiKey}
                      onChange={(e) => setObsidianApiKey(e.target.value)}
                      placeholder="Enter API key if required"
                      className="w-full px-4 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  
                  {/* Test Connection Button */}
                  <button
                    onClick={testObsidianConnection}
                    disabled={testingConnection || !obsidianApiUrl}
                    className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
                  >
                    {testingConnection ? 'Testing Connection...' : 'Test Connection'}
                  </button>
                  
                  {/* Setup Instructions */}
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mt-4">
                    <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-400 mb-2">Setup Instructions:</h3>
                    <ol className="text-xs text-gray-700 dark:text-gray-400 space-y-1 list-decimal list-inside">
                      <li>Install the "Local REST API" plugin in Obsidian</li>
                      <li>Enable the plugin in Obsidian Settings → Community Plugins</li>
                      <li>Configure the plugin to run on port 27124 (or your custom port)</li>
                      <li>Copy the API URL and paste it above</li>
                      <li>If using HTTPS with self-signed certificates, you may need to accept the certificate</li>
                    </ol>
                  </div>
                </div>
              )}
            </div>
            
            {/* Save Button */}
            <div className="flex gap-4">
              <button
                onClick={saveSettings}
                disabled={loading}
                className="flex-1 py-3 px-6 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors"
              >
                {loading ? 'Saving...' : 'Save Settings'}
              </button>
              
              <button
                onClick={() => router.back()}
                className="px-6 py-3 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
