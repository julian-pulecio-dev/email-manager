import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from "../Context/useAuth";


const CallbackSocialLoginPage = () => {
  const { callbackSocialLoginUser } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  
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
