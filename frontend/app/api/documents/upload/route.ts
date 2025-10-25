import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://graphmind-rag:8000'

// Disable body size limit for large file uploads (up to 400MB)
export const config = {
  api: {
    bodyParser: false,
  },
}

export const maxDuration = 300 // 5 minutes for large uploads

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization')
    if (!authHeader) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 })
    }

    // Forward the file to the backend
    const backendFormData = new FormData()
    backendFormData.append('file', file)

    // Use longer timeout for large file uploads (5 minutes)
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 300000) // 5 minutes
    
    const response = await fetch(`${BACKEND_URL}/upload`, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
      },
      body: backendFormData,
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        { error: errorData.detail || 'File upload failed' },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('File upload error:', error)
    return NextResponse.json(
      { error: 'File upload failed' },
      { status: 500 }
    )
  }
}

