import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://rag-service:8000'

export async function GET(request: NextRequest) {
  try {
    const response = await fetch(`${BACKEND_URL}/ollama/models`, {
      method: 'GET',
    })

    const data = await response.json()
    
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('Ollama models API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}