import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from "../Context/useAuth";

const params = new URLSearchParams({
    client_id: '68404229391-50kt67jb079h7fjabuppd6me4eth5932.apps.googleusercontent.com',
    redirect_uri: 'http://localhost:5173/google-oauth-confirm-code',
    response_type: "code",
    scope: "https://www.googleapis.com/auth/gmail.modify email profile openid",
    access_type: "offline",
    prompt: "consent",
  });

const CallbackSocialLoginPage = () => {
  const { callbackSocialLoginUser } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleGoogleLogin = () => {
    window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
  };

  
  useEffect(() => {
    const handleCallback = async () => {
      const searchParams = new URLSearchParams(location.search);
      const code = searchParams.get('code');
      if (!code) {
        throw new Error('Authorization code not found');
      }
      console.log('Authorization code:', code);
      let res = await callbackSocialLoginUser(code, 'Google')
      if (res) {
        console.log('User authenticated successfully');
        handleGoogleLogin();
        navigate('/');
      }
    };

    handleCallback();
  }, [location, navigate]);

  return (
    <>
    <div className="callback-page">
      <h2>Processing login...</h2>
      <p>Please wait while we authenticate your account.</p>
    </div>
    </>
  );
};

export default CallbackSocialLoginPage;
