import { useState } from 'react'
import { Outlet } from "react-router";
import './App.css'
import { UserProvider } from "./Context/useAuth";
import { GoogleOAuthProvider } from '@react-oauth/google';

function App() {
  return (
    <GoogleOAuthProvider clientId="736009949949-ekbue316djiqb7ljq2q75rh2vp6b9hq7.apps.googleusercontent.com">
      <UserProvider>
        <Outlet />
      </UserProvider>
    </GoogleOAuthProvider>
  )
}

export default App
