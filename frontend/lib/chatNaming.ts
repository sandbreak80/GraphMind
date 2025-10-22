/**
 * Chat naming utilities for auto-generating meaningful chat titles
 */

export function generateChatTitle(firstMessage: string): string {
  // Extract key trading terms and concepts
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

  const message = firstMessage.toLowerCase()
  
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

  // Look for question words to create a generic title
  if (message.includes('what') || message.includes('how') || message.includes('why')) {
    return 'Trading Strategy Question'
  }

  if (message.includes('explain') || message.includes('describe')) {
    return 'Strategy Explanation Request'
  }

  if (message.includes('help') || message.includes('assist')) {
    return 'Trading Assistance'
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

  // Default fallback
  return 'Trading Strategy Chat'
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