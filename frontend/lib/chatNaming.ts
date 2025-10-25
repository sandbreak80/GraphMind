/**
 * Chat naming utilities using LLM for intelligent title generation
 */

import { useStore } from './store'
import { getApiUrl } from './api'

export async function generateChatTitle(firstMessage: string): Promise<string> {
  try {
    // Use the API to generate a title using LLM
    const response = await fetch(`${getApiUrl()}/generate-chat-title`, {
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
  const researchTerms = [
    'research', 'analysis', 'study', 'investigation', 'exploration', 'examination',
    'methodology', 'approach', 'framework', 'model', 'theory', 'concept',
    'data', 'findings', 'results', 'conclusion', 'hypothesis', 'experiment',
    'domain', 'field', 'subject', 'topic', 'area', 'discipline',
    'knowledge', 'information', 'insight', 'understanding', 'comprehension',
    'document', 'source', 'reference', 'citation', 'evidence', 'proof',
    'key', 'important', 'critical', 'significant', 'relevant', 'essential'
  ]

  const messageLower = message.toLowerCase()
  return researchTerms.filter(term => messageLower.includes(term))
}