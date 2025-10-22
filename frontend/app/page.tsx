'use client'

import { useEffect } from 'react'
import { useStore } from '@/lib/store'
import { ChatInterface } from '@/components/ChatInterface'
import { Sidebar } from '@/components/Sidebar'
import { Header } from '@/components/Header'
import { LoadingScreen } from '@/components/LoadingScreen'

export default function Home() {
  const { 
    sidebarOpen, 
    currentChatId, 
    chats, 
    initializeApp,
    isLoading 
  } = useStore()

  useEffect(() => {
    initializeApp()
  }, [initializeApp])

  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <Header />
        
        {/* Chat Interface */}
        <div className="flex-1 flex">
          {currentChatId ? (
            <ChatInterface />
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
                  Welcome to EminiPlayer RAG
                </h1>
                <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
                  Your advanced trading strategy assistant with Obsidian integration
                </p>
                <div className="space-y-4">
                  <button
                    onClick={() => useStore.getState().createChat('New Chat')}
                    className="btn btn-primary px-6 py-3 text-lg"
                  >
                    Start New Chat
                  </button>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Choose from {chats.length} existing chats or start fresh
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}