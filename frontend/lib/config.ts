/**
 * Global configuration for the application
 */

// Public domain configuration
export const PUBLIC_DOMAIN = process.env.NEXT_PUBLIC_DOMAIN || 'https://emini.riffyx.com'

// Application branding
export const APP_CONFIG = {
  name: 'TradingAI Research Platform',
  shortName: 'TradingAI',
  tagline: 'Advanced AI Research & Knowledge Management',
  description: 'Comprehensive AI-powered research platform with RAG, web search, Obsidian integration, and intelligent query generation',
  version: '2.0.0',
  author: 'TradingAI Team',
  
  // Feature indicators
  features: {
    rag: 'RAG',
    obsidian: 'Obsidian', 
    web: 'Web',
    research: 'Research',
    memory: 'Memory'
  },
  
  // API endpoints
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://emini-rag-dev:8000',
    endpoints: {
      ask: '/ask',
      askEnhanced: '/ask-enhanced',
      askObsidian: '/ask-obsidian',
      askResearch: '/ask-research',
      health: '/health',
      auth: {
        login: '/auth/login',
        me: '/auth/me'
      },
      models: '/ollama/models',
      prompts: {
        system: '/system-prompts',
        user: '/user-prompts'
      }
    }
  },
  
  // Performance presets
  presets: {
    fast: {
      name: 'Fast',
      description: 'Quick responses for real-time trading',
      icon: '⚡',
      responseTime: '1-2s'
    },
    balanced: {
      name: 'Balanced', 
      description: 'Optimal performance for general queries',
      icon: '⚖️',
      responseTime: '2-3s'
    },
    comprehensive: {
      name: 'Comprehensive',
      description: 'Deep research and analysis',
      icon: '🔍', 
      responseTime: '3-5s'
    }
  }
} as const

// Export types
export type AppConfig = typeof APP_CONFIG
export type PresetKey = keyof typeof APP_CONFIG.presets