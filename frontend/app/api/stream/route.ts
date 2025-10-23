import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://rag-service:8000'

export async function POST(request: NextRequest) {
  try {
    const body = await request.text()
    const authHeader = request.headers.get('authorization')
    const url = new URL(request.url)
    const mode = url.searchParams.get('mode') || 'enhanced'
    
    let endpoint = '/ask-enhanced'
    if (mode === 'obsidian') {
      endpoint = '/ask-obsidian'
    } else if (mode === 'spec') {
      endpoint = '/ask'
    }
    
    const response = await fetch(`${BACKEND_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader || '',
      },
      body: body,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    // Stream the response back to the client
    const stream = new ReadableStream({
      start(controller) {
        const reader = response.body?.getReader()
        if (!reader) {
          controller.close()
          return
        }

        function pump(): Promise<void> {
          return reader!.read().then(({ done, value }) => {
            if (done) {
              controller.close()
              return
            }
            controller.enqueue(value)
            return pump()
          })
        }

        return pump()
      }
    })

    return new NextResponse(stream, {
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    })
  } catch (error) {
    console.error('Stream API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}