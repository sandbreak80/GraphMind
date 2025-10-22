'use client'

import { useStore } from '@/lib/store'
import { 
  GlobeAltIcon, 
  DocumentTextIcon, 
  BookOpenIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline'

interface ChatControlsProps {
  selectedMode: 'qa' | 'spec' | 'obsidian'
  onModeChange: (mode: 'qa' | 'spec' | 'obsidian') => void
}

export function ChatControls({ selectedMode, onModeChange }: ChatControlsProps) {
  const { settings, updateSettings } = useStore()

  const modes = [
    {
      id: 'obsidian' as const,
      name: 'Obsidian',
      description: 'Search your personal notes',
      icon: BookOpenIcon,
      enabled: settings.enableObsidian
    },
    {
      id: 'qa' as const,
      name: 'RAG',
      description: 'Document knowledge base',
      icon: DocumentTextIcon,
      enabled: settings.enableRAG
    },
    {
      id: 'spec' as const,
      name: 'Spec',
      description: 'Generate specifications',
      icon: Cog6ToothIcon,
      enabled: settings.enableRAG
    }
  ]

  return (
    <div className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Mode:
          </h3>
          <div className="flex space-x-2">
            {modes.map((mode) => {
              const Icon = mode.icon
              return (
                <button
                  key={mode.id}
                  onClick={() => onModeChange(mode.id)}
                  disabled={!mode.enabled}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedMode === mode.id
                      ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                      : mode.enabled
                      ? 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                      : 'text-gray-400 dark:text-gray-600 cursor-not-allowed'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{mode.name}</span>
                  {!mode.enabled && (
                    <span className="text-xs opacity-75">(disabled)</span>
                  )}
                </button>
              )
            })}
          </div>
        </div>

        <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${settings.enableRAG ? 'bg-green-500' : 'bg-gray-300'}`}></div>
            <span>RAG</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${settings.enableObsidian ? 'bg-blue-500' : 'bg-gray-300'}`}></div>
            <span>Obsidian</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${settings.enableWebSearch ? 'bg-purple-500' : 'bg-gray-300'}`}></div>
            <span>Web</span>
          </div>
        </div>
      </div>
    </div>
  )
}