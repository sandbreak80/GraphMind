import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://tradingai-rag:8000'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const category = searchParams.get('category') || 'general'
    const limit = searchParams.get('limit') || '10'
    const authHeader = request.headers.get('authorization')
    
    const response = await fetch(`${BACKEND_URL}/memory/insights/admin?category=${category}&limit=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader || '',
      },
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching user insights:', error)
    return NextResponse.json(
      { error: 'Failed to fetch user insights' },
      { status: 500 }
    )
  }
}
