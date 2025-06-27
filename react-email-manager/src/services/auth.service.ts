// src/services/auth.service.ts
export async function loginWithGoogleToken(accessToken: string): Promise<any> {
  try {
    const response = await fetch('https://5whohu7bm0.execute-api.us-east-1.amazonaws.com/dev/hello_world', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`
      },
      body: JSON.stringify({ token: accessToken })
    })

    if (!response.ok) {
      throw new Error(`Error del servidor: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error en loginWithGoogleToken:', error)
    throw error
  }
}
