'use client'

import { useState, useEffect } from 'react'
import { useStore } from '@/lib/store'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { apiClient } from '@/lib/api'
import toast from 'react-hot-toast'

interface SettingsModalProps {
  isOpen: boolean
  onClose: () => void
}

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const { 
    settings, 
    updateSettings, 
    models, 
    setModels,
    selectedModel,
    setSelectedModel 
  } = useStore()
  
  const [localSettings, setLocalSettings] = useState(settings)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setLocalSettings(settings)
      loadModels()
    }
  }, [isOpen, settings])

  const loadModels = async () => {
    try {
      const data = await apiClient.getModels()
      setModels(data.models)
    } catch (error) {
      console.error('Failed to load models:', error)
      toast.error('Failed to load models')
    }
  }

  const handleSave = async () => {
    setIsLoading(true)
    try {
      updateSettings(localSettings)
      setSelectedModel(localSettings.selectedModel)
      toast.success('Settings saved successfully')
      onClose()
    } catch (error) {
      console.error('Failed to save settings:', error)
      toast.error('Failed to save settings')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setLocalSettings(settings)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Settings
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {/* Model Selection */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Model Selection
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Ollama Model
                </label>
                <select
                  value={localSettings.selectedModel}
                  onChange={(e) => setLocalSettings({ ...localSettings, selectedModel: e.target.value })}
                  className="input w-full"
                >
                  {models.map((model) => (
                    <option key={model.name} value={model.name}>
                      {model.name} ({model.details.parameter_size})
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Model Parameters */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Model Parameters
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Temperature
                </label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={localSettings.temperature}
                  onChange={(e) => setLocalSettings({ ...localSettings, temperature: parseFloat(e.target.value) })}
                  className="w-full"
                />
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {localSettings.temperature}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Max Tokens
                </label>
                <input
                  type="number"
                  min="100"
                  max="32000"
                  step="100"
                  value={localSettings.maxTokens}
                  onChange={(e) => setLocalSettings({ ...localSettings, maxTokens: parseInt(e.target.value) })}
                  className="input w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Top K
                </label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={localSettings.topK}
                  onChange={(e) => setLocalSettings({ ...localSettings, topK: parseInt(e.target.value) })}
                  className="input w-full"
                />
              </div>
            </div>
          </div>

          {/* Feature Toggles */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Features
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    RAG (Document Search)
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Enable document knowledge base search
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={localSettings.enableRAG}
                    onChange={(e) => setLocalSettings({ ...localSettings, enableRAG: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Obsidian Integration
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Search your personal Obsidian notes
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={localSettings.enableObsidian}
                    onChange={(e) => setLocalSettings({ ...localSettings, enableObsidian: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Web Search
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Enable real-time web search via SearXNG
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={localSettings.enableWebSearch}
                    onChange={(e) => setLocalSettings({ ...localSettings, enableWebSearch: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={handleReset}
            className="btn btn-secondary"
            disabled={isLoading}
          >
            Reset
          </button>
          <button
            onClick={handleSave}
            className="btn btn-primary"
            disabled={isLoading}
          >
            {isLoading ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  )
}