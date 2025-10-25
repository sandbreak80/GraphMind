'use client'

import { useEffect, useState } from 'react'
import { useStore } from '@/lib/store'
import { AuthWrapper } from '@/components/AuthWrapper'
import { UIEnhancements } from '@/components/UIEnhancements'
import { useRouter } from 'next/navigation'
import {
  SparklesIcon,
  DocumentMagnifyingGlassIcon,
  GlobeAltIcon,
  BookOpenIcon,
  LightBulbIcon,
  RocketLaunchIcon,
  ShieldCheckIcon,
  BoltIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

function LandingPage({ onGetStarted }: { onGetStarted: () => void }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <UIEnhancements />
      
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -inset-[10px] opacity-50">
            <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl animate-blob"></div>
            <div className="absolute top-0 -right-4 w-72 h-72 bg-yellow-500 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-2000"></div>
            <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-4000"></div>
          </div>
        </div>

        {/* Content */}
        <div className="relative">
          {/* Navigation */}
          <nav className="container mx-auto px-6 py-6 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                <SparklesIcon className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-white">GraphMind</span>
            </div>
            <button
              onClick={onGetStarted}
              className="px-6 py-2.5 bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white rounded-lg font-medium transition-all hover:scale-105 border border-white/20"
            >
              Sign In
            </button>
          </nav>

          {/* Hero Content */}
          <div className="container mx-auto px-6 py-20 md:py-32">
            <div className="text-center max-w-4xl mx-auto">
              <div className="inline-flex items-center space-x-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full border border-white/20 mb-8">
                <RocketLaunchIcon className="w-4 h-4 text-purple-300" />
                <span className="text-sm text-purple-100">Advanced AI-Powered Research Platform</span>
              </div>
              
              <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
                Your Knowledge,
                <br />
                <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-yellow-400 bg-clip-text text-transparent">
                  Supercharged by AI
                </span>
              </h1>
              
              <p className="text-xl md:text-2xl text-purple-100 mb-12 leading-relaxed">
                GraphMind combines your documents, Obsidian notes, and web research
                <br />
                with cutting-edge AI to deliver instant, accurate insights.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <button
                  onClick={onGetStarted}
                  className="group relative px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold text-lg transition-all hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/50"
                >
                  <span className="relative z-10 flex items-center space-x-2">
                    <span>Get Started Free</span>
                    <BoltIcon className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </span>
                </button>
                
                <a
                  href="#features"
                  className="px-8 py-4 bg-white/10 backdrop-blur-sm text-white rounded-xl font-semibold text-lg transition-all hover:bg-white/20 border border-white/20"
                >
                  Explore Features
                </a>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-8 mt-20 max-w-3xl mx-auto">
                <div className="text-center">
                  <div className="text-4xl font-bold text-white mb-2">4</div>
                  <div className="text-purple-200">AI Modes</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-white mb-2">400MB</div>
                  <div className="text-purple-200">File Upload</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-white mb-2">∞</div>
                  <div className="text-purple-200">Possibilities</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="relative py-20 bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Four Powerful Research Modes
            </h2>
            <p className="text-xl text-purple-200">
              Choose the perfect source for every question
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* RAG Mode */}
            <div className="group p-6 bg-gradient-to-br from-blue-900/50 to-blue-800/30 backdrop-blur-sm rounded-2xl border border-blue-500/20 hover:border-blue-400/50 transition-all hover:scale-105 hover:shadow-xl hover:shadow-blue-500/20">
              <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center mb-4 group-hover:bg-blue-500/30 transition-colors">
                <DocumentMagnifyingGlassIcon className="w-6 h-6 text-blue-300" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Document RAG</h3>
              <p className="text-blue-100 text-sm">
                Search your uploaded PDFs, videos, and documents with AI-powered semantic search
              </p>
            </div>

            {/* Obsidian Mode */}
            <div className="group p-6 bg-gradient-to-br from-purple-900/50 to-purple-800/30 backdrop-blur-sm rounded-2xl border border-purple-500/20 hover:border-purple-400/50 transition-all hover:scale-105 hover:shadow-xl hover:shadow-purple-500/20">
              <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center mb-4 group-hover:bg-purple-500/30 transition-colors">
                <BookOpenIcon className="w-6 h-6 text-purple-300" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Obsidian Notes</h3>
              <p className="text-purple-100 text-sm">
                Connect your personal knowledge base and search your Obsidian vault
              </p>
            </div>

            {/* Web Search Mode */}
            <div className="group p-6 bg-gradient-to-br from-green-900/50 to-green-800/30 backdrop-blur-sm rounded-2xl border border-green-500/20 hover:border-green-400/50 transition-all hover:scale-105 hover:shadow-xl hover:shadow-green-500/20">
              <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center mb-4 group-hover:bg-green-500/30 transition-colors">
                <GlobeAltIcon className="w-6 h-6 text-green-300" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Web Search</h3>
              <p className="text-green-100 text-sm">
                Get real-time information from the web with privacy-focused SearXNG
              </p>
            </div>

            {/* Research Mode */}
            <div className="group p-6 bg-gradient-to-br from-orange-900/50 to-orange-800/30 backdrop-blur-sm rounded-2xl border border-orange-500/20 hover:border-orange-400/50 transition-all hover:scale-105 hover:shadow-xl hover:shadow-orange-500/20">
              <div className="w-12 h-12 bg-orange-500/20 rounded-xl flex items-center justify-center mb-4 group-hover:bg-orange-500/30 transition-colors">
                <LightBulbIcon className="w-6 h-6 text-orange-300" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Comprehensive</h3>
              <p className="text-orange-100 text-sm">
                Combine all sources for the most thorough research possible
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="relative py-20">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <ShieldCheckIcon className="w-8 h-8 text-purple-300" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Privacy First</h3>
              <p className="text-purple-200">
                Your data stays on your infrastructure. Self-hosted and secure.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-pink-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <BoltIcon className="w-8 h-8 text-pink-300" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Lightning Fast</h3>
              <p className="text-purple-200">
                Chunked uploads, parallel processing, and optimized retrieval.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-yellow-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <ChartBarIcon className="w-8 h-8 text-yellow-300" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Production Ready</h3>
              <p className="text-purple-200">
                Battle-tested with comprehensive monitoring and error handling.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="relative py-20">
        <div className="container mx-auto px-6">
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl p-12 text-center">
            <h2 className="text-4xl font-bold text-white mb-4">
              Ready to Transform Your Research?
            </h2>
            <p className="text-xl text-purple-100 mb-8">
              Start using GraphMind today and experience AI-powered knowledge management.
            </p>
            <button
              onClick={onGetStarted}
              className="px-8 py-4 bg-white text-purple-600 rounded-xl font-semibold text-lg transition-all hover:scale-105 hover:shadow-2xl"
            >
              Get Started Now
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-white/10 py-8">
        <div className="container mx-auto px-6 text-center text-purple-200 text-sm">
          <p>© 2025 GraphMind. Open source AI research platform.</p>
        </div>
      </div>

      <style jsx global>{`
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  )
}

export default function Home() {
  const { isAuthenticated, checkAuth } = useStore()
  const router = useRouter()
  const [showLanding, setShowLanding] = useState(true)
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    const authenticated = checkAuth()
    setIsChecking(false)
    if (authenticated) {
      setShowLanding(false)
    }
  }, [checkAuth])

  const handleGetStarted = () => {
    setShowLanding(false)
  }

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto"></div>
          <p className="mt-4 text-purple-200">Loading...</p>
        </div>
      </div>
    )
  }

  if (showLanding && !isAuthenticated) {
    return <LandingPage onGetStarted={handleGetStarted} />
  }

  return (
    <>
      <UIEnhancements />
      <AuthWrapper />
    </>
  )
}