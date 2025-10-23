'use client'

import { useState, useRef, useEffect } from 'react'
import { useStore } from '@/lib/store'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'
import { ChatControls } from './ChatControls'
import { ModelSelector } from './ModelSelector'
import { ResponseTimeDisplay, AverageResponseTime } from './ResponseTimeDisplay'
import { ChatExport } from './ChatExport'
import { apiClient } from '@/lib/api'

export function ChatInterface() {
  const { 
    messages, 
    addMessage, 
    updateMessage, 
    isProcessing,
    setProcessing,
    settings,
    currentChatId,
    getCurrentModel,
    updateResponseTime
  } = useStore()
  
  const [inputValue, setInputValue] = useState('')
  const [selectedMode, setSelectedMode] = useState<'obsidian-only' | 'rag-only' | 'web-only' | 'research'>('obsidian-only')
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
    if (!inputValue.trim() || isProcessing) return

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

    // Start timing the response
    const startTime = Date.now()

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
        top_k: settings.rerankTopK,  // Use rerankTopK for backward compatibility
        temperature: settings.temperature,
        max_tokens: settings.maxTokens,
        top_k_sampling: settings.topKSampling,  // New LLM sampling parameter
        model: getCurrentModel(),
        conversation_history: conversationHistory,
        // Document Retrieval Settings
        bm25_top_k: settings.bm25TopK,
        embedding_top_k: settings.embeddingTopK,
        rerank_top_k: settings.rerankTopK,
        // Web Search Settings
        web_search_results: settings.webSearchResults,
        web_pages_to_parse: settings.webPagesToParse
      }

      // Call the appropriate API method based on selected mode
      let response
      if (selectedMode === 'obsidian-only') {
        response = await apiClient.askObsidian(request)
      } else if (selectedMode === 'web-only') {
        response = await apiClient.askEnhanced(request)
      } else if (selectedMode === 'rag-only') {
        response = await apiClient.ask(request)
      } else if (selectedMode === 'research') {
        response = await apiClient.askResearch(request)
      }

      // Check if response is valid
      if (!response) {
        throw new Error('No response received from API')
      }

      // Calculate response time
      const responseTime = (Date.now() - startTime) / 1000

      // Update assistant message with response
      updateMessage(assistantMessageId, {
        content: response.answer,
        sources: response.citations,
        mode: response.mode,
        totalSources: response.total_sources,
        isProcessing: false
      })

      // Update response time
      updateResponseTime(assistantMessageId, responseTime)

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
      <div className="flex items-center justify-between border-b border-gray-200 dark:border-gray-700 p-4">
        <ChatControls 
          selectedMode={selectedMode}
          onModeChange={setSelectedMode}
        />
        <div className="flex items-center space-x-4">
          <ModelSelector chatId={currentChatId || undefined} />
          {currentChatId && <ChatExport chatId={currentChatId} />}
        </div>
      </div>

      {/* Chat Stats */}
      {currentChatId && (
        <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 px-4 py-2 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <AverageResponseTime chatId={currentChatId} />
          <div>Model: {getCurrentModel()}</div>
        </div>
      )}

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
          disabled={isProcessing}
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