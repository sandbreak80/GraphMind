import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://tradingai-rag:8000'

export async function DELETE(
  request: NextRequest,
  { params }: { params: { category: string } }
) {
  try {
    const { category } = params
    const authHeader = request.headers.get('authorization')

    const response = await fetch(`${BACKEND_URL}/memory/clear/${category}`, {
      method: 'DELETE',
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
    console.error(`Error clearing category ${params.category}:`, error)
    return NextResponse.json(
      { error: 'Failed to clear category' },
      { status: 500 }
    )
  }
}
