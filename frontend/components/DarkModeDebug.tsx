'use client'

import { useEffect, useState } from 'react'
import { useStore } from '@/lib/store'

export function DarkModeDebug() {
  const { theme, settings } = useStore()
  const [domTheme, setDomTheme] = useState<string>('')
  const [localStorageTheme, setLocalStorageTheme] = useState<string>('')

  useEffect(() => {
    if (typeof window === 'undefined') return

    // Check DOM classes
    const root = document.documentElement
    const classes = Array.from(root.classList)
    const darkClass = classes.includes('dark')
    const lightClass = classes.includes('light')
    setDomTheme(darkClass ? 'dark' : lightClass ? 'light' : 'none')

    // Check localStorage
    const stored = localStorage.getItem('theme')
    setLocalStorageTheme(stored || 'none')

    // Listen for theme changes
    const observer = new MutationObserver(() => {
      const newClasses = Array.from(root.classList)
      const newDarkClass = newClasses.includes('dark')
      const newLightClass = newClasses.includes('light')
      setDomTheme(newDarkClass ? 'dark' : newLightClass ? 'light' : 'none')
    })

    observer.observe(root, { attributes: true, attributeFilter: ['class'] })

    return () => observer.disconnect()
  }, [])

  return (
    <div className="fixed bottom-4 left-4 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg p-3 text-xs font-mono z-50">
      <div className="space-y-1">
        <div>Store Theme: <span className="text-blue-600 dark:text-blue-400">{theme}</span></div>
        <div>Settings Theme: <span className="text-green-600 dark:text-green-400">{settings.theme}</span></div>
        <div>DOM Classes: <span className="text-purple-600 dark:text-purple-400">{domTheme}</span></div>
        <div>LocalStorage: <span className="text-orange-600 dark:text-orange-400">{localStorageTheme}</span></div>
        <div>Data Attribute: <span className="text-red-600 dark:text-red-400">{typeof window !== 'undefined' ? document.documentElement.getAttribute('data-theme') || 'none' : 'none'}</span></div>
      </div>
    </div>
  )
}
