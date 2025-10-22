'use client'

import { Message } from '@/lib/store'
import { MessageBubble } from './MessageBubble'
import { TypingIndicator } from './TypingIndicator'

interface MessageListProps {
  messages: Message[]
}

export function MessageList({ messages }: MessageListProps) {
  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center">
          <div className="text-6xl mb-4">🤖</div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Ready to help with your trading strategies
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Ask me anything about your trading notes, strategies, or market analysis
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-4">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
    </div>
  )
}