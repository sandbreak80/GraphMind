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
  const [selectedMode, setSelectedMode] = useState<'qa' | 'spec' | 'obsidian'>('obsidian')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isStreaming || isProcessing) return

    const userMessage = inputValue.trim()
    setInputValue('')

    // Set processing state
    setProcessing(true)

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
      // Call the appropriate API method based on mode and settings
      let response
      if (selectedMode === 'obsidian' && settings.enableObsidian) {
        response = await apiClient.askObsidian({
          query: userMessage,
          mode: selectedMode,
          top_k: settings.topK,
          temperature: settings.temperature,
          max_tokens: settings.maxTokens
        })
      } else if (settings.enableWebSearch) {
        response = await apiClient.askEnhanced({
          query: userMessage,
          mode: selectedMode,
          top_k: settings.topK,
          temperature: settings.temperature,
          max_tokens: settings.maxTokens
        })
      } else {
        response = await apiClient.ask({
          query: userMessage,
          mode: selectedMode,
          top_k: settings.topK,
          temperature: settings.temperature,
          max_tokens: settings.maxTokens
        })
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
              : selectedMode === 'obsidian' 
              ? "Ask about your trading strategies..." 
              : selectedMode === 'spec'
              ? "Generate a trading strategy specification..."
              : "Ask a question..."
          }
        />
      </div>
    </div>
  )
}