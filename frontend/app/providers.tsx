'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { useStore } from '@/lib/store'

interface ProvidersProps {
  children: React.ReactNode
}

export function Providers({ children }: ProvidersProps) {
  const { initializeApp } = useStore()
  
  useEffect(() => {
    initializeApp()
  }, [initializeApp])

  return <>{children}</>
}