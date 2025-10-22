/**
 * Chat naming utilities for auto-generating meaningful chat titles
 */

export function generateChatTitle(firstMessage: string): string {
  const message = firstMessage.toLowerCase()
  
  // Extract company names (common companies)
  const companyNames = [
    'intuit', 'microsoft', 'google', 'apple', 'amazon', 'meta', 'tesla',
    'netflix', 'nvidia', 'salesforce', 'adobe', 'oracle', 'ibm', 'facebook',
    'twitter', 'linkedin', 'uber', 'airbnb', 'spotify', 'zoom', 'slack'
  ]
  
  for (const company of companyNames) {
    if (message.includes(company)) {
      return `${capitalizeWords(company)} Research`
    }
  }
  
  // Extract trading terms and concepts
  const tradingTerms = [
    'fade', 'setup', 'strategy', 'trading', 'entry', 'exit', 'stop', 'target',
    'support', 'resistance', 'trend', 'breakout', 'pullback', 'continuation',
    'macd', 'rsi', 'moving average', 'indicator', 'signal', 'pattern',
    'scalp', 'swing', 'position', 'risk', 'reward', 'ratio', 'management',
    'backtest', 'optimize', 'parameter', 'settings', 'configuration',
    'market', 'price', 'volume', 'momentum', 'volatility', 'range',
    'zone', 'level', 'key', 'critical', 'important', 'setup', 'rule'
  ]

  // Extract potential strategy names
  const strategyNames = [
    'battlecard', 'fade setup', 'pullback continuation', 'pbc', 'opening drive',
    'trend following', 'mean reversion', 'breakout', 'scalping', 'swing trading',
    'position trading', 'day trading', 'intraday', 'overnight', 'session'
  ]
  
  // Look for strategy names first
  for (const strategy of strategyNames) {
    if (message.includes(strategy)) {
      return capitalizeWords(strategy)
    }
  }

  // Look for trading terms and create a title
  const foundTerms = tradingTerms.filter(term => message.includes(term))
  
  if (foundTerms.length > 0) {
    // Take the first 2-3 relevant terms
    const relevantTerms = foundTerms.slice(0, 3)
    return capitalizeWords(relevantTerms.join(' ')) + ' Discussion'
  }

  // Look for research-related terms
  if (message.includes('research') || message.includes('analysis') || message.includes('report')) {
    return 'Research Analysis'
  }

  if (message.includes('company') || message.includes('business') || message.includes('corporate')) {
    return 'Company Analysis'
  }

  if (message.includes('financial') || message.includes('revenue') || message.includes('earnings')) {
    return 'Financial Analysis'
  }

  if (message.includes('technology') || message.includes('tech') || message.includes('software')) {
    return 'Technology Discussion'
  }

  if (message.includes('market') || message.includes('stock') || message.includes('investment')) {
    return 'Market Analysis'
  }

  // Look for question words to create a more specific title
  if (message.includes('what') || message.includes('how') || message.includes('why')) {
    // Try to extract the main topic
    const words = firstMessage.split(' ').slice(0, 5) // First 5 words
    const topic = words.join(' ').replace(/[?.,!]/g, '')
    return topic.length > 30 ? topic.substring(0, 30) + '...' : topic
  }

  if (message.includes('explain') || message.includes('describe')) {
    return 'Explanation Request'
  }

  if (message.includes('help') || message.includes('assist')) {
    return 'Assistance Request'
  }

  // Look for specific timeframes or markets
  if (message.includes('es') || message.includes('emini') || message.includes('s&p')) {
    return 'E-mini S&P Strategy'
  }

  if (message.includes('nq') || message.includes('nasdaq')) {
    return 'Nasdaq Strategy'
  }

  if (message.includes('ym') || message.includes('dow')) {
    return 'Dow Strategy'
  }

  // Try to create a title from the first few words
  const words = firstMessage.split(' ').slice(0, 4)
  const title = words.join(' ').replace(/[?.,!]/g, '')
  
  if (title.length > 0 && title.length <= 40) {
    return title
  }

  // Default fallback
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