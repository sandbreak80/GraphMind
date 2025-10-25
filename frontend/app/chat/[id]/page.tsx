'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useStore } from '@/lib/store'
import { LoginForm } from '@/components/LoginForm'
import { Sidebar } from '@/components/Sidebar'
import { Header } from '@/components/Header'
import { ChatInterface } from '@/components/ChatInterface'
import { EnhancedChatInterface } from '@/components/EnhancedChatInterface'
import { UIEnhancements } from '@/components/UIEnhancements'

export default function ChatPage() {
  const params = useParams()
  const router = useRouter()
  const { isAuthenticated, checkAuth, login, logout, chats, setCurrentChat } = useStore()
  const [isChecking, setIsChecking] = useState(true)
  const [chatExists, setChatExists] = useState(false)

  const chatId = params.id as string

  useEffect(() => {
    // Check if user is already authenticated
    const authenticated = checkAuth()
    setIsChecking(false)

    if (authenticated && chatId) {
      // Check if the chat exists
      const chat = chats.find(c => c.id === chatId)
      if (chat) {
        setChatExists(true)
        setCurrentChat(chatId)
      } else {
        // Chat doesn't exist, create a new one instead of showing error
        const { createChat } = useStore.getState()
        const newChatId = createChat('New Chat')
        router.push(`/chat/${newChatId}`)
      }
    }
  }, [chatId, chats, checkAuth, setCurrentChat, router])

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

  if (!chatExists) {
    // Show loading while creating new chat
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Creating new chat...</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <UIEnhancements />
      <div className="h-screen flex bg-gray-50 dark:bg-gray-900">
        <Sidebar />
        <div className="flex-1 flex flex-col">
          <Header onLogout={handleLogout} />
          <EnhancedChatInterface />
        </div>
      </div>
    </>
  )
}
