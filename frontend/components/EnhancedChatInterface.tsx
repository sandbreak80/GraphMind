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
            <div className="flex-1 flex items-center justify-center p-6">
              <div className="text-center max-w-4xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                  <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                    <span className="text-4xl">🧠</span>
                  </div>
                  <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-3">
                    Welcome to GraphMind
                  </h1>
                  <p className="text-base text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                    Advanced RAG framework with four powerful research modes
                  </p>
                </div>

                {/* Mode Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                  {/* RAG Documents Mode */}
                  <button
                    onClick={() => {
                      onModeChange?.('rag-only')
                      setInput("What insights can you extract from the uploaded documents?")
                    }}
                    className="group p-5 text-left bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 rounded-xl hover:shadow-lg transition-all border-2 border-blue-200 dark:border-blue-700 hover:border-blue-400 dark:hover:border-blue-500"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                        <span className="text-xl">📚</span>
                      </div>
                      <div className="flex-1">
                        <div className="font-bold text-base text-gray-900 dark:text-white mb-1">RAG Documents</div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          Query your uploaded PDFs, videos, and documents with AI-powered retrieval
                        </div>
                        <div className="text-xs text-blue-600 dark:text-blue-400 font-medium">
                          → Try: "Summarize the key points from my documents"
                        </div>
                      </div>
                    </div>
                  </button>

                  {/* Web Search Mode */}
                  <button
                    onClick={() => {
                      onModeChange?.('web-only')
                      setInput("What are the latest developments in AI research?")
                    }}
                    className="group p-5 text-left bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl hover:shadow-lg transition-all border-2 border-green-200 dark:border-green-700 hover:border-green-400 dark:hover:border-green-500"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                        <span className="text-xl">🌐</span>
                      </div>
                      <div className="flex-1">
                        <div className="font-bold text-base text-gray-900 dark:text-white mb-1">Web Search</div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          Get real-time information from the web with privacy-focused SearXNG
                        </div>
                        <div className="text-xs text-green-600 dark:text-green-400 font-medium">
                          → Try: "What's the latest news about quantum computing?"
                        </div>
                      </div>
                    </div>
                  </button>

                  {/* Obsidian Mode */}
                  <button
                    onClick={() => {
                      onModeChange?.('obsidian-only')
                      setInput("What connections exist in my personal knowledge base?")
                    }}
                    className="group p-5 text-left bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl hover:shadow-lg transition-all border-2 border-purple-200 dark:border-purple-700 hover:border-purple-400 dark:hover:border-purple-500"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                        <span className="text-xl">🗂️</span>
                      </div>
                      <div className="flex-1">
                        <div className="font-bold text-base text-gray-900 dark:text-white mb-1">Obsidian Notes</div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          Connect to your Obsidian vault for personalized knowledge retrieval
                        </div>
                        <div className="text-xs text-purple-600 dark:text-purple-400 font-medium">
                          → Try: "What have I written about project management?"
                        </div>
                      </div>
                    </div>
                  </button>

                  {/* Comprehensive Research Mode */}
                  <button
                    onClick={() => {
                      onModeChange?.('research')
                      setInput("Conduct comprehensive research on machine learning applications")
                    }}
                    className="group p-5 text-left bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 rounded-xl hover:shadow-lg transition-all border-2 border-orange-200 dark:border-orange-700 hover:border-orange-400 dark:hover:border-orange-500"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                        <span className="text-xl">🔬</span>
                      </div>
                      <div className="flex-1">
                        <div className="font-bold text-base text-gray-900 dark:text-white mb-1">Comprehensive Research</div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          Combine all sources: documents, web, and notes for deep analysis
                        </div>
                        <div className="text-xs text-orange-600 dark:text-orange-400 font-medium">
                          → Try: "Analyze the current state of renewable energy"
                        </div>
                      </div>
                    </div>
                  </button>
                </div>

                {/* Quick Tips */}
                <div className="text-center">
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                    💡 <span className="font-medium">Pro Tip:</span> Switch modes anytime using the controls above
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Upload documents • Configure Obsidian • Adjust settings for optimal results
                  </p>
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

