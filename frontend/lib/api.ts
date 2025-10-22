import axios from 'axios'
import { useStore } from './store'

const api = axios.create({
  timeout: 300000, // 5 minutes for LLM/RAG processing
})

// Request interceptor
api.interceptors.request.use((config) => {
  // Always use localhost:8001 directly to avoid Cloudflare DNS issues
  config.baseURL = 'http://localhost:8001'
  return config
})

export interface AskRequest {
  query: string
  mode: 'qa' | 'spec' | 'obsidian'
  top_k?: number
  temperature?: number
  max_tokens?: number
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
    onComplete: () => void,
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
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.content) {
                onMessage(data.content)
              }
            } catch (e) {
              // Ignore malformed JSON
            }
          }
        }
      }

      onComplete()
    } catch (error) {
      onError(error as Error)
    }
  }
}

export default apiClient