import axios from 'axios'
import { useStore } from './store'

const api = axios.create({
  timeout: 300000, // 5 minutes for LLM/RAG processing
})

// Request interceptor
api.interceptors.request.use((config) => {
  // Check if we're running in the browser (client-side)
  if (typeof window !== 'undefined') {
    // Use the external URL when accessed from browser
    config.baseURL = 'http://localhost:8001'
  } else {
    // Use Docker service name for container-to-container communication
    config.baseURL = 'http://rag-service:8000'
  }
  
  // Add authentication header if available
  const { authToken } = useStore.getState()
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`
  }
  
  return config
})

export interface AskRequest {
  query: string
  mode: 'qa' | 'spec' | 'obsidian'
  top_k?: number
  temperature?: number
  max_tokens?: number
  conversation_history?: Array<{
    role: 'user' | 'assistant'
    content: string
  }>
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
    const { data } = await api.post('/ask', { request })
    return data
  },

  async askEnhanced(request: AskRequest): Promise<AskResponse> {
    const { data } = await api.post('/ask-enhanced', { request })
    return data
  },

  async askObsidian(request: AskRequest): Promise<AskResponse> {
    const { data } = await api.post('/ask-obsidian', { request })
    return data
  },

  async askResearch(request: AskRequest): Promise<AskResponse> {
    const { data } = await api.post('/ask-research', { request })
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
    stream?: boolean
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

  // Streaming chat
  async streamChat(
    request: AskRequest,
    onMessage: (chunk: string) => void,
    onComplete: (data?: any) => void,
    onError: (error: Error) => void
  ) {
    try {
      const { settings } = useStore.getState()
      const endpoint = request.mode === 'obsidian' ? '/ask-obsidian' : 
                     request.mode === 'spec' ? '/ask' : '/ask-enhanced'
      
      const response = await fetch(`${settings.apiUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${useStore.getState().authToken}`
        },
        body: JSON.stringify({ request }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Since backend doesn't support streaming yet, simulate it with the complete response
      const data = await response.json()
      
      if (data && data.answer) {
        // Simulate streaming by breaking the response into chunks
        const words = data.answer.split(' ')
        let currentText = ''
        
        for (let i = 0; i < words.length; i++) {
          const newWord = (i > 0 ? ' ' : '') + words[i]
          currentText += newWord
          
          // Send chunk every 3 words for smooth streaming effect
          if (i % 3 === 0 || i === words.length - 1) {
            onMessage(currentText) // Send the full accumulated text
            // Small delay to simulate streaming
            await new Promise(resolve => setTimeout(resolve, 50))
          }
        }
      } else {
        // If no answer, send error message
        onMessage('Sorry, I encountered an error. Please try again.')
      }

      onComplete(data)
    } catch (error) {
      onError(error as Error)
    }
  }
}

export default apiClient