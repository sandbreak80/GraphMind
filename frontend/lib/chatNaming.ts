/**
 * Chat naming utilities using LLM for intelligent title generation
 */

import { useStore } from './store'

export async function generateChatTitle(firstMessage: string): Promise<string> {
  try {
    // Use the API to generate a title using LLM
    const response = await fetch('/api/generate-chat-title', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${useStore.getState().authToken}`
      },
      body: JSON.stringify({ message: firstMessage })
    })

    if (response.ok) {
      const data = await response.json()
      return data.title || fallbackTitle(firstMessage)
    }
  } catch (error) {
    console.warn('Failed to generate LLM title:', error)
  }

  // Fallback to simple title generation
  return fallbackTitle(firstMessage)
}

function fallbackTitle(firstMessage: string): string {
  // Simple fallback - just use first few words
  const words = firstMessage.split(' ').slice(0, 4)
  const title = words.join(' ').replace(/[?.,!]/g, '')
  
  if (title.length > 0 && title.length <= 40) {
    return title
  }

  return 'New Chat'
}

function capitalizeWords(str: string): string {
  return str
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

export function extractKeywords(message: string): string[] {
  const tradingTerms = [
    'fade', 'setup', 'strategy', 'trading', 'entry', 'exit', 'stop', 'target',
    'support', 'resistance', 'trend', 'breakout', 'pullback', 'continuation',
    'macd', 'rsi', 'moving average', 'indicator', 'signal', 'pattern',
    'scalp', 'swing', 'position', 'risk', 'reward', 'ratio', 'management',
    'backtest', 'optimize', 'parameter', 'settings', 'configuration',
    'market', 'price', 'volume', 'momentum', 'volatility', 'range',
    'zone', 'level', 'key', 'critical', 'important', 'setup', 'rule'
  ]

  const messageLower = message.toLowerCase()
  return tradingTerms.filter(term => messageLower.includes(term))
}