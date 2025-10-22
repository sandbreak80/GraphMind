'use client'

import { Source } from '@/lib/store'
import { DocumentTextIcon, LinkIcon } from '@heroicons/react/24/outline'
import { useState } from 'react'

interface SourceListProps {
  sources: Source[]
}

export function SourceList({ sources }: SourceListProps) {
  const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set())

  const toggleSource = (index: number) => {
    const newExpanded = new Set(expandedSources)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedSources(newExpanded)
  }

  if (sources.length === 0) return null

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
        Sources ({sources.length})
      </h4>
      <div className="space-y-1">
        {sources.map((source, index) => (
          <div
            key={index}
            className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700"
          >
            <button
              onClick={() => toggleSource(index)}
              className="w-full text-left flex items-start space-x-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded p-1 -m-1"
            >
              <DocumentTextIcon className="h-4 w-4 text-gray-500 dark:text-gray-400 mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {source.section || source.doc_id}
                </div>
                {source.page && (
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Page {source.page}
                  </div>
                )}
                <div className="text-xs text-gray-400 dark:text-gray-500">
                  Score: {source.score.toFixed(3)}
                </div>
              </div>
              <div className="text-xs text-gray-400 dark:text-gray-500">
                {expandedSources.has(index) ? '▼' : '▶'}
              </div>
            </button>
            
            {expandedSources.has(index) && (
              <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                  {source.text}
                </div>
                <div className="mt-2 flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                  <span>Doc ID: {source.doc_id}</span>
                  {source.page && <span>• Page: {source.page}</span>}
                  {source.section && <span>• Section: {source.section}</span>}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}