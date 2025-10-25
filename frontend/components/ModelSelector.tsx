import React, { useState } from 'react'
import { useStore } from '../lib/store'
import { ArrowPathIcon } from '@heroicons/react/24/outline'

interface ModelSelectorProps {
  chatId?: string
  className?: string
}

export function ModelSelector({ chatId, className = '' }: ModelSelectorProps) {
  const { 
    models, 
    getCurrentModel, 
    getChatModel, 
    switchModel,
    refreshModels
  } = useStore()
  
  const [refreshing, setRefreshing] = useState(false)

  const currentModel = chatId ? getChatModel(chatId) : getCurrentModel()

  const handleModelChange = (model: string) => {
    switchModel(model)
  }
  
  const handleRefresh = async () => {
    setRefreshing(true)
    await refreshModels()
    setRefreshing(false)
  }

  if (models.length === 0) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          Loading models...
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="p-1 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700 disabled:opacity-50"
          title="Refresh models"
        >
          <ArrowPathIcon className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>
    )
  }

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <label htmlFor="model-select" className="text-sm font-medium text-gray-700 dark:text-gray-300">
        Model:
      </label>
      <select
        id="model-select"
        value={currentModel}
        onChange={(e) => handleModelChange(e.target.value)}
        className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        {models.map((model) => (
          <option key={model.name} value={model.name}>
            {model.name} ({Math.round(model.size / 1024 / 1024 / 1024)}GB)
          </option>
        ))}
      </select>
      <button
        onClick={handleRefresh}
        disabled={refreshing}
        className="p-1 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700 disabled:opacity-50"
        title="Refresh models"
      >
        <ArrowPathIcon className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
      </button>
    </div>
  )
}