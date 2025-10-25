'use client'

import React, { useState, useEffect } from 'react'
import { useStore } from '../lib/store'
import { formatDistanceToNow } from 'date-fns'

interface MemoryInsight {
  insight: string
  created_at: number
}

interface MemoryCategory {
  category: string
  insights: MemoryInsight[]
  count: number
}

interface UserProfile {
  user_id: string
  preferences: Record<string, any>
  strategies: string[]
  recent_insights: MemoryInsight[]
  created_at: number
  updated_at: number
}

interface MemoryStats {
  total_insights: number
  categories: Record<string, number>
  oldest_insight: number
  newest_insight: number
}

export default function MemoryManagement() {
  const { authToken } = useStore()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [categories, setCategories] = useState<MemoryCategory[]>([])
  const [stats, setStats] = useState<MemoryStats | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [exportFormat, setExportFormat] = useState<'json' | 'csv' | 'txt'>('json')

  useEffect(() => {
    loadMemoryData()
  }, [])

  const loadMemoryData = async () => {
    try {
      setLoading(true)
      setError('')
      
      // Load user profile
      const profileResponse = await fetch('/api/memory/profile', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      if (profileResponse.ok) {
        const profileData = await profileResponse.json()
        setProfile(profileData)
      }
      
      // Load insights for each category
      const categories = ['general', 'strategy_discussion', 'preferences', 'context']
      const categoryData: MemoryCategory[] = []
      
      for (const category of categories) {
        const insightsResponse = await fetch(`/api/memory/insights?category=${category}`, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        })
        
        if (insightsResponse.ok) {
          const insightsData = await insightsResponse.json()
          categoryData.push({
            category,
            insights: insightsData.insights || [],
            count: insightsData.insights?.length || 0
          })
        }
      }
      
      setCategories(categoryData)
      
      // Calculate stats
      const totalInsights = categoryData.reduce((sum, cat) => sum + cat.count, 0)
      const categoryStats = categoryData.reduce((acc, cat) => {
        acc[cat.category] = cat.count
        return acc
      }, {} as Record<string, number>)
      
      const allInsights = categoryData.flatMap(cat => cat.insights)
      const timestamps = allInsights.map(insight => insight.created_at)
      
      setStats({
        total_insights: totalInsights,
        categories: categoryStats,
        oldest_insight: timestamps.length > 0 ? Math.min(...timestamps) : 0,
        newest_insight: timestamps.length > 0 ? Math.max(...timestamps) : 0
      })
      
    } catch (err) {
      setError('Failed to load memory data')
    } finally {
      setLoading(false)
    }
  }

  const clearCategory = async (category: string) => {
    try {
      const response = await fetch(`/api/memory/clear/${category}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      if (response.ok) {
        await loadMemoryData() // Reload data
      } else {
        setError('Failed to clear category')
      }
    } catch (err) {
      setError('Failed to clear category')
    }
  }

  const exportMemory = async () => {
    try {
      const exportData = {
        profile,
        categories: categories.reduce((acc, cat) => {
          acc[cat.category] = cat.insights
          return acc
        }, {} as Record<string, MemoryInsight[]>),
        stats,
        exported_at: new Date().toISOString()
      }
      
      let content: string
      let filename: string
      let mimeType: string
      
      switch (exportFormat) {
        case 'json':
          content = JSON.stringify(exportData, null, 2)
          filename = `memory-export-${new Date().toISOString().split('T')[0]}.json`
          mimeType = 'application/json'
          break
        case 'csv':
          const csvRows = ['Category,Insight,Created At']
          categories.forEach(cat => {
            cat.insights.forEach(insight => {
              csvRows.push(`"${cat.category}","${insight.insight.replace(/"/g, '""')}","${new Date(insight.created_at * 1000).toISOString()}"`)
            })
          })
          content = csvRows.join('\n')
          filename = `memory-export-${new Date().toISOString().split('T')[0]}.csv`
          mimeType = 'text/csv'
          break
        case 'txt':
          content = `Memory Export - ${new Date().toISOString()}\n\n`
          categories.forEach(cat => {
            if (cat.insights.length > 0) {
              content += `=== ${cat.category.toUpperCase()} ===\n`
              cat.insights.forEach(insight => {
                content += `- ${insight.insight}\n`
                content += `  Created: ${new Date(insight.created_at * 1000).toLocaleString()}\n\n`
              })
            }
          })
          filename = `memory-export-${new Date().toISOString().split('T')[0]}.txt`
          mimeType = 'text/plain'
          break
      }
      
      const blob = new Blob([content], { type: mimeType })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
    } catch (err) {
      setError('Failed to export memory data')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-900 dark:text-white">Loading memory data...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <div className="flex">
          <div className="text-red-600 dark:text-red-400">{error}</div>
          <button 
            onClick={loadMemoryData}
            className="ml-4 text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-300"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  const filteredCategories = selectedCategory === 'all' 
    ? categories 
    : categories.filter(cat => cat.category === selectedCategory)

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Memory Management</h1>
        <p className="text-gray-600 dark:text-gray-400">View and manage your stored insights, preferences, and strategies.</p>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{stats.total_insights}</div>
            <div className="text-sm text-blue-800 dark:text-blue-300">Total Insights</div>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">{Object.keys(stats.categories).length}</div>
            <div className="text-sm text-green-800 dark:text-green-300">Categories</div>
          </div>
          <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {stats.oldest_insight > 0 ? formatDistanceToNow(new Date(stats.oldest_insight * 1000), { addSuffix: true }) : 'N/A'}
            </div>
            <div className="text-sm text-purple-800 dark:text-purple-300">Oldest Insight</div>
          </div>
          <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
            <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
              {stats.newest_insight > 0 ? formatDistanceToNow(new Date(stats.newest_insight * 1000), { addSuffix: true }) : 'N/A'}
            </div>
            <div className="text-sm text-orange-800 dark:text-orange-300">Newest Insight</div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Category:</label>
          <select 
            value={selectedCategory} 
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Categories</option>
            {categories.map(cat => (
              <option key={cat.category} value={cat.category}>
                {cat.category.replace('_', ' ')} ({cat.count})
              </option>
            ))}
          </select>
        </div>
        
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Export Format:</label>
          <select 
            value={exportFormat} 
            onChange={(e) => setExportFormat(e.target.value as 'json' | 'csv' | 'txt')}
            className="border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="json">JSON</option>
            <option value="csv">CSV</option>
            <option value="txt">Text</option>
          </select>
        </div>
        
        <button
          onClick={exportMemory}
          className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm transition-colors"
        >
          Export Memory
        </button>
      </div>

      {/* Categories */}
      <div className="space-y-6">
        {filteredCategories.map(category => (
          <div key={category.category} className="border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800">
            <div className="bg-gray-50 dark:bg-gray-700/50 px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white capitalize">
                  {category.category.replace('_', ' ')} ({category.count} insights)
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {category.insights.length > 0 && (
                    `Last updated: ${formatDistanceToNow(new Date(Math.max(...category.insights.map(i => i.created_at)) * 1000), { addSuffix: true })}`
                  )}
                </p>
              </div>
              <button
                onClick={() => clearCategory(category.category)}
                className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={category.count === 0}
              >
                Clear Category
              </button>
            </div>
            
            <div className="p-4">
              {category.insights.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400 italic">No insights in this category</p>
              ) : (
                <div className="space-y-3">
                  {category.insights.map((insight, index) => (
                    <div key={index} className="border-l-4 border-primary-200 dark:border-primary-800 pl-4 py-2 bg-gray-50 dark:bg-gray-700/30 rounded-r">
                      <p className="text-gray-900 dark:text-white">{insight.insight}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {formatDistanceToNow(new Date(insight.created_at * 1000), { addSuffix: true })}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
