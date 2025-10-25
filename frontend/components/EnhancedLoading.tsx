'use client'

import { useState, useEffect } from 'react'

interface EnhancedLoadingProps {
  message?: string
  type?: 'dots' | 'pulse' | 'wave' | 'spinner'
  size?: 'sm' | 'md' | 'lg'
}

export function EnhancedLoading({ 
  message = 'Processing...', 
  type = 'dots',
  size = 'md' 
}: EnhancedLoadingProps) {
  const [dots, setDots] = useState('')

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.')
    }, 500)
    return () => clearInterval(interval)
  }, [])

  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  }

  const renderLoader = () => {
    switch (type) {
      case 'dots':
        return (
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
        )
      case 'pulse':
        return (
          <div className="w-8 h-8 bg-primary-600 rounded-full animate-pulse"></div>
        )
      case 'wave':
        return (
          <div className="flex items-center space-x-1">
            <div className="w-1 h-6 bg-primary-600 rounded-full animate-pulse"></div>
            <div className="w-1 h-6 bg-primary-600 rounded-full animate-pulse" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-1 h-6 bg-primary-600 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-1 h-6 bg-primary-600 rounded-full animate-pulse" style={{ animationDelay: '0.3s' }}></div>
            <div className="w-1 h-6 bg-primary-600 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
          </div>
        )
      case 'spinner':
        return (
          <div className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
        )
      default:
        return null
    }
  }

  return (
    <div className="flex items-center space-x-3 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
      {renderLoader()}
      <span className={`text-gray-600 dark:text-gray-400 ${sizeClasses[size]}`}>
        {message}{dots}
      </span>
    </div>
  )
}

export function TypingIndicator() {
  return (
    <div className="flex items-center space-x-2 p-3 bg-gray-100 dark:bg-gray-800 rounded-lg">
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
      </div>
      <span className="text-sm text-gray-500 dark:text-gray-400">AI is thinking...</span>
    </div>
  )
}

export function ProgressBar({ progress, message }: { progress: number; message?: string }) {
  return (
    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
      <div 
        className="bg-primary-600 h-2 rounded-full transition-all duration-300 ease-out"
        style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
      ></div>
      {message && (
        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          {message}
        </div>
      )}
    </div>
  )
}

