'use client'

import { Source } from '@/lib/store'
import { 
  DocumentTextIcon, 
  LinkIcon, 
  BookOpenIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  MagnifyingGlassIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import { useState, useMemo } from 'react'

interface SourceListProps {
  sources: Source[]
}

interface SourceWithIndex extends Source {
  originalIndex: number
}

interface CategorizedSources {
  documents: SourceWithIndex[]
  web: SourceWithIndex[]
  obsidian: SourceWithIndex[]
  other: SourceWithIndex[]
}

export function SourceList({ sources }: SourceListProps) {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['documents']))
  const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set())
  const [searchQuery, setSearchQuery] = useState('')
  const [showAll, setShowAll] = useState(false)

  // Categorize sources based on doc_id patterns
  const categorizedSources = useMemo((): CategorizedSources => {
    const categories: CategorizedSources = {
      documents: [],
      web: [],
      obsidian: [],
      other: []
    }

    sources.forEach((source, index) => {
      const docId = source.doc_id.toLowerCase()
      
      if (docId.includes('obsidian') || docId.includes('note')) {
        categories.obsidian.push({ ...source, originalIndex: index })
      } else if (docId.includes('web') || docId.includes('search') || docId.includes('url')) {
        categories.web.push({ ...source, originalIndex: index })
      } else if (docId.includes('pdf') || docId.includes('document') || docId.includes('doc')) {
        categories.documents.push({ ...source, originalIndex: index })
      } else {
        categories.other.push({ ...source, originalIndex: index })
      }
    })

    return categories
  }, [sources])

  // Filter sources based on search query
  const filteredSources = useMemo(() => {
    if (!searchQuery.trim()) return categorizedSources

    const query = searchQuery.toLowerCase()
    const filtered: CategorizedSources = {
      documents: [],
      web: [],
      obsidian: [],
      other: []
    }

    Object.entries(categorizedSources).forEach(([category, sources]) => {
      filtered[category as keyof CategorizedSources] = sources.filter((source: SourceWithIndex) =>
        source.text.toLowerCase().includes(query) ||
        source.doc_id.toLowerCase().includes(query) ||
        (source.section && source.section.toLowerCase().includes(query))
      )
    })

    return filtered
  }, [categorizedSources, searchQuery])

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories)
    if (newExpanded.has(category)) {
      newExpanded.delete(category)
    } else {
      newExpanded.add(category)
    }
    setExpandedCategories(newExpanded)
  }

  const toggleSource = (originalIndex: number) => {
    const newExpanded = new Set(expandedSources)
    if (newExpanded.has(originalIndex)) {
      newExpanded.delete(originalIndex)
    } else {
      newExpanded.add(originalIndex)
    }
    setExpandedSources(newExpanded)
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'documents':
        return <DocumentTextIcon className="h-4 w-4" />
      case 'web':
        return <LinkIcon className="h-4 w-4" />
      case 'obsidian':
        return <BookOpenIcon className="h-4 w-4" />
      default:
        return <DocumentTextIcon className="h-4 w-4" />
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'documents':
        return 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
      case 'web':
        return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20'
      case 'obsidian':
        return 'text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20'
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20'
    }
  }

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'documents':
        return 'Documents'
      case 'web':
        return 'Web Sources'
      case 'obsidian':
        return 'Personal Notes'
      default:
        return 'Other Sources'
    }
  }

  const totalSources = sources.length
  const totalFilteredSources = Object.values(filteredSources).reduce((sum, sources) => sum + sources.length, 0)

  if (sources.length === 0) return null

  return (
    <div className="mt-4 space-y-3">
      {/* Header with search and controls */}
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          Sources ({totalFilteredSources}{totalFilteredSources !== totalSources ? ` of ${totalSources}` : ''})
        </h4>
        <div className="flex items-center space-x-2">
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              Clear
            </button>
          )}
          <button
            onClick={() => setShowAll(!showAll)}
            className="text-xs text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
          >
            {showAll ? 'Show Less' : 'Show All'}
          </button>
        </div>
      </div>

      {/* Search bar */}
      <div className="relative">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search sources..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
        {searchQuery && (
          <button
            onClick={() => setSearchQuery('')}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Categories */}
      <div className="space-y-2">
        {Object.entries(filteredSources).map(([category, categorySources]) => {
          if (categorySources.length === 0) return null

          const isExpanded = expandedCategories.has(category)
          const shouldShowAll = showAll || categorySources.length <= 3
          const displaySources = shouldShowAll ? categorySources : categorySources.slice(0, 3)

          return (
            <div key={category} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
              {/* Category Header */}
              <button
                onClick={() => toggleCategory(category)}
                className={`w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors ${getCategoryColor(category)}`}
              >
                <div className="flex items-center space-x-3">
                  {getCategoryIcon(category)}
                  <span className="font-medium text-sm">
                    {getCategoryLabel(category)}
                  </span>
                  <span className="text-xs px-2 py-1 rounded-full bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300">
                    {categorySources.length}
                  </span>
                </div>
                {isExpanded ? (
                  <ChevronDownIcon className="h-4 w-4" />
                ) : (
                  <ChevronRightIcon className="h-4 w-4" />
                )}
              </button>

              {/* Category Content */}
              {isExpanded && (
                <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                  <div className="p-3 space-y-2">
                    {displaySources.map((source: SourceWithIndex, index: number) => (
                      <div
                        key={source.originalIndex}
                        className="group bg-gray-50 dark:bg-gray-700 rounded-lg p-3 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                      >
                        <button
                          onClick={() => toggleSource(source.originalIndex)}
                          className="w-full text-left flex items-start space-x-3"
                        >
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                              {source.section || source.doc_id}
                            </div>
                            {source.page && (
                              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                Page {source.page}
                              </div>
                            )}
                            <div className="flex items-center space-x-2 mt-1">
                              <span className="text-xs text-gray-400 dark:text-gray-500">
                                Score: {source.score.toFixed(3)}
                              </span>
                              <span className="text-xs text-gray-400 dark:text-gray-500">•</span>
                              <span className="text-xs text-gray-400 dark:text-gray-500">
                                {source.text.length > 100 ? `${source.text.substring(0, 100)}...` : source.text}
                              </span>
                            </div>
                          </div>
                          <div className="text-xs text-gray-400 dark:text-gray-500 flex-shrink-0">
                            {expandedSources.has(source.originalIndex) ? '▼' : '▶'}
                          </div>
                        </button>

                        {expandedSources.has(source.originalIndex) && (
                          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
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

                    {/* Show more/less button */}
                    {categorySources.length > 3 && (
                      <button
                        onClick={() => setShowAll(!showAll)}
                        className="w-full text-center text-xs text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 py-2"
                      >
                        {shouldShowAll 
                          ? `Show Less (${categorySources.length - 3} hidden)`
                          : `Show ${categorySources.length - 3} More`
                        }
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* No results message */}
      {totalFilteredSources === 0 && searchQuery && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <MagnifyingGlassIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No sources found matching "{searchQuery}"</p>
        </div>
      )}
    </div>
  )
}