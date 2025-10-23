import React from 'react'
import { useStore } from '../lib/store'

interface ModelSelectorProps {
  chatId?: string
  className?: string
}

export function ModelSelector({ chatId, className = '' }: ModelSelectorProps) {
  const { 
    models, 
    getCurrentModel, 
    getChatModel, 
    switchModel 
  } = useStore()

  const currentModel = chatId ? getChatModel(chatId) : getCurrentModel()

  const handleModelChange = (model: string) => {
    switchModel(model)
  }

  if (models.length === 0) {
    return (
      <div className={`text-sm text-gray-500 ${className}`}>
        Loading models...
      </div>
    )
  }

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <label htmlFor="model-select" className="text-sm font-medium text-gray-700">
        Model:
      </label>
      <select
        id="model-select"
        value={currentModel}
        onChange={(e) => handleModelChange(e.target.value)}
        className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        {models.map((model) => (
          <option key={model.name} value={model.name}>
            {model.name} ({Math.round(model.size / 1024 / 1024 / 1024)}GB)
          </option>
        ))}
      </select>
    </div>
  )
}