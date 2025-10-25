'use client'

import { useEffect, useState } from 'react'
import { useStore } from '@/lib/store'
import { LoginForm } from './LoginForm'
import { ChatInterface } from './ChatInterface'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import { usePathname } from 'next/navigation'

export function AuthWrapper({ children }: { children?: React.ReactNode }) {
  const { isAuthenticated, checkAuth, login, logout } = useStore()
  const [isChecking, setIsChecking] = useState(true)
  const pathname = usePathname()

  useEffect(() => {
    // Check if user is already authenticated
    const authenticated = checkAuth()
    setIsChecking(false)
  }, [checkAuth])

  const handleLogin = (token: string, user: any) => {
    login(token, user)
  }

  const handleLogout = () => {
    logout()
  }

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <LoginForm onLogin={handleLogin} />
  }

  // If children are provided (like for specific pages), render them
  if (children) {
    return <>{children}</>
  }

  // Default chat interface for home page
  return (
    <div className="h-screen flex bg-gray-50 dark:bg-gray-900">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header onLogout={handleLogout} />
        <ChatInterface />
      </div>
    </div>
  )
}