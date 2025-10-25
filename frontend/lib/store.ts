import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { generateChatTitle } from './chatNaming'

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: string
  sources?: Source[]
  mode?: string
  totalSources?: number
  isProcessing?: boolean
  model?: string
  responseTime?: number
}

export interface Source {
  text: string
  doc_id: string
  page?: number
  section?: string
  score: number
}

export interface Chat {
  id: string
  title: string
  messages: Message[]
  createdAt: string
  updatedAt: string
  currentModel?: string
  averageResponseTime?: number
}

export interface OllamaModel {
  name: string
  size: number
  modified_at: string
  digest: string
  details: {
    format: string
    family: string
    families: string[]
    parameter_size: string
    quantization_level: string
  }
}

export interface User {
  username: string
  is_admin: boolean
}

export interface Settings {
  selectedModel: string
  temperature: number
  maxTokens: number
  topKSampling: number  // Renamed from topK to avoid confusion with retrieval
  enableWebSearch: boolean
  enableRAG: boolean
  enableObsidian: boolean
  theme: 'light' | 'dark' | 'system'
  // Document Retrieval Settings
  bm25TopK: number
  embeddingTopK: number
  rerankTopK: number
  // Web Search Settings
  webSearchResults: number
  webPagesToParse: number
}

interface AppState {
  // Authentication
  isAuthenticated: boolean
  user: User | null
  authToken: string | null
  
  // Chat state
  chats: Chat[]
  currentChatId: string | null
  messages: Message[]
  isLoading: boolean
  isProcessing: boolean
  
  // Models
  models: OllamaModel[]
  selectedModel: string
  
  // Settings
  settings: Settings
  
  // UI state
  sidebarOpen: boolean
  theme: 'light' | 'dark'
  
  // Actions
  setCurrentChat: (chatId: string | null) => void
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
  updateMessage: (id: string, updates: Partial<Message>) => void
  createChat: (title: string) => string
  createChatWithAutoName: (firstMessage: string) => string
  deleteChat: (chatId: string) => void
  clearMessages: () => void
  setProcessing: (processing: boolean) => void
  retryLastMessage: () => void
  
  // URL navigation
  navigateToChat: (chatId: string) => void
  getChatUrl: (chatId: string) => string
  
  // Model switching
  switchModel: (model: string) => void
  getCurrentModel: () => string
  getChatModel: (chatId: string) => string
  
  // Response time tracking
  updateResponseTime: (messageId: string, responseTime: number) => void
  calculateAverageResponseTime: (chatId: string) => number
  
  // Chat export
  exportChat: (chatId: string) => Promise<string>
  exportAllChats: () => Promise<string>
  
  setModels: (models: OllamaModel[]) => void
  setSelectedModel: (model: string) => void
  
  updateSettings: (settings: Partial<Settings>) => void
  setSidebarOpen: (open: boolean) => void
  setTheme: (theme: 'light' | 'dark') => void
  
  // Authentication actions
  login: (token: string, user: User) => void
  logout: () => void
  checkAuth: () => boolean
  
  initializeApp: () => Promise<void>
}

const defaultSettings: Settings = {
  selectedModel: 'qwen2.5-coder:14b',
  temperature: 0.1,
  maxTokens: 8000,
  topKSampling: 40,    // Renamed and optimized for high-end hardware
  enableWebSearch: false,
  enableRAG: true,
  enableObsidian: true,
  theme: 'system',
  // Document Retrieval Settings (optimized for 100GB RAM + 24 CPU cores + 2x GPU)
  bm25TopK: 30,        // Increased for better recall on high-end hardware
  embeddingTopK: 30,   // Increased for better recall on high-end hardware
  rerankTopK: 8,       // Increased for more comprehensive results
  // Web Search Settings (balanced for real-time performance)
  webSearchResults: 6, // Slightly increased for better coverage
  webPagesToParse: 4,  // Increased for more detailed web content
}

