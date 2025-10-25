'use client'

import { useState, useEffect } from 'react'
import { useStore } from '@/lib/store'
import { 
  SunIcon, 
  MoonIcon, 
  ComputerDesktopIcon 
} from '@heroicons/react/24/outline'

export function ThemeToggle() {
  const { theme, setTheme, settings } = useStore()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="p-2 rounded-md bg-gray-100 dark:bg-gray-700">
        <SunIcon className="h-5 w-5 text-gray-400" />
      </div>
    )
  }

  const cycleTheme = () => {
    const themes = ['light', 'dark', 'system'] as const
    const currentIndex = themes.indexOf(settings.theme)
    const nextIndex = (currentIndex + 1) % themes.length
    const newTheme = themes[nextIndex]
    
    // Update settings first
    useStore.getState().updateSettings({ theme: newTheme })
    
    // Then apply the actual theme to the UI
    if (newTheme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      setTheme(systemTheme)
    } else {
      setTheme(newTheme)
    }
    
    // Force a re-render by updating the component state
    setMounted(false)
    setTimeout(() => setMounted(true), 0)
  }

  const getIcon = () => {
    if (settings.theme === 'system') {
      return <ComputerDesktopIcon className="h-5 w-5" />
    }
    return theme === 'dark' ? <MoonIcon className="h-5 w-5" /> : <SunIcon className="h-5 w-5" />
  }

  const getTooltip = () => {
    if (settings.theme === 'system') {
      return 'System theme (follows OS)'
    }
    return theme === 'dark' ? 'Dark mode' : 'Light mode'
  }

  return (
    <button
      onClick={cycleTheme}
      className="p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700 transition-all duration-200 hover:scale-105"
      title={getTooltip()}
    >
      {getIcon()}
    </button>
  )
}
