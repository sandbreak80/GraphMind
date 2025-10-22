'use client'

import { useState, useRef, useEffect } from 'react'
import { useStore } from '@/lib/store'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'
import { ChatControls } from './ChatControls'
import { apiClient } from '@/lib/api'

export function ChatInterface() {
  const { 
    messages, 
    addMessage, 
    updateMessage, 
    isStreaming,
    isProcessing,
    setProcessing,
    settings 
  } = useStore()
  
  const [inputValue, setInputValue] = useState('')
  const [selectedMode, setSelectedMode] = useState<'obsidian-only' | 'rag-only' | 'web-only'>('obsidian-only')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    // Only scroll to bottom when a new message is added, not when content is updated
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1]
      // Only scroll if it's a new message (not a content update)
      if (lastMessage.role === 'user' || !lastMessage.isProcessing) {
        scrollToBottom()
      }
    }
  }, [messages.length]) // Only trigger on message count change, not content changes

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isStreaming || isProcessing) return

    const userMessage = inputValue.trim()
    setInputValue('')

    // Set processing state
    setProcessing(true)

    // Create new chat if none exists
    const { currentChatId, createChatWithAutoName } = useStore.getState()
    if (!currentChatId) {
      createChatWithAutoName(userMessage)
    }

    // Add user message
    addMessage({
      content: userMessage,
      role: 'user'
    })

    // Add assistant message placeholder with processing status
    addMessage({
      content: 'Processing your request... This may take a few minutes for complex queries.',
      role: 'assistant',
      isProcessing: true
    })
    
    // Get the ID of the last message (the one we just added)
    const { messages: currentMessages } = useStore.getState()
    const assistantMessageId = currentMessages[currentMessages.length - 1]?.id

    try {
      // Prepare conversation history (exclude the current message and processing message)
      const conversationHistory = messages
        .filter(msg => msg.role !== 'assistant' || !msg.isProcessing)
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }))

      // Prepare request object
      const request = {
        query: userMessage,
        mode: 'qa' as const,
        top_k: settings.topK,
        temperature: settings.temperature,
        max_tokens: settings.maxTokens,
        conversation_history: conversationHistory
      }

      // Call the appropriate API method based on selected mode
      let response
      if (selectedMode === 'obsidian-only') {
        response = await apiClient.askObsidian(request)
      } else if (selectedMode === 'web-only') {
        response = await apiClient.askEnhanced(request)
      } else if (selectedMode === 'rag-only') {
        response = await apiClient.ask(request)
      }

      // Check if response is valid
      if (!response) {
        throw new Error('No response received from API')
      }

      // Update assistant message with response
      updateMessage(assistantMessageId, {
        content: response.answer,
        sources: response.citations,
        mode: response.mode,
        totalSources: response.total_sources,
        isProcessing: false
      })

    } catch (error) {
      console.error('Error sending message:', error)
      updateMessage(assistantMessageId, {
        content: 'Sorry, I encountered an error. Please try again.',
        isProcessing: false
      })
    } finally {
      // Clear processing state
      setProcessing(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex-1 flex flex-col bg-white dark:bg-gray-900">
      {/* Chat Controls */}
      <ChatControls 
        selectedMode={selectedMode}
        onModeChange={setSelectedMode}
      />

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-4">
        <MessageInput
          value={inputValue}
          onChange={setInputValue}
          onSend={handleSendMessage}
          onKeyPress={handleKeyPress}
          disabled={isStreaming || isProcessing}
          placeholder={
            isProcessing 
              ? "Processing your request... Please wait..."
              : selectedMode === 'obsidian-only' 
              ? "Ask about your personal trading notes..." 
              : selectedMode === 'web-only'
              ? "Search the web for real-time information..."
              : "Ask about the trading strategy knowledge base..."
          }
        />
      </div>
    </div>
  )
}