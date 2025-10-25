import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://graphmind-rag:8000'

export async function GET(
  request: NextRequest,
  { params }: { params: { mode: string } }
) {
  try {
    const { mode } = params
    const authHeader = request.headers.get('authorization')

    const response = await fetch(`${BACKEND_URL}/user-prompts/${mode}`, {
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
    console.error(`Error fetching user prompt for mode ${params.mode}:`, error)
    return NextResponse.json(
      { error: 'Failed to fetch user prompt' },
      { status: 500 }
    )
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { mode: string } }
) {
  try {
    const { mode } = params
    const body = await request.json()
    const authHeader = request.headers.get('authorization')

    const response = await fetch(`${BACKEND_URL}/user-prompts/${mode}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader || '',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error(`Error updating user prompt for mode ${params.mode}:`, error)
    return NextResponse.json(
      { error: 'Failed to update user prompt' },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { mode: string } }
) {
  try {
    const { mode } = params
    const authHeader = request.headers.get('authorization')

    const response = await fetch(`${BACKEND_URL}/user-prompts/${mode}`, {
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
    console.error(`Error clearing user prompt for mode ${params.mode}:`, error)
    return NextResponse.json(
      { error: 'Failed to clear user prompt' },
      { status: 500 }
    )
  }
}