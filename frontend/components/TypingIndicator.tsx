'use client'

export function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="flex max-w-[80%] flex-row space-x-2">
        <div className="flex-shrink-0 mr-2">
          <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 flex items-center justify-center">
            <div className="w-4 h-4 rounded-full bg-gray-400"></div>
          </div>
        </div>
        <div className="flex-1">
          <div className="bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 mr-auto max-w-[80%] rounded-lg px-4 py-2">
            <div className="typing-indicator">
              <div className="typing-dot" style={{ animationDelay: '0ms' }}></div>
              <div className="typing-dot" style={{ animationDelay: '150ms' }}></div>
              <div className="typing-dot" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}