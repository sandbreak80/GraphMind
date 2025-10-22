'use client'

import { useState } from 'react'
import { useStore } from '@/lib/store'
import { 
  Bars3Icon, 
  Cog6ToothIcon, 
  SunIcon, 
  MoonIcon,
  ComputerDesktopIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline'
import { SettingsModal } from './SettingsModal'

interface HeaderProps {
  onLogout: () => void
}

export function Header({ onLogout }: HeaderProps) {
  const { 
    sidebarOpen, 
    setSidebarOpen, 
    theme, 
    setTheme,
    settings,
    user
  } = useStore()
  const [showSettings, setShowSettings] = useState(false)

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    useStore.getState().updateSettings({ theme: newTheme })
  }

  return (
    <>
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700"
            >
              <Bars3Icon className="h-5 w-5" />
            </button>
            
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                EminiPlayer RAG
              </h1>
              <div className="flex items-center space-x-1 text-xs text-gray-500 dark:text-gray-400">
                <div className={`w-2 h-2 rounded-full ${settings.enableRAG ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                <span>RAG</span>
                <div className={`w-2 h-2 rounded-full ${settings.enableObsidian ? 'bg-blue-500' : 'bg-gray-300'}`}></div>
                <span>Obsidian</span>
                <div className={`w-2 h-2 rounded-full ${settings.enableWebSearch ? 'bg-purple-500' : 'bg-gray-300'}`}></div>
                <span>Web</span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Welcome, {user?.username}
            </div>
            
            <button
              onClick={toggleTheme}
              className="p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700"
            >
              {theme === 'light' ? (
                <MoonIcon className="h-5 w-5" />
              ) : (
                <SunIcon className="h-5 w-5" />
              )}
            </button>
            
            <button
              onClick={() => setShowSettings(true)}
              className="p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700"
            >
              <Cog6ToothIcon className="h-5 w-5" />
            </button>
            
            <button
              onClick={onLogout}
              className="p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700"
              title="Logout"
            >
              <ArrowRightOnRectangleIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </header>

      <SettingsModal 
        isOpen={showSettings} 
        onClose={() => setShowSettings(false)} 
      />
    </>
  )
}