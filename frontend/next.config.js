/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://rag-service:8000',
  },
  async rewrites() {
    return [
      {
        source: '/api/ask',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://rag-service:8000'}/ask`,
      },
      {
        source: '/api/ask-enhanced',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://rag-service:8000'}/ask-enhanced`,
      },
      {
        source: '/api/ask-obsidian',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://rag-service:8000'}/ask-obsidian`,
      },
      {
        source: '/api/ask-research',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://rag-service:8000'}/ask-research`,
      },
      {
        source: '/api/auth/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://rag-service:8000'}/auth/:path*`,
      },
      {
        source: '/api/health',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://rag-service:8000'}/health`,
      },
      {
        source: '/api/ollama/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://rag-service:8000'}/ollama/:path*`,
      },
      {
        source: '/api/generate-chat-title',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://rag-service:8000'}/generate-chat-title`,
      },
    ]
  },
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig