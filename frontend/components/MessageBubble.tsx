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
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'} space-x-2`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-2' : 'mr-2'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isUser 
              ? 'bg-primary-600 text-white' 
              : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
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
          <div className={`inline-block p-4 rounded-lg ${
            isUser
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
          }`}>
            {isUser ? (
              <div className="whitespace-pre-wrap">{message.content}</div>
            ) : (
              <div className="prose prose-sm max-w-none dark:prose-invert prose-table:table-auto prose-th:border prose-th:border-gray-300 prose-th:px-4 prose-th:py-2 prose-th:bg-gray-50 prose-th:font-semibold prose-td:border prose-td:border-gray-300 prose-td:px-4 prose-td:py-2 prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-li:text-gray-900 dark:prose-li:text-gray-100 prose-p:text-gray-900 dark:prose-p:text-gray-100 prose-strong:text-gray-900 dark:prose-strong:text-gray-100 prose-em:text-gray-900 dark:prose-em:text-gray-100">
                {message.isProcessing && (
                  <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
                    <span>Processing your request...</span>
                  </div>
                )}
                <ReactMarkdown
                  remarkPlugins={[remarkGfm, remarkMath]}
                  rehypePlugins={[rehypeKatex, rehypeRaw, rehypeSanitize]}
                  components={{
                    code({ node, className, children, ...props }: any) {
                      const inline = false;
                      const match = /language-(\w+)/.exec(className || '')
                      return !inline && match ? (
                        <SyntaxHighlighter
                          style={tomorrow}
                          language={match[1]}
                          PreTag="div"
                          {...props}
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={`${className} bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm`} {...props}>
                          {children}
                        </code>
                      )
                    },
                    table({ children, ...props }: any) {
                      return (
                        <div className="overflow-x-auto my-4">
                          <table className="min-w-full border-collapse border border-gray-300 dark:border-gray-600" {...props}>
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
                        <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left font-semibold text-gray-900 dark:text-gray-100" {...props}>
                          {children}
                        </th>
                      )
                    },
                    td({ children, ...props }: any) {
                      return (
                        <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-900 dark:text-gray-100" {...props}>
                          {children}
                        </td>
                      )
                    },
                    blockquote({ children, ...props }: any) {
                      return (
                        <blockquote className="border-l-4 border-primary-500 pl-4 py-2 my-4 bg-gray-50 dark:bg-gray-800 italic" {...props}>
                          {children}
                        </blockquote>
                      )
                    },
                    hr({ ...props }: any) {
                      return (
                        <hr className="my-6 border-gray-300 dark:border-gray-600" {...props} />
                      )
                    },
                    ul({ children, ...props }: any) {
                      return (
                        <ul className="list-disc list-inside my-4 space-y-1" {...props}>
                          {children}
                        </ul>
                      )
                    },
                    ol({ children, ...props }: any) {
                      return (
                        <ol className="list-decimal list-inside my-4 space-y-1" {...props}>
                          {children}
                        </ol>
                      )
                    },
                    li({ children, ...props }: any) {
                      return (
                        <li className="text-gray-900 dark:text-gray-100" {...props}>
                          {children}
                        </li>
                      )
                    },
                    h1({ children, ...props }: any) {
                      return (
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 my-4" {...props}>
                          {children}
                        </h1>
                      )
                    },
                    h2({ children, ...props }: any) {
                      return (
                        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 my-3" {...props}>
                          {children}
                        </h2>
                      )
                    },
                    h3({ children, ...props }: any) {
                      return (
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 my-2" {...props}>
                          {children}
                        </h3>
                      )
                    },
                    h4({ children, ...props }: any) {
                      return (
                        <h4 className="text-base font-semibold text-gray-900 dark:text-gray-100 my-2" {...props}>
                          {children}
                        </h4>
                      )
                    },
                    h5({ children, ...props }: any) {
                      return (
                        <h5 className="text-sm font-semibold text-gray-900 dark:text-gray-100 my-1" {...props}>
                          {children}
                        </h5>
                      )
                    },
                    h6({ children, ...props }: any) {
                      return (
                        <h6 className="text-sm font-medium text-gray-900 dark:text-gray-100 my-1" {...props}>
                          {children}
                        </h6>
                      )
                    },
                    p({ children, ...props }: any) {
                      return (
                        <p className="my-2 text-gray-900 dark:text-gray-100" {...props}>
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
                        <em className="italic text-gray-900 dark:text-gray-100" {...props}>
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
                      return (
                        <img 
                          src={src} 
                          alt={alt} 
                          className="max-w-full h-auto rounded-lg my-4" 
                          {...props} 
                        />
                      )
                    },
                    pre({ children, ...props }: any) {
                      return (
                        <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto my-4" {...props}>
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