import axios from 'axios'
import { useStore } from './store'
import { APP_CONFIG } from './config'

// Centralized API URL determination
export const getApiUrl = () => {
  // Check if we're running in the browser (client-side)
  if (typeof window !== 'undefined') {
    // Check if we're in development mode (localhost)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      // Use local backend for development - connect to the exposed port
      return 'http://localhost:8002'
    } else {
      // For production, the frontend is exposed via Cloudflare tunnel
      // but the API is NOT exposed - it's internal to the Docker network
      // The frontend uses Next.js API routes that proxy to the backend
      // These routes handle the internal Docker network communication
      return '/api'
    }
  }
  // Use Docker service name for container-to-container communication
  return APP_CONFIG.api.baseUrl
}

const api = axios.create({
  timeout: 300000, // 5 minutes for LLM/RAG processing
})

// Request interceptor
api.interceptors.request.use((config) => {
  // Set base URL using centralized function
  config.baseURL = getApiUrl()
  
  // Add authentication header if available
  const { authToken } = useStore.getState()
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`
  }
  
  return config
})

// Response interceptor to handle authentication errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle authentication errors
    if (error.response?.status === 401 || error.response?.status === 403) {
      // Clear authentication state and redirect to login
      const { logout } = useStore.getState()
      logout()
      
      // Show user-friendly message
      if (typeof window !== 'undefined') {
        // Import toast dynamically to avoid SSR issues
        import('react-hot-toast').then(({ toast }) => {
          toast.error('Your session has expired. Please log in again.')
        })
      }
    }
    
    return Promise.reject(error)
  }
)

export interface AskRequest {
  query: string
  mode: 'qa' | 'spec' | 'obsidian'
  top_k?: number  // This is for retrieval (legacy, will be replaced by rerank_top_k)
  temperature?: number
  max_tokens?: number
  top_k_sampling?: number  // New: LLM sampling parameter
  model?: string
  conversation_history?: Array<{
    role: 'user' | 'assistant'
    content: string
  }>
  // Document Retrieval Settings
  bm25_top_k?: number
  embedding_top_k?: number
  rerank_top_k?: number
  // Web Search Settings
  web_search_results?: number
  web_pages_to_parse?: number
}

export interface AskResponse {
  query: string
  answer: string
  citations: Array<{
    text: string
    doc_id: string
    page?: number
    section?: string
    score: number
  }>
  mode: string
  spec_file?: string
  web_enabled: boolean
  total_sources?: number
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

export interface StatsResponse {
  total_documents: number
  collection_name: string
  bm25_documents: number
  embedding_documents: number
  last_ingestion: string
  models_available: string[]
  web_search_enabled: boolean
  obsidian_enabled: boolean
}

export const apiClient = {
  // Chat endpoints
  async ask(request: AskRequest): Promise<AskResponse> {
    const { data } = await api.post('/ask', request)
    return data
  },

  async askEnhanced(request: AskRequest): Promise<AskResponse> {
    const { data } = await api.post('/ask-enhanced', request)
    return data
  },

  async askObsidian(request: AskRequest): Promise<AskResponse> {
    const { data } = await api.post('/ask-obsidian', request)
    return data
  },

  async askResearch(request: AskRequest): Promise<AskResponse> {
    const { data } = await api.post('/ask-research', request)
    return data
  },

  // Ollama endpoints
  async getModels(): Promise<{ models: OllamaModel[] }> {
    const { data } = await api.get('/ollama/models')
    return data
  },

  async generate(request: {
    model: string
    prompt: string
    options?: {
      temperature?: number
      num_predict?: number
      top_k?: number
      top_p?: number
    }
  }): Promise<any> {
    const { data } = await api.post('/ollama/generate', request)
    return data
  },

  // System endpoints
  async getStats(): Promise<StatsResponse> {
    const { data } = await api.get('/stats')
    return data
  },

  async getHealth(): Promise<{ status: string }> {
    const { data } = await api.get('/health')
    return data
  },

}

export default apiClient