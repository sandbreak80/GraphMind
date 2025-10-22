import { create } from 'zustand'
import { persist } from 'zustand/middleware'

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
  deleteChat: (chatId: string) => void
  clearMessages: () => void
  setProcessing: (processing: boolean) => void
  
  setModels: (models: OllamaModel[]) => void
  setSelectedModel: (model: string) => void
  
  updateSettings: (settings: Partial<Settings>) => void
  setSidebarOpen: (open: boolean) => void
  setTheme: (theme: 'light' | 'dark') => void
  
  initializeApp: () => Promise<void>
}

// Determine API URL based on environment
const getApiUrl = () => {
  // Always use localhost:8001 to avoid Cloudflare DNS issues
  // The backend is exposed on localhost:8001, not through the domain
  return 'http://localhost:8001'
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
        set({
          currentChatId: chatId,
          messages: chat?.messages || []
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
          
          // Update current chat
          const updatedChats = state.chats.map(chat => 
            chat.id === state.currentChatId 
              ? { ...chat, messages: newMessages, updatedAt: new Date().toISOString() }
              : chat
          )
          
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