'use client'

import { useState, useRef, useEffect } from 'react'
import { useStore } from '@/lib/store'
import { PaperAirplaneIcon, StopIcon } from '@heroicons/react/24/outline'
import { MessageBubble } from './MessageBubble'
import { SourceList } from './SourceList'
import { EnhancedLoading, TypingIndicator } from './EnhancedLoading'
import { UIEnhancements } from './UIEnhancements'

export function EnhancedChatInterface() {
  const { 
    messages, 
    addMessage, 
    updateMessage, 
    isProcessing, 
    setProcessing,
    currentChatId,
    getCurrentModel,
    settings
  } = useStore()
  
  const [input, setInput] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!input.trim() || isSubmitting) return

    const userMessage = input.trim()
    setInput('')
    setIsSubmitting(true)

    // Add user message
    addMessage({
      role: 'user',
      content: userMessage
    })

    // Add processing message
    const assistantMessageId = crypto.randomUUID()
    addMessage({
      role: 'assistant',
      content: '',
      isProcessing: true
    })

    try {
      const response = await fetch('/api/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
          query: userMessage,
          mode: 'qa',
          model: getCurrentModel(),
          temperature: settings.temperature,
          max_tokens: settings.maxTokens,
          top_k_sampling: settings.topKSampling,
          conversation_history: messages.slice(-10) // Last 10 messages for context
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      // Update the processing message with the actual response
      updateMessage(assistantMessageId, {
        content: data.answer,
        sources: data.sources || [],
        totalSources: data.sources?.length || 0,
        mode: 'qa',
        model: getCurrentModel(),
        isProcessing: false
      })

    } catch (error: any) {
      console.error('Error sending message:', error)
      
      let errorMessage = 'Sorry, I encountered an error. Please try again.'
      
      if (error.response?.status === 401 || error.response?.status === 403) {
        errorMessage = 'Your session has expired. Please log in again.'
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error. Please try again in a moment.'
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. Please try again.'
      } else if (error.message?.includes('Network Error')) {
        errorMessage = 'Network error. Please check your connection.'
      }
      
      updateMessage(assistantMessageId, {
        content: errorMessage,
        isProcessing: false
      })
    } finally {
      setIsSubmitting(false)
      setProcessing(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleStopGeneration = () => {
    setProcessing(false)
    setIsSubmitting(false)
  }

  return (
    <>
      <UIEnhancements />
      <div className="flex-1 flex flex-col h-full">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto scrollbar-enhanced p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center max-w-md mx-auto">
                <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🤖</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Welcome to TradingAI Research Platform
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  Ask me anything about trading strategies, market analysis, or financial research. 
                  I can help you with RAG-based document analysis, web search, and comprehensive research.
                </p>
                <div className="grid grid-cols-1 gap-3">
                  <button
                    onClick={() => setInput("What trading strategies work best?")}
                    className="p-3 text-left bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="font-medium text-gray-900 dark:text-white">Trading Strategies</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Get insights on proven trading approaches</div>
                  </button>
                  <button
                    onClick={() => setInput("What's the current market trend?")}
                    className="p-3 text-left bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="font-medium text-gray-900 dark:text-white">Market Analysis</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Real-time market insights and trends</div>
                  </button>
                  <button
                    onClick={() => setInput("Explain risk management in trading")}
                    className="p-3 text-left bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="font-medium text-gray-900 dark:text-white">Risk Management</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Learn about protecting your capital</div>
                  </button>
                </div>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div key={message.id} className={`message-bubble ${message.role === 'user' ? 'user' : ''}`}>
                <MessageBubble message={message} />
              </div>
            ))
          )}
          
          {isProcessing && (
            <div className="message-bubble">
              <TypingIndicator />
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-900">
          <div className="flex items-end space-x-3">
            <div className="flex-1">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about trading, markets, or research..."
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none input-enhanced bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                rows={1}
                style={{ minHeight: '48px', maxHeight: '120px' }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement
                  target.style.height = 'auto'
                  target.style.height = Math.min(target.scrollHeight, 120) + 'px'
                }}
                disabled={isSubmitting}
              />
            </div>
            
            <div className="flex items-center space-x-2">
              {isSubmitting ? (
                <button
                  onClick={handleStopGeneration}
                  className="p-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors btn-enhanced"
                  title="Stop generation"
                >
                  <StopIcon className="h-5 w-5" />
                </button>
              ) : (
                <button
                  onClick={handleSendMessage}
                  disabled={!input.trim() || isSubmitting}
                  className="p-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors btn-enhanced"
                  title="Send message"
                >
                  <PaperAirplaneIcon className="h-5 w-5" />
                </button>
              )}
            </div>
          </div>
          
          <div className="mt-2 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center space-x-4">
              <span>Model: {getCurrentModel()}</span>
              <span>Mode: {settings.enableRAG ? 'RAG' : 'Web'}</span>
            </div>
            <div>
              Press Enter to send, Shift+Enter for new line
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

