'use client'

import { useStore } from '@/lib/store'
import { 
  PlusIcon, 
  TrashIcon, 
  ChatBubbleLeftRightIcon,
  XMarkIcon,
  CpuChipIcon,
  CogIcon,
  LinkIcon,
  DocumentTextIcon,
  ChatBubbleBottomCenterTextIcon,
  LockClosedIcon
} from '@heroicons/react/24/outline'
import { formatDistanceToNow } from 'date-fns'
import { ExportAll } from './ChatExport'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useState } from 'react'

export function Sidebar() {
  const { 
    sidebarOpen, 
    setSidebarOpen, 
    chats, 
    currentChatId, 
    setCurrentChat,
    createChat,
    deleteChat,
    navigateToChat,
    getChatUrl
  } = useStore()
  
  const pathname = usePathname()
  const router = useRouter()
  const [showShareModal, setShowShareModal] = useState(false)
  const [shareUrl, setShareUrl] = useState('')

  const handleChatClick = (chatId: string) => {
    navigateToChat(chatId)
    router.push(`/chat/${chatId}`)
  }

  const handleShareChat = (chatId: string) => {
    const url = getChatUrl(chatId)
    setShareUrl(url)
    setShowShareModal(true)
  }

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl)
      setShowShareModal(false)
      // You could add a toast notification here
    } catch (err) {
      console.error('Failed to copy URL:', err)
    }
  }

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
              const newChatId = createChat('New Chat')
              router.push(`/chat/${newChatId}`)
            }}
            className="btn btn-primary w-full flex items-center justify-center space-x-2"
          >
            <PlusIcon className="h-4 w-4" />
            <span>New Chat</span>
          </button>
          <ExportAll className="w-full" />
        </div>
        
        {/* Navigation Links */}
        <div className="mt-4 space-y-1">
          <Link
            href="/"
            className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              pathname === '/'
                ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <ChatBubbleLeftRightIcon className="h-4 w-4" />
            <span>Chats</span>
          </Link>
          
          <Link
            href="/memory"
            className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              pathname === '/memory'
                ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <CpuChipIcon className="h-4 w-4" />
            <span>Memory</span>
          </Link>
          
          <Link
            href="/documents"
            className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              pathname === '/documents'
                ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <DocumentTextIcon className="h-4 w-4" />
            <span>Documents</span>
          </Link>
          
          <Link
            href="/prompts"
            className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              pathname === '/prompts'
                ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <ChatBubbleBottomCenterTextIcon className="h-4 w-4" />
            <span>Prompts</span>
          </Link>
          
          <Link
            href="/settings"
            className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              pathname === '/settings'
                ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <CogIcon className="h-4 w-4" />
            <span>Settings</span>
          </Link>
          
          <Link
            href="/change-password"
            className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              pathname === '/change-password'
                ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <LockClosedIcon className="h-4 w-4" />
            <span>Change Password</span>
          </Link>
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
              onClick={() => handleChatClick(chat.id)}
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
                
                <div className="flex items-center space-x-1">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleShareChat(chat.id)
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-gray-400 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900 transition-all"
                    title="Share chat"
                  >
                    <LinkIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      deleteChat(chat.id)
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900 transition-all"
                    title="Delete chat"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
          GraphMind v3.0 - Open RAG Framework
        </div>
      </div>

      {/* Share Modal */}
      {showShareModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Share Chat
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Copy this link to share the chat with others:
            </p>
            <div className="flex items-center space-x-2 mb-4">
              <input
                type="text"
                value={shareUrl}
                readOnly
                className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              />
              <button
                onClick={copyToClipboard}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Copy
              </button>
            </div>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowShareModal(false)}
                className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}