'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useStore } from '@/lib/store'
import { AuthWrapper } from '@/components/AuthWrapper'

export default function Home() {
  const router = useRouter()
  const { isAuthenticated, currentChatId, chats } = useStore()

  useEffect(() => {
    if (isAuthenticated) {
      if (currentChatId) {
        // Redirect to current chat
        router.push(`/chat/${currentChatId}`)
      } else if (chats.length > 0) {
        // Redirect to most recent chat
        const mostRecentChat = chats[0]
        router.push(`/chat/${mostRecentChat.id}`)
      } else {
        // Create a new chat
        const { createChat } = useStore.getState()
        const newChatId = createChat('New Chat')
        router.push(`/chat/${newChatId}`)
      }
    }
  }, [isAuthenticated, currentChatId, chats, router])

  return <AuthWrapper />
}