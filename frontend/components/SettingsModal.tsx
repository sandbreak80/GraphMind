'use client'

import { useState, useEffect } from 'react'
import { useStore } from '@/lib/store'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { apiClient } from '@/lib/api'
import { SystemPromptManager } from './SystemPromptManager'
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
  const [showSystemPrompts, setShowSystemPrompts] = useState(false)

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
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Configure LLM generation parameters for response quality and creativity.
            </p>
            <div className="grid grid-cols-3 gap-4">
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
                <div className="text-xs text-gray-400 mt-1">
                  <strong>Recommended:</strong> 0.1-0.3 (Focused: 0.1, Balanced: 0.2, Creative: 0.5)
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Max Tokens
                </label>
                <input
                  type="number"
                  min="1000"
                  max="16000"
                  step="500"
                  value={localSettings.maxTokens}
                  onChange={(e) => setLocalSettings({ ...localSettings, maxTokens: parseInt(e.target.value) })}
                  className="input w-full"
                />
                <div className="text-xs text-gray-400 mt-1">
                  <strong>Recommended:</strong> 4000-8000 (Short: 4K, Balanced: 8K, Long: 12K)
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Top-K Sampling
                </label>
                <input
                  type="number"
                  min="10"
                  max="100"
                  value={localSettings.topKSampling}
                  onChange={(e) => setLocalSettings({ ...localSettings, topKSampling: parseInt(e.target.value) })}
                  className="input w-full"
                />
                <div className="text-xs text-gray-400 mt-1">
                  <strong>Recommended:</strong> 20-60 (Focused: 20, Balanced: 40, Diverse: 60)
                </div>
              </div>
            </div>
            <div className="mt-3 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <p className="text-xs text-purple-700 dark:text-purple-300">
                <strong>LLM Parameters:</strong> Temperature controls creativity (0=focused, 1=creative), 
                Max Tokens limits response length, Top-K Sampling controls vocabulary diversity.
              </p>
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

          {/* Document Retrieval Settings */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Document Retrieval Settings
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Configure how many documents are retrieved and reranked for better responses.
            </p>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  BM25 Top K
                </label>
                <input
                  type="number"
                  min="10"
                  max="100"
                  value={localSettings.bm25TopK}
                  onChange={(e) => setLocalSettings({ ...localSettings, bm25TopK: parseInt(e.target.value) })}
                  className="input w-full"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Keyword search results
                </p>
                <div className="text-xs text-gray-400 mt-1">
                  <strong>Recommended:</strong> 20-50 (Fast: 20, Balanced: 30, Comprehensive: 50)
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Embedding Top K
                </label>
                <input
                  type="number"
                  min="10"
                  max="100"
                  value={localSettings.embeddingTopK}
                  onChange={(e) => setLocalSettings({ ...localSettings, embeddingTopK: parseInt(e.target.value) })}
                  className="input w-full"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Semantic search results
                </p>
                <div className="text-xs text-gray-400 mt-1">
                  <strong>Recommended:</strong> 20-50 (Fast: 20, Balanced: 30, Comprehensive: 50)
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Rerank Top K
                </label>
                <input
                  type="number"
                  min="5"
                  max="20"
                  value={localSettings.rerankTopK}
                  onChange={(e) => setLocalSettings({ ...localSettings, rerankTopK: parseInt(e.target.value) })}
                  className="input w-full"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Final results used
                </p>
                <div className="text-xs text-gray-400 mt-1">
                  <strong>Recommended:</strong> 5-12 (Fast: 5, Balanced: 8, Comprehensive: 12)
                </div>
              </div>
            </div>
            <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p className="text-xs text-blue-700 dark:text-blue-300">
                <strong>Hardware Profile:</strong> 100GB RAM + 24 CPU cores + 2x GPU - optimized for high performance.
                Higher values provide better recall but may increase response time by 0.5-2s.
              </p>
            </div>
            
            {/* Performance Presets */}
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Performance Presets</h4>
              <div className="grid grid-cols-3 gap-2">
                <button
                  onClick={() => setLocalSettings({
                    ...localSettings,
                    bm25TopK: 20,
                    embeddingTopK: 20,
                    rerankTopK: 5,
                    webSearchResults: 4,
                    webPagesToParse: 3
                  })}
                  className="px-3 py-2 text-xs font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600"
                >
                  ⚡ Fast
                  <div className="text-xs text-gray-500">~1-2s response</div>
                </button>
                <button
                  onClick={() => setLocalSettings({
                    ...localSettings,
                    bm25TopK: 30,
                    embeddingTopK: 30,
                    rerankTopK: 8,
                    webSearchResults: 6,
                    webPagesToParse: 4
                  })}
                  className="px-3 py-2 text-xs font-medium text-white bg-blue-600 border border-blue-600 rounded-md hover:bg-blue-700"
                >
                  ⚖️ Balanced
                  <div className="text-xs text-blue-200">~2-3s response</div>
                </button>
                <button
                  onClick={() => setLocalSettings({
                    ...localSettings,
                    bm25TopK: 50,
                    embeddingTopK: 50,
                    rerankTopK: 12,
                    webSearchResults: 8,
                    webPagesToParse: 6
                  })}
                  className="px-3 py-2 text-xs font-medium text-gray-700 bg-green-100 border border-green-300 rounded-md hover:bg-green-200 dark:bg-green-900 dark:text-green-300 dark:border-green-600 dark:hover:bg-green-800"
                >
                  🔍 Comprehensive
                  <div className="text-xs text-gray-500">~3-5s response</div>
                </button>
              </div>
            </div>
          </div>

          {/* Web Search Settings */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Web Search Settings
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Configure web search behavior for real-time information.
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Search Results
                </label>
                <input
                  type="number"
                  min="3"
                  max="20"
                  value={localSettings.webSearchResults}
                  onChange={(e) => setLocalSettings({ ...localSettings, webSearchResults: parseInt(e.target.value) })}
                  className="input w-full"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Number of web search results
                </p>
                <div className="text-xs text-gray-400 mt-1">
                  <strong>Recommended:</strong> 4-8 (Fast: 4, Balanced: 6, Comprehensive: 8)
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Pages to Parse
                </label>
                <input
                  type="number"
                  min="2"
                  max="10"
                  value={localSettings.webPagesToParse}
                  onChange={(e) => setLocalSettings({ ...localSettings, webPagesToParse: parseInt(e.target.value) })}
                  className="input w-full"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Pages to parse for content
                </p>
                <div className="text-xs text-gray-400 mt-1">
                  <strong>Recommended:</strong> 3-6 (Fast: 3, Balanced: 4, Comprehensive: 6)
                </div>
              </div>
            </div>
            <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <p className="text-xs text-green-700 dark:text-green-300">
                <strong>Performance Impact:</strong> Web search adds 1-3s to response time. 
                More results provide better real-time coverage but slower responses.
              </p>
            </div>
          </div>

          {/* System Prompts Section */}
          <div className="border-t border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              System Prompts
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Customize how the AI behaves in different chat modes by editing system prompts.
            </p>
            <button
              onClick={() => setShowSystemPrompts(true)}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Manage System Prompts
            </button>
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

      {/* System Prompt Manager */}
      <SystemPromptManager
        isOpen={showSystemPrompts}
        onClose={() => setShowSystemPrompts(false)}
      />
    </div>
  )
}