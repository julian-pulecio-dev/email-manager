import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from "../Context/useAuth";


const CallbackGoogleOAuthPage = () => {
  const { getGoogleOauthTokensUser } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  
  useEffect(() => {
    const handleCallback = async () => {
      try {
        const searchParams = new URLSearchParams(location.search);
        const code = searchParams.get('code');
        const error = searchParams.get('error');
        if (error) {
          throw new Error(`OAuth error: ${error}`);
        }
        if (!code) {
          throw new Error('Authorization code not found');
        }
        console.log('Authorization code:', code);
        let res = await getGoogleOauthTokensUser(code, 'Google')
        if (res) {
          console.log('User authenticated successfully');
          navigate('/');
        }
      } catch (err) {
        console.error('Authentication failed:', err);
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

export default CallbackGoogleOAuthPage;
