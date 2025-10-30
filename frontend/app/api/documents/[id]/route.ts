import { NextResponse } from 'next/server'

export async function DELETE(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const authorization = request.headers.get('authorization')
    
    const response = await fetch(`http://graphmind-rag:8000/documents/${params.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': authorization || '',
      },
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to delete document' },
      { status: 500 }
    )
  }
}



