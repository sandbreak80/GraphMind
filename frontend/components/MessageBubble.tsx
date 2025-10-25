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
              <div className="whitespace-pre-wrap text-xs">{message.content}</div>
            ) : (
              <div className="text-xs prose prose-xs max-w-none dark:prose-invert prose-headings:font-bold prose-headings:text-gray-900 dark:prose-headings:text-gray-100 prose-p:text-gray-900 dark:prose-p:text-gray-100 prose-strong:text-gray-900 dark:prose-strong:text-gray-100 prose-em:text-gray-900 dark:prose-em:text-gray-100 prose-li:text-gray-900 dark:prose-li:text-gray-100 prose-a:text-primary-600 dark:prose-a:text-primary-400 prose-a:no-underline hover:prose-a:underline prose-blockquote:border-primary-500 prose-blockquote:bg-gray-50 dark:prose-blockquote:bg-gray-800 prose-code:bg-gray-100 dark:prose-code:bg-gray-800 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-xs prose-pre:bg-gray-900 dark:prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-pre:border prose-pre:border-gray-300 dark:prose-pre:border-gray-600">
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
                      const inline = !className?.includes('language-');
                      const match = /language-(\w+)/.exec(className || '')
                      
                      if (inline) {
                        return (
                          <code className="bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-1.5 py-0.5 rounded text-sm font-mono border border-gray-200 dark:border-gray-700" {...props}>
                            {children}
                          </code>
                        )
                      }
                      
                      return match ? (
                        <div className="my-4 rounded-lg overflow-hidden border border-gray-300 dark:border-gray-600">
                          <div className="bg-gray-800 text-gray-300 px-4 py-2 text-xs font-medium border-b border-gray-700">
                            {match[1].toUpperCase()}
                          </div>
                          <SyntaxHighlighter
                            style={tomorrow}
                            language={match[1]}
                            PreTag="div"
                            className="!m-0 !p-4"
                            showLineNumbers={false}
                            wrapLines={true}
                            {...props}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        </div>
                      ) : (
                        <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto my-4 border border-gray-300 dark:border-gray-600">
                          <code className="text-sm font-mono" {...props}>
                            {children}
                          </code>
                        </pre>
                      )
                    },
                    table({ children, ...props }: any) {
                      return (
                        <div className="overflow-x-auto my-6 rounded-lg border border-gray-300 dark:border-gray-600 shadow-sm">
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
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider" {...props}>
                          {children}
                        </th>
                      )
                    },
                    td({ children, ...props }: any) {
                      return (
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100" {...props}>
                          {children}
                        </td>
                      )
                    },
                    blockquote({ children, ...props }: any) {
                      return (
                        <blockquote className="border-l-4 border-primary-500 pl-6 py-4 my-6 bg-gray-50 dark:bg-gray-800 italic text-gray-700 dark:text-gray-300 rounded-r-lg shadow-sm" {...props}>
                          {children}
                        </blockquote>
                      )
                    },
                    hr({ ...props }: any) {
                      return (
                        <hr className="my-8 border-0 border-t-2 border-gray-200 dark:border-gray-700" {...props} />
                      )
                    },
                    ul({ children, ...props }: any) {
                      return (
                        <ul className="list-disc list-inside my-4 space-y-2 ml-4" {...props}>
                          {children}
                        </ul>
                      )
                    },
                    ol({ children, ...props }: any) {
                      return (
                        <ol className="list-decimal list-inside my-4 space-y-2 ml-4" {...props}>
                          {children}
                        </ol>
                      )
                    },
                    li({ children, ...props }: any) {
                      return (
                        <li className="text-gray-900 dark:text-gray-100 leading-relaxed" {...props}>
                          {children}
                        </li>
                      )
                    },
                    h1({ children, ...props }: any) {
                      return (
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 my-6 border-b border-gray-200 dark:border-gray-700 pb-2" {...props}>
                          {children}
                        </h1>
                      )
                    },
                    h2({ children, ...props }: any) {
                      return (
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 my-5 border-b border-gray-200 dark:border-gray-700 pb-1" {...props}>
                          {children}
                        </h2>
                      )
                    },
                    h3({ children, ...props }: any) {
                      return (
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 my-4" {...props}>
                          {children}
                        </h3>
                      )
                    },
                    h4({ children, ...props }: any) {
                      return (
                        <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100 my-3" {...props}>
                          {children}
                        </h4>
                      )
                    },
                    h5({ children, ...props }: any) {
                      return (
                        <h5 className="text-base font-semibold text-gray-900 dark:text-gray-100 my-2" {...props}>
                          {children}
                        </h5>
                      )
                    },
                    h6({ children, ...props }: any) {
                      return (
                        <h6 className="text-sm font-medium text-gray-900 dark:text-gray-100 my-2 text-primary-600 dark:text-primary-400" {...props}>
                          {children}
                        </h6>
                      )
                    },
                    p({ children, ...props }: any) {
                      return (
                        <p className="my-4 text-gray-900 dark:text-gray-100 leading-relaxed" {...props}>
                          {children}
                        </p>
                      )
                    },
                    strong({ children, ...props }: any) {
                      return (
                        <strong className="font-bold text-gray-900 dark:text-gray-100" {...props}>
                          {children}
                        </strong>
                      )
                    },
                    em({ children, ...props }: any) {
                      return (
                        <em className="italic text-gray-700 dark:text-gray-300" {...props}>
                          {children}
                        </em>
                      )
                    },
                    a({ children, href, ...props }: any) {
                      return (
                        <a 
                          href={href} 
                          className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 hover:underline font-medium transition-colors" 
                          target="_blank" 
                          rel="noopener noreferrer"
                          {...props}
                        >
                          {children}
                        </a>
                      )
                    },
                    img({ src, alt, ...props }: any) {
                      // Enhanced image placeholder with better styling
                      return (
                        <div className="bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-6 my-6 text-center">
                          <div className="text-4xl mb-2">🖼️</div>
                          <div className="text-sm font-medium text-gray-600 dark:text-gray-400">Image Placeholder</div>
                          <div className="text-xs mt-2 text-gray-500 dark:text-gray-500 max-w-xs mx-auto">
                            {alt || 'No description available'}
                          </div>
                          {src && (
                            <div className="text-xs mt-2 text-gray-400 dark:text-gray-600 break-all">
                              {src}
                            </div>
                          )}
                        </div>
                      )
                    },
                    pre({ children, ...props }: any) {
                      return (
                        <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto my-4 border border-gray-300 dark:border-gray-600 shadow-sm" {...props}>
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