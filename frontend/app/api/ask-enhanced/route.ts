import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://172.23.0.3:8000'

export async function POST(request: NextRequest) {
  try {
    const body = await request.text()
    const authHeader = request.headers.get('authorization')
    
    const response = await fetch(`${BACKEND_URL}/ask-enhanced`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader || '',
      },
      body: body,
    })

    const data = await response.json()
    
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('Ask enhanced API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}