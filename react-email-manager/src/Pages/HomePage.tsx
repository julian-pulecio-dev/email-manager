import CognitoLoginComponent from '../Components/CognitoLoginComponent';
import GoogleOAuthComponent from "../Components/GoogleOAuthComponent";
import PromptBoxComponent from '../Components/PromptBoxComponent';

const HomePage = () => {
  return (
    <div>
      <h2>Home Page</h2>
      <CognitoLoginComponent />
      <GoogleOAuthComponent />
      <PromptBoxComponent />
    </div>
  );
};

export default HomePage;
