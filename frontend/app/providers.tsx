'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { useStore } from '@/lib/store'

interface ProvidersProps {
  children: React.ReactNode
}

export function Providers({ children }: ProvidersProps) {
  const { initializeApp, theme } = useStore()
  
  useEffect(() => {
    initializeApp()
  }, [initializeApp])

  // Apply theme to html element whenever it changes
  useEffect(() => {
    if (typeof window === 'undefined') return
    
    const root = document.documentElement
    root.classList.remove('light', 'dark')
    root.classList.add(theme)
    root.setAttribute('data-theme', theme)
  }, [theme])

  return <>{children}</>
}