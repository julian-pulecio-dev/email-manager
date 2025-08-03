import { useState } from 'react'
import { Outlet } from "react-router";
import './App.css'
import { UserProvider } from "./Context/useAuth";
import { GoogleOAuthProvider } from '@react-oauth/google';

function App() {
  return (
    <GoogleOAuthProvider clientId="68404229391-50kt67jb079h7fjabuppd6me4eth5932.apps.googleusercontent.com">
      <UserProvider>
        <Outlet />
      </UserProvider>
    </GoogleOAuthProvider>
  )
}

export default App
