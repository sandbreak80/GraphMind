'use client'

import { Message } from '@/lib/store'
import { UserIcon, CpuChipIcon } from '@heroicons/react/24/outline'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import rehypeRaw from 'rehype-raw'
import rehypeSanitize from 'rehype-sanitize'
import { format } from 'date-fns'
import { SourceList } from './SourceList'
import { ResponseTimeDisplay } from './ResponseTimeDisplay'

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-[fadeInUp_0.4s_ease-out]`}>
      <div className={`flex max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'} ${isUser ? 'space-x-reverse' : ''} space-x-3`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center shadow-md transition-transform duration-200 hover:scale-110 ${
            isUser 
              ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white' 
              : 'bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 text-gray-700 dark:text-gray-300'
          }`}>
            {isUser ? (
              <UserIcon className="h-5 w-5" />
            ) : (
              <CpuChipIcon className={`h-5 w-5 ${message.isProcessing ? 'animate-pulse' : ''}`} />
            )}
          </div>
        </div>

        {/* Message Content */}
        <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
          <div className={`inline-block p-4 rounded-2xl shadow-sm transition-all duration-200 ${
            isUser
              ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white shadow-blue-500/20 hover:shadow-md hover:shadow-blue-500/30'
              : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200/50 dark:border-gray-700/50 hover:shadow-md'
          }`}>
            {isUser ? (
              <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</div>
            ) : (
              <div className="prose prose-sm max-w-none dark:prose-invert">
                {message.isProcessing && (
                  <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400 mb-3">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
                    <span>Processing...</span>
                  </div>
                )}
                <ReactMarkdown
                  remarkPlugins={[remarkGfm, remarkMath]}
                  rehypePlugins={[rehypeKatex, rehypeRaw, rehypeSanitize]}
                  components={{
                    code({ node, className, children, ...props }: any) {
                      const inline = !className?.includes('language-');
                      const match = /language-(\w+)/.exec(className || '')
                      
                      if (inline) {
                        return (
                          <code className="bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
                            {children}
                          </code>
                        )
                      }
                      
                      return match ? (
                        <div className="my-3 rounded-lg overflow-hidden border border-gray-300 dark:border-gray-600">
                          <div className="bg-gray-800 text-gray-300 px-3 py-1.5 text-sm font-medium">
                            {match[1].toUpperCase()}
                          </div>
                          <SyntaxHighlighter
                            style={tomorrow}
                            language={match[1]}
                            PreTag="div"
                            className="!m-0 !p-3 !text-sm"
                            showLineNumbers={false}
                            wrapLines={true}
                            {...props}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        </div>
                      ) : (
                        <pre className="bg-gray-900 text-gray-100 p-3 rounded-lg overflow-x-auto my-3">
                          <code className="text-sm font-mono" {...props}>
                            {children}
                          </code>
                        </pre>
                      )
                    },
                    table({ children, ...props }: any) {
                      return (
                        <div className="overflow-x-auto my-3 rounded-lg border border-gray-300 dark:border-gray-600">
                          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700" {...props}>
                            {children}
                          </table>
                        </div>
                      )
                    },
                    thead({ children, ...props }: any) {
                      return (
                        <thead className="bg-gray-50 dark:bg-gray-800" {...props}>
                          {children}
                        </thead>
                      )
                    },
                    th({ children, ...props }: any) {
                      return (
                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-700 dark:text-gray-300" {...props}>
                          {children}
                        </th>
                      )
                    },
                    td({ children, ...props }: any) {
                      return (
                        <td className="px-4 py-2 text-sm text-gray-900 dark:text-gray-100" {...props}>
                          {children}
                        </td>
                      )
                    },
                    blockquote({ children, ...props }: any) {
                      return (
                        <blockquote className="border-l-4 border-primary-500 pl-4 py-2 my-3 bg-gray-50 dark:bg-gray-800/50 italic text-sm text-gray-700 dark:text-gray-300 rounded-r" {...props}>
                          {children}
                        </blockquote>
                      )
                    },
                    hr({ ...props }: any) {
                      return (
                        <hr className="my-4 border-0 border-t border-gray-300 dark:border-gray-600" {...props} />
                      )
                    },
                    ul({ children, ...props }: any) {
                      return (
                        <ul className="list-disc list-inside my-2 space-y-1 ml-4 text-sm" {...props}>
                          {children}
                        </ul>
                      )
                    },
                    ol({ children, ...props }: any) {
                      return (
                        <ol className="list-decimal list-inside my-2 space-y-1 ml-4 text-sm" {...props}>
                          {children}
                        </ol>
                      )
                    },
                    li({ children, ...props }: any) {
                      return (
                        <li className="text-sm text-gray-900 dark:text-gray-100 leading-relaxed" {...props}>
                          {children}
                        </li>
                      )
                    },
                    h1({ children, ...props }: any) {
                      return (
                        <h1 className="text-lg font-bold text-gray-900 dark:text-gray-100 mt-4 mb-3 border-b border-gray-300 dark:border-gray-600 pb-2" {...props}>
                          {children}
                        </h1>
                      )
                    },
                    h2({ children, ...props }: any) {
                      return (
                        <h2 className="text-base font-bold text-gray-900 dark:text-gray-100 mt-4 mb-2" {...props}>
                          {children}
                        </h2>
                      )
                    },
                    h3({ children, ...props }: any) {
                      return (
                        <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100 mt-3 mb-2" {...props}>
                          {children}
                        </h3>
                      )
                    },
                    h4({ children, ...props }: any) {
                      return (
                        <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mt-3 mb-1.5" {...props}>
                          {children}
                        </h4>
                      )
                    },
                    h5({ children, ...props }: any) {
                      return (
                        <h5 className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-2 mb-1" {...props}>
                          {children}
                        </h5>
                      )
                    },
                    h6({ children, ...props }: any) {
                      return (
                        <h6 className="text-sm font-medium text-primary-600 dark:text-primary-400 mt-2 mb-1" {...props}>
                          {children}
                        </h6>
                      )
                    },
                    p({ children, ...props }: any) {
                      return (
                        <p className="my-2 text-sm text-gray-900 dark:text-gray-100 leading-relaxed" {...props}>
                          {children}
                        </p>
                      )
                    },
                    strong({ children, ...props }: any) {
                      return (
                        <strong className="font-semibold text-gray-900 dark:text-gray-100" {...props}>
                          {children}
                        </strong>
                      )
                    },
                    em({ children, ...props }: any) {
                      return (
                        <em className="italic" {...props}>
                          {children}
                        </em>
                      )
                    },
                    a({ children, href, ...props }: any) {
                      return (
                        <a 
                          href={href} 
                          className="text-primary-600 dark:text-primary-400 hover:underline" 
                          target="_blank" 
                          rel="noopener noreferrer"
                          {...props}
                        >
                          {children}
                        </a>
                      )
                    },
                    img({ src, alt, ...props }: any) {
                      // Don't render images, just show nothing or alt text
                      return null
                    },
                    pre({ children, ...props }: any) {
                      return (
                        <pre className="bg-gray-900 text-gray-100 p-3 rounded-lg overflow-x-auto my-3 text-sm" {...props}>
                          {children}
                        </pre>
                      )
                    }
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            )}
          </div>

          {/* Message Metadata */}
          <div className={`text-xs text-gray-500 dark:text-gray-400 mt-1 ${
            isUser ? 'text-right' : 'text-left'
          }`}>
            <div className="flex items-center space-x-2">
              <span>{format(new Date(message.timestamp), 'HH:mm')}</span>
              {message.model && (
                <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-full">
                  {message.model.split(':')[0]}
                </span>
              )}
              {message.mode && (
                <span className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded-full">
                  {message.mode}
                </span>
              )}
              {message.totalSources && message.totalSources > 0 && (
                <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full">
                  {message.totalSources} sources
                </span>
              )}
              {!isUser && (
                <ResponseTimeDisplay messageId={message.id} />
              )}
            </div>
          </div>

          {/* Sources */}
          {message.sources && message.sources.length > 0 && (
            <div className="mt-2">
              <SourceList sources={message.sources} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}