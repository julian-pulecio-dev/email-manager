function App() {
  const login = () => {
    const clientId = '736009949949-ekbue316djiqb7ljq2q75rh2vp6b9hq7.apps.googleusercontent.com'
    const redirectUri = 'https://8c46gyc5fj.execute-api.us-east-1.amazonaws.com/dev/hello_world'
    const scope = encodeURIComponent('https://www.googleapis.com/auth/gmail.readonly')
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}&access_type=offline&prompt=consent`
    window.location.href = authUrl
  }

  return (
    <div>
      <h1>Login con Google + Acceso a Gmail API + Refresh Token</h1>
      <button onClick={login}>
        Iniciar sesión con Google
      </button>
    </div>
  )
}

export default App
