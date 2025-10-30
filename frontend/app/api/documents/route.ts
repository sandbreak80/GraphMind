import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  try {
    const authorization = request.headers.get('authorization')
    
    const response = await fetch('http://graphmind-rag:8000/documents', {
      headers: {
        'Authorization': authorization || '',
      },
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch documents' },
      { status: 500 }
    )
  }
}


