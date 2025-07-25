import React from "react";

const GoogleOAuthComponent: React.FC = () => {  
  const params = new URLSearchParams({
    client_id: '736009949949-ekbue316djiqb7ljq2q75rh2vp6b9hq7.apps.googleusercontent.com',
    redirect_uri: 'http://localhost:5173/google-oauth-confirm-code',
    response_type: "code",
    scope: "https://www.googleapis.com/auth/gmail.readonly email profile openid",
    access_type: "offline",
    prompt: "consent",
  });

  const handleLogin = () => {
    window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
  };

  return (
    <button onClick={handleLogin} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
      Conectar con Gmail
    </button>
  );
};

export default GoogleOAuthComponent;
