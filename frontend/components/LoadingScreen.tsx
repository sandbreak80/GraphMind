'use client'

export function LoadingScreen() {
  return (
    <div className="flex h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <div className="mb-8">
          <div className="mx-auto h-16 w-16 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600"></div>
        </div>
        <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
          Loading EminiPlayer RAG
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Initializing your trading strategy assistant...
        </p>
      </div>
    </div>
  )
}