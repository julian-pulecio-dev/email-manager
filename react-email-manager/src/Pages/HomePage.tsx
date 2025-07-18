import CognitoLoginComponent from '../Components/CognitoLoginComponent';
import GoogleOAuthComponent from "../Components/GoogleOAuthComponent";

const HomePage = () => {
  return (
    <div>
      <h2>Home Page</h2>
      <CognitoLoginComponent />
      <GoogleOAuthComponent />
    </div>
  );
};

export default HomePage;
