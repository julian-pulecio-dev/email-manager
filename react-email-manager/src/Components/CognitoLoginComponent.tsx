import {cognitoUserPool} from "../Config/CognitoUserPool";
import { useAuth } from "../Context/useAuth";

const COGNITO_DOMAIN = cognitoUserPool.Domain;
const CLIENT_ID = cognitoUserPool.ClientId;
const REDIRECT_URI = cognitoUserPool.RedirectSignIn;
const RESPONSE_TYPE = cognitoUserPool.ResponseType;
const PROVIDER = "";

const CognitoLoginComponent = () => {

  const { logoutUser } = useAuth();

  const handleLogin = () => {
    logoutUser()
    window.location.href = getLoginUrl();
  };

  const getLoginUrl = () => {
    return `${COGNITO_DOMAIN}/login?client_id=${CLIENT_ID}&response_type=${RESPONSE_TYPE}&scope=email+openid+profile&redirect_uri=${encodeURIComponent(
        REDIRECT_URI
    )}${PROVIDER}`;
  };

  return (
    <div>
      <button onClick={handleLogin}>Login With Cognito</button>
    </div>
  );
};

export default CognitoLoginComponent;