export const useStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      isAuthenticated: false,
      user: null,
      authToken: null,
      chats: [],
      currentChatId: null,
      messages: [],
      isLoading: false,
      isProcessing: false,
      models: [],
      selectedModel: 'qwen2.5-coder:14b',
      settings: defaultSettings,
      sidebarOpen: true,
      theme: 'light',
      
      // Actions
      setCurrentChat: (chatId) => {
        const chat = get().chats.find(c => c.id === chatId)
        const messages = chat?.messages || []
        
        // Clean up any processing messages from the loaded chat
        const cleanedMessages = messages.map(msg => ({
          ...msg,
          isProcessing: false
        }))
        
        set({
          currentChatId: chatId,
          messages: cleanedMessages,
          isProcessing: false,
        })
      },
      
      addMessage: (message) => {
        const { getCurrentModel } = get()
        const newMessage: Message = {
          ...message,
          id: crypto.randomUUID(),
          timestamp: new Date().toISOString(),
          model: message.model || getCurrentModel()
        }
        
        set(state => {
          const newMessages = [...state.messages, newMessage]
          
          // Auto-name chat if this is the first user message
          let updatedChats = state.chats.map(chat => {
            if (chat.id === state.currentChatId) {
              const updatedChat = { ...chat, messages: newMessages, updatedAt: new Date().toISOString() }
              
              // If this is the first user message and chat title is generic, auto-name it
              if (message.role === 'user' && 
                  newMessages.filter(m => m.role === 'user').length === 1 && 
                  (chat.title === 'New Chat' || chat.title === 'Trading Strategy Chat')) {
                // Generate title asynchronously
                generateChatTitle(message.content).then(title => {
                  // Update the chat title after generation
                  set(state => ({
                    chats: state.chats.map(c => 
                      c.id === chat.id ? { ...c, title } : c
                    )
                  }))
                }).catch(() => {
                  // Fallback to simple title if LLM fails
                  const simpleTitle = message.content.split(' ').slice(0, 4).join(' ')
                  set(state => ({
                    chats: state.chats.map(c => 
                      c.id === chat.id ? { ...c, title: simpleTitle } : c
                    )
                  }))
                })
              }
              
              return updatedChat
            }
            return chat
          })
          
          return {
            messages: newMessages,
            chats: updatedChats
          }
        })
      },
      
      updateMessage: (id, updates) => {
        set(state => {
          const updatedMessages = state.messages.map(msg => 
            msg.id === id ? { ...msg, ...updates } : msg
          )
          
          // Also update the chat object to persist changes
          const updatedChats = state.chats.map(chat => {
            if (chat.id === state.currentChatId) {
              return { ...chat, messages: updatedMessages, updatedAt: new Date().toISOString() }
            }
            return chat
          })
          
          return {
            messages: updatedMessages,
            chats: updatedChats
          }
        })
      },
      
      createChat: (title) => {
        const newChat: Chat = {
          id: crypto.randomUUID(),
          title,
          messages: [],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
        
        set(state => ({
          chats: [newChat, ...state.chats],
          currentChatId: newChat.id,
          messages: []
        }))
        
        return newChat.id
      },
      
      createChatWithAutoName: (firstMessage: string) => {
        // Create chat with temporary title, will be updated asynchronously
        const chatId = get().createChat('New Chat')
        
        // Generate title asynchronously and update
        generateChatTitle(firstMessage).then(title => {
          set(state => ({
            chats: state.chats.map(chat => 
              chat.id === chatId ? { ...chat, title } : chat
            )
          }))
        }).catch(() => {
          // Fallback to simple title if LLM fails
          const simpleTitle = firstMessage.split(' ').slice(0, 4).join(' ')
          set(state => ({
            chats: state.chats.map(chat => 
              chat.id === chatId ? { ...chat, title: simpleTitle } : chat
            )
          }))
        })
        
        return chatId
      },
      
      deleteChat: (chatId) => {
        set(state => ({
          chats: state.chats.filter(chat => chat.id !== chatId),
          currentChatId: state.currentChatId === chatId ? null : state.currentChatId,
          messages: state.currentChatId === chatId ? [] : state.messages
        }))
      },
      
      clearMessages: () => {
        set({ messages: [] })
      },
      
      setProcessing: (processing) => {
        set({ isProcessing: processing })
      },
      
      retryLastMessage: () => {
        const state = get()
        const lastMessage = state.messages[state.messages.length - 1]
        
        if (lastMessage && lastMessage.role === 'assistant' && lastMessage.isProcessing) {
          // Remove the processing message
          set(state => ({
            messages: state.messages.slice(0, -1)
          }))
        }
      },
      
      // Authentication actions
      login: (token: string, user: User) => {
        set({ 
          isAuthenticated: true, 
          user, 
          authToken: token 
        })
        // Store token in localStorage
        localStorage.setItem('authToken', token)
        localStorage.setItem('user', JSON.stringify(user))
      },
      
      logout: () => {
        set({ 
          isAuthenticated: false, 
          user: null, 
          authToken: null 
        })
        // Clear token from localStorage
        localStorage.removeItem('authToken')
        localStorage.removeItem('user')
      },
      
      checkAuth: () => {
        const token = localStorage.getItem('authToken')
        const userStr = localStorage.getItem('user')
        
        if (token && userStr) {
          try {
            const user = JSON.parse(userStr)
            set({ 
              isAuthenticated: true, 
              user, 
              authToken: token 
            })
            return true
          } catch (error) {
            console.error('Failed to parse user data:', error)
            localStorage.removeItem('authToken')
            localStorage.removeItem('user')
          }
        }
        
        set({ 
          isAuthenticated: false, 
          user: null, 
          authToken: null 
        })
        return false
      },
      
      setModels: (models) => set({ models }),
      setSelectedModel: (model) => set({ selectedModel: model }),
      
      // Model switching
      switchModel: (model) => {
        set({ selectedModel: model })
        // Update current chat's model if it exists
        const { currentChatId, chats } = get()
        if (currentChatId) {
          const updatedChats = chats.map(chat => 
            chat.id === currentChatId 
              ? { ...chat, currentModel: model, updatedAt: new Date().toISOString() }
              : chat
          )
          set({ chats: updatedChats })
        }
      },
      
      getCurrentModel: () => {
        const { currentChatId, chats, selectedModel } = get()
        if (currentChatId) {
          const chat = chats.find(c => c.id === currentChatId)
          return chat?.currentModel || selectedModel
        }
        return selectedModel
      },
      
      getChatModel: (chatId) => {
        const { chats, selectedModel } = get()
        const chat = chats.find(c => c.id === chatId)
        return chat?.currentModel || selectedModel
      },
      
      // Response time tracking
      updateResponseTime: (messageId, responseTime) => {
        set(state => {
          const updatedMessages = state.messages.map(msg => 
            msg.id === messageId ? { ...msg, responseTime } : msg
          )
          
          // Update chat's average response time
          const updatedChats = state.chats.map(chat => {
            if (chat.id === state.currentChatId) {
              const chatMessages = updatedMessages.filter(msg => msg.role === 'assistant' && msg.responseTime)
              const avgTime = chatMessages.length > 0 
                ? chatMessages.reduce((sum, msg) => sum + (msg.responseTime || 0), 0) / chatMessages.length
                : 0
              return { ...chat, messages: updatedMessages, averageResponseTime: avgTime }
            }
            return chat
          })
          
          return {
            messages: updatedMessages,
            chats: updatedChats
          }
        })
      },
      
      calculateAverageResponseTime: (chatId) => {
        const { chats } = get()
        const chat = chats.find(c => c.id === chatId)
        if (!chat) return 0
        
        const assistantMessages = chat.messages.filter(msg => msg.role === 'assistant' && msg.responseTime)
        if (assistantMessages.length === 0) return 0
        
        return assistantMessages.reduce((sum, msg) => sum + (msg.responseTime || 0), 0) / assistantMessages.length
      },
      
      // Chat export
      exportChat: async (chatId) => {
        const { chats } = get()
        const chat = chats.find(c => c.id === chatId)
        if (!chat) throw new Error('Chat not found')
        
        let markdown = `# ${chat.title}\n\n`
        markdown += `**Created:** ${new Date(chat.createdAt).toLocaleString()}\n`
        markdown += `**Last Updated:** ${new Date(chat.updatedAt).toLocaleString()}\n`
        if (chat.averageResponseTime) {
          markdown += `**Average Response Time:** ${chat.averageResponseTime.toFixed(2)}s\n`
        }
        markdown += `\n---\n\n`
        
        for (const message of chat.messages) {
          const timestamp = new Date(message.timestamp).toLocaleString()
          const model = message.model ? ` (${message.model})` : ''
          const responseTime = message.responseTime ? ` [${message.responseTime.toFixed(2)}s]` : ''
          
          markdown += `## ${message.role === 'user' ? 'User' : 'Assistant'}${model}${responseTime}\n`
          markdown += `*${timestamp}*\n\n`
          markdown += `${message.content}\n\n`
          
          if (message.sources && message.sources.length > 0) {
            markdown += `### Sources\n`
            for (const source of message.sources) {
              markdown += `- **${source.section}** (Score: ${source.score.toFixed(2)})\n`
              markdown += `  ${source.text.substring(0, 200)}...\n\n`
            }
          }
          
          markdown += `---\n\n`
        }
        
        return markdown
      },
      
      exportAllChats: async () => {
        const { chats } = get()
        let markdown = `# TradingAI Research Platform Chat Export\n\n`
        markdown += `**Export Date:** ${new Date().toLocaleString()}\n`
        markdown += `**Total Chats:** ${chats.length}\n\n`
        markdown += `---\n\n`
        
        for (const chat of chats) {
          const chatExport = await get().exportChat(chat.id)
          markdown += chatExport + '\n\n'
        }
        
        return markdown
      },
      
      updateSettings: (newSettings) => {
        set(state => ({
          settings: { ...state.settings, ...newSettings }
        }))
      },
      
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setTheme: (theme) => {
        set({ theme })
        // Apply theme to DOM
        if (typeof window !== 'undefined') {
          const root = window.document.documentElement
          root.classList.remove('light', 'dark')
          root.classList.add(theme)
          // Also set data attribute for better CSS targeting
          root.setAttribute('data-theme', theme)
          // Store in localStorage for persistence
          localStorage.setItem('theme', theme)
        }
      },
      
      // URL navigation
      navigateToChat: (chatId) => {
        // Update URL without page reload
        if (typeof window !== 'undefined') {
          window.history.pushState({}, '', `/chat/${chatId}`)
        }
        get().setCurrentChat(chatId)
      },
      
      getChatUrl: (chatId) => {
        if (typeof window !== 'undefined') {
          return `${window.location.origin}/chat/${chatId}`
        }
        return `/chat/${chatId}`
      },
      
      initializeApp: async () => {
        // Load models from Ollama
        try {
          // Import getApiUrl dynamically to avoid circular dependency
          const { getApiUrl } = await import('./api')
          const response = await fetch(`${getApiUrl()}/ollama/models`)
          if (response.ok) {
            const data = await response.json()
            set({ models: data.models || [] })
          }
        } catch (error) {
          console.error('Failed to load models:', error)
        }
        
        // Apply theme
        const settingsTheme = get().settings.theme
        let actualTheme: 'light' | 'dark' = 'light'
        if (settingsTheme === 'system') {
          actualTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
        } else {
          actualTheme = settingsTheme
        }
        set({ theme: actualTheme })
        
        // Apply theme to DOM
        if (typeof window !== 'undefined') {
          const root = window.document.documentElement
          root.classList.remove('light', 'dark')
          root.classList.add(actualTheme)
          // Also set data attribute for better CSS targeting
          root.setAttribute('data-theme', actualTheme)
          // Store in localStorage for persistence
          localStorage.setItem('theme', actualTheme)
        }
      }
    }),
    {
      name: 'tradingai-store',
      partialize: (state) => ({
        chats: state.chats,
        settings: state.settings,
        selectedModel: state.selectedModel,
        theme: state.theme,
      }),
    }
  )
)