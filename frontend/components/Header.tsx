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
import { ThemeToggle } from './ThemeToggle'

interface HeaderProps {
  onLogout: () => void
}

export function Header({ onLogout }: HeaderProps) {
  const { 
    sidebarOpen, 
    setSidebarOpen, 
    settings,
    user,
    createChat
  } = useStore()
  const [showSettings, setShowSettings] = useState(false)

  const handleTitleClick = () => {
    // Navigate to homepage
    if (typeof window !== 'undefined') {
      window.location.href = '/'
    }
  }

  return (
    <>
      <header className="sticky top-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg border-b border-gray-200/50 dark:border-gray-700/50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Left Section */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100/80 dark:text-gray-400 dark:hover:text-gray-100 dark:hover:bg-gray-800/80 transition-all duration-200 active:scale-95"
                aria-label="Toggle sidebar"
              >
                <Bars3Icon className="h-6 w-6" />
              </button>
              
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleTitleClick}
                  className="group flex items-center space-x-2 transition-all duration-200"
                  title="Go to homepage"
                >
                  <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 shadow-md group-hover:shadow-lg transition-all duration-200">
                    <span className="text-white font-bold text-sm">GM</span>
                  </div>
                  <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent group-hover:from-blue-700 group-hover:to-purple-700 transition-all duration-200">
                    GraphMind
                  </span>
                </button>
                
                {/* Status Indicators */}
                <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-gray-100/80 dark:bg-gray-800/80 border border-gray-200/50 dark:border-gray-700/50">
                  <div className="flex items-center space-x-1.5">
                    <div className={`w-2 h-2 rounded-full transition-all duration-300 ${settings.enableRAG ? 'bg-green-500 shadow-sm shadow-green-500/50' : 'bg-gray-300 dark:bg-gray-600'}`} title="RAG Documents"></div>
                    <span className="text-xs font-medium text-gray-600 dark:text-gray-400">Docs</span>
                  </div>
                  <div className="w-px h-3 bg-gray-300 dark:bg-gray-600"></div>
                  <div className="flex items-center space-x-1.5">
                    <div className={`w-2 h-2 rounded-full transition-all duration-300 ${settings.enableObsidian ? 'bg-blue-500 shadow-sm shadow-blue-500/50' : 'bg-gray-300 dark:bg-gray-600'}`} title="Obsidian Notes"></div>
                    <span className="text-xs font-medium text-gray-600 dark:text-gray-400">Obsidian</span>
                  </div>
                  <div className="w-px h-3 bg-gray-300 dark:bg-gray-600"></div>
                  <div className="flex items-center space-x-1.5">
                    <div className={`w-2 h-2 rounded-full transition-all duration-300 ${settings.enableWebSearch ? 'bg-purple-500 shadow-sm shadow-purple-500/50' : 'bg-gray-300 dark:bg-gray-600'}`} title="Web Search"></div>
                    <span className="text-xs font-medium text-gray-600 dark:text-gray-400">Web</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Section */}
            <div className="flex items-center space-x-3">
              <div className="hidden md:block text-sm font-medium text-gray-700 dark:text-gray-300">
                {user?.username}
              </div>
              
              <ThemeToggle />
              
              <button
                onClick={() => setShowSettings(true)}
                className="p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100/80 dark:text-gray-400 dark:hover:text-gray-100 dark:hover:bg-gray-800/80 transition-all duration-200 active:scale-95"
                aria-label="Settings"
              >
                <Cog6ToothIcon className="h-5 w-5" />
              </button>
              
              <button
                onClick={onLogout}
                className="p-2 rounded-lg text-gray-600 hover:text-red-600 hover:bg-red-50 dark:text-gray-400 dark:hover:text-red-400 dark:hover:bg-red-900/20 transition-all duration-200 active:scale-95"
                title="Logout"
                aria-label="Logout"
              >
                <ArrowRightOnRectangleIcon className="h-5 w-5" />
              </button>
            </div>
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