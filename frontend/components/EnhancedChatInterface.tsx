'use client'

import { useState, useRef, useEffect } from 'react'
import { useStore } from '@/lib/store'
import { PaperAirplaneIcon, StopIcon } from '@heroicons/react/24/outline'
import { MessageBubble } from './MessageBubble'
import { SourceList } from './SourceList'
import { EnhancedLoading, TypingIndicator } from './EnhancedLoading'
import { UIEnhancements } from './UIEnhancements'
import { ChatControls } from './ChatControls'
import { ModelSelector } from './ModelSelector'
import { ChatExport } from './ChatExport'

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
  const [selectedMode, setSelectedMode] = useState<'obsidian-only' | 'rag-only' | 'web-only' | 'research'>('rag-only')
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
    addMessage({
      role: 'assistant',
      content: '',
      isProcessing: true
    })
    
    // Get the ID of the assistant message we just added
    const { messages: currentMessages } = useStore.getState()
    const assistantMessageId = currentMessages[currentMessages.length - 1]?.id

    try {
      // Determine the API endpoint based on selected mode
      let apiEndpoint = '/api/ask'
      if (selectedMode === 'obsidian-only') {
        apiEndpoint = '/api/ask-obsidian'
      } else if (selectedMode === 'web-only') {
        apiEndpoint = '/api/ask-enhanced'
      } else if (selectedMode === 'research') {
        apiEndpoint = '/api/ask-research'
      }

      const response = await fetch(apiEndpoint, {
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
          conversation_history: messages.slice(-10).map(m => ({
            role: m.role,
            content: m.content
          })),
          // Document Retrieval Settings
          bm25_top_k: settings.bm25TopK,
          embedding_top_k: settings.embeddingTopK,
          rerank_top_k: settings.rerankTopK,
          // Web Search Settings
          web_search_results: settings.webSearchResults,
          web_pages_to_parse: settings.webPagesToParse
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      // Update the processing message with the actual response
      updateMessage(assistantMessageId, {
        content: data.answer,
        sources: data.citations || data.sources || [],
        totalSources: data.total_sources || data.sources?.length || 0,
        mode: selectedMode,
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
        {/* Chat Controls */}
        <div className="flex items-center justify-between border-b border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-900">
          <ChatControls 
            selectedMode={selectedMode}
            onModeChange={setSelectedMode}
          />
          <div className="flex items-center space-x-4">
            <ModelSelector chatId={currentChatId || undefined} />
            {currentChatId && <ChatExport chatId={currentChatId} />}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto scrollbar-enhanced p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center max-w-md mx-auto">
                <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🤖</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Welcome to GraphMind
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                  Your open-source RAG framework for domain-agnostic research. 
                  I can help you with document analysis, web search, knowledge graphs, and comprehensive research across any domain.
                </p>
                <div className="grid grid-cols-1 gap-3">
                  <button
                    onClick={() => setInput("What are the key concepts in this domain?")}
                    className="p-3 text-left bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="font-medium text-sm text-gray-900 dark:text-white">Domain Research</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">Explore key concepts in any field</div>
                  </button>
                  <button
                    onClick={() => setInput("Summarize the latest research findings")}
                    className="p-3 text-left bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="font-medium text-sm text-gray-900 dark:text-white">Research Summary</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">Get comprehensive research insights</div>
                  </button>
                  <button
                    onClick={() => setInput("How can I analyze this data effectively?")}
                    className="p-3 text-left bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="font-medium text-sm text-gray-900 dark:text-white">Data Analysis</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">Learn effective analysis techniques</div>
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
                placeholder={
                  isSubmitting 
                    ? "Processing your request... Please wait..."
                    : selectedMode === 'obsidian-only' 
                    ? "Ask about your personal notes..." 
                    : selectedMode === 'web-only'
                    ? "Search the web for real-time information..."
                    : selectedMode === 'research'
                    ? "Ask me anything for comprehensive research..."
                    : "Ask about the document knowledge base..."
                }
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none input-enhanced bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 text-xs"
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
              <span>Mode: {
                selectedMode === 'obsidian-only' ? 'Obsidian Only' :
                selectedMode === 'web-only' ? 'Web Search' :
                selectedMode === 'research' ? 'Comprehensive Research' :
                'RAG Only'
              }</span>
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

