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
  apiUrl: string
  selectedModel: string
  temperature: number
  maxTokens: number
  topK: number
  enableWebSearch: boolean
  enableRAG: boolean
  enableObsidian: boolean
  theme: 'light' | 'dark' | 'system'
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
  isStreaming: boolean
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

// Determine API URL based on environment
const getApiUrl = () => {
  // Check if we're running in the browser (client-side)
  if (typeof window !== 'undefined') {
    // Use the external URL when accessed from browser
    return 'http://localhost:8001'
  }
  // Use Docker service name for container-to-container communication
  return 'http://rag-service:8000'
}

const defaultSettings: Settings = {
  apiUrl: getApiUrl(),
  selectedModel: 'qwen2.5-coder:14b',
  temperature: 0.1,
  maxTokens: 8000,
  topK: 5,
  enableWebSearch: false,
  enableRAG: true,
  enableObsidian: true,
  theme: 'system',
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
      isStreaming: false,
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
          isStreaming: false
        })
      },
      
      addMessage: (message) => {
        const newMessage: Message = {
          ...message,
          id: crypto.randomUUID(),
          timestamp: new Date().toISOString()
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
                updatedChat.title = generateChatTitle(message.content)
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
        set(state => ({
          messages: state.messages.map(msg => 
            msg.id === id ? { ...msg, ...updates } : msg
          )
        }))
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
        const title = generateChatTitle(firstMessage)
        return get().createChat(title)
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
      
      updateSettings: (newSettings) => {
        set(state => ({
          settings: { ...state.settings, ...newSettings }
        }))
      },
      
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setTheme: (theme) => set({ theme }),
      
      initializeApp: async () => {
        // Load models from Ollama
        try {
          const response = await fetch(`${get().settings.apiUrl}/ollama/models`)
          if (response.ok) {
            const data = await response.json()
            set({ models: data.models || [] })
          }
        } catch (error) {
          console.error('Failed to load models:', error)
        }
        
        // Apply theme
        const theme = get().settings.theme
        if (theme === 'system') {
          const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
          set({ theme: systemTheme })
        } else {
          set({ theme })
        }
      }
    }),
    {
      name: 'eminiplayer-store',
      partialize: (state) => ({
        chats: state.chats,
        settings: state.settings,
        selectedModel: state.selectedModel,
        theme: state.theme,
      }),
    }
  )
)