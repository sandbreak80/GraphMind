'use client'

import { useStore } from '@/lib/store'
import { 
  PlusIcon, 
  TrashIcon, 
  ChatBubbleLeftRightIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import { formatDistanceToNow } from 'date-fns'
import { ExportAll } from './ChatExport'

export function Sidebar() {
  const { 
    sidebarOpen, 
    setSidebarOpen, 
    chats, 
    currentChatId, 
    setCurrentChat,
    createChat,
    deleteChat 
  } = useStore()

  if (!sidebarOpen) return null

  return (
    <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Chats
          </h2>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-1 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
        
        <div className="space-y-2">
          <button
            onClick={() => {
              const { createChat } = useStore.getState()
              createChat('New Chat')
            }}
            className="btn btn-primary w-full flex items-center justify-center space-x-2"
          >
            <PlusIcon className="h-4 w-4" />
            <span>New Chat</span>
          </button>
          <ExportAll className="w-full" />
        </div>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {chats.length === 0 ? (
          <div className="text-center text-gray-500 dark:text-gray-400 py-8">
            <ChatBubbleLeftRightIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No chats yet</p>
            <p className="text-sm">Start a new conversation</p>
          </div>
        ) : (
          chats.map((chat) => (
            <div
              key={chat.id}
              className={`group relative p-3 rounded-lg cursor-pointer transition-colors ${
                currentChatId === chat.id
                  ? 'bg-primary-100 dark:bg-primary-900 border border-primary-200 dark:border-primary-700'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
              onClick={() => setCurrentChat(chat.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {chat.title}
                  </h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {formatDistanceToNow(new Date(chat.updatedAt), { addSuffix: true })}
                  </p>
                  <div className="flex items-center space-x-2 mt-1">
                    <p className="text-xs text-gray-400 dark:text-gray-500">
                      {chat.messages.length} messages
                    </p>
                    {chat.currentModel && (
                      <span className="text-xs px-1.5 py-0.5 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded">
                        {chat.currentModel.split(':')[0]}
                      </span>
                    )}
                    {chat.averageResponseTime && (
                      <span className="text-xs text-green-600 dark:text-green-400">
                        {chat.averageResponseTime.toFixed(1)}s avg
                      </span>
                    )}
                  </div>
                </div>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    deleteChat(chat.id)
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900 transition-all"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
          TradingAI Research Platform v2.0
        </div>
      </div>
    </div>
  )
}