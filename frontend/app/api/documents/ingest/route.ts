import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const authorization = request.headers.get('authorization')
    
    if (!authorization) {
      console.error('Ingest API: No authorization header provided')
      return NextResponse.json(
        { detail: 'Unauthorized - No authorization header' },
        { status: 401 }
      )
    }
    
    const body = await request.json()
    
    console.log('Ingest API: Forwarding request to backend...')
    const response = await fetch('http://graphmind-rag:8000/ingest', {
      method: 'POST',
      headers: {
        'Authorization': authorization,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    const data = await response.json().catch(() => ({ detail: 'Unknown error' }))
    
    if (!response.ok) {
      console.error('Ingest API: Backend error:', response.status, data)
      return NextResponse.json(data, { status: response.status })
    }
    
    console.log('Ingest API: Success:', data)
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('Ingest API: Exception:', error)
    return NextResponse.json(
      { detail: `Failed to start ingestion: ${error instanceof Error ? error.message : 'Unknown error'}` },
      { status: 500 }
    )
  }
}


