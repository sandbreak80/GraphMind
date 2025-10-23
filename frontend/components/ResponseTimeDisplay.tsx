import React from 'react'
import { useStore } from '../lib/store'

interface ResponseTimeDisplayProps {
  messageId: string
  className?: string
}

export function ResponseTimeDisplay({ messageId, className = '' }: ResponseTimeDisplayProps) {
  const { messages } = useStore()
  const message = messages.find(m => m.id === messageId)
  
  if (!message?.responseTime) return null

  const formatTime = (seconds: number) => {
    if (seconds < 1) {
      return `${Math.round(seconds * 1000)}ms`
    } else if (seconds < 60) {
      return `${seconds.toFixed(1)}s`
    } else {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}m ${remainingSeconds.toFixed(1)}s`
    }
  }

  const getTimeColor = (seconds: number) => {
    if (seconds < 5) return 'text-green-600'
    if (seconds < 15) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <span className={`text-xs ${getTimeColor(message.responseTime)} ${className}`}>
      {formatTime(message.responseTime)}
    </span>
  )
}

interface AverageResponseTimeProps {
  chatId: string
  className?: string
}

export function AverageResponseTime({ chatId, className = '' }: AverageResponseTimeProps) {
  const { calculateAverageResponseTime } = useStore()
  const averageTime = calculateAverageResponseTime(chatId)
  
  if (averageTime === 0) return null

  const formatTime = (seconds: number) => {
    if (seconds < 1) {
      return `${Math.round(seconds * 1000)}ms`
    } else if (seconds < 60) {
      return `${seconds.toFixed(1)}s`
    } else {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}m ${remainingSeconds.toFixed(1)}s`
    }
  }

  return (
    <div className={`text-xs text-gray-500 ${className}`}>
      Avg: {formatTime(averageTime)}
    </div>
  )
}