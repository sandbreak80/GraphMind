'use client'

import { useState, useRef, useEffect } from 'react'
import { PaperAirplaneIcon } from '@heroicons/react/24/outline'

interface MessageInputProps {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  onKeyPress: (e: React.KeyboardEvent) => void
  disabled?: boolean
  placeholder?: string
}

export function MessageInput({
  value,
  onChange,
  onSend,
  onKeyPress,
  disabled = false,
  placeholder = "Type your message..."
}: MessageInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (textareaRef.current) {
      // Force reset height to get accurate scroll height
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.overflowY = 'hidden'
      
      // Get the natural height of the content
      const scrollHeight = textareaRef.current.scrollHeight
      
      // Set height to content height, but cap at 256px
      const newHeight = Math.min(scrollHeight, 256)
      textareaRef.current.style.height = `${newHeight}px`
      
      // Enable scrolling if content exceeds max height
      if (scrollHeight > 256) {
        textareaRef.current.style.overflowY = 'auto'
      }
      
      // Ensure the textarea can handle large content
      textareaRef.current.style.whiteSpace = 'pre-wrap'
      textareaRef.current.style.wordWrap = 'break-word'
    }
  }, [value])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (value.trim() && !disabled) {
      onSend()
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex space-x-2">
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={onKeyPress}
          disabled={disabled}
          placeholder={placeholder}
          className="input w-full resize-none min-h-[44px] max-h-64 py-3 pr-12"
          rows={1}
          style={{ 
            overflowY: 'auto',
            minHeight: '44px',
            maxHeight: '256px',
            height: 'auto'
          }}
        />
        <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
          <button
            type="submit"
            disabled={!value.trim() || disabled}
            className="p-2 rounded-md text-primary-600 hover:text-primary-700 hover:bg-primary-50 dark:text-primary-400 dark:hover:text-primary-300 dark:hover:bg-primary-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <PaperAirplaneIcon className="h-5 w-5" />
          </button>
        </div>
        {/* Character counter for debugging */}
        {value.length > 0 && (
          <div className="absolute bottom-1 right-12 text-xs text-gray-500 dark:text-gray-400">
            {value.length.toLocaleString()} chars
          </div>
        )}
      </div>
    </form>
  )
}