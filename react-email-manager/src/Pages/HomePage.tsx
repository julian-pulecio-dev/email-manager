import CognitoLoginComponent from '../Components/CognitoLoginComponent';
import GoogleOAuthComponent from "../Components/GoogleOAuthComponent";
import PromptBoxComponent from '../Components/PromptBoxComponent';
import CreateLabelComponent from '../Components/CreateLabelComponent';

const HomePage = () => {
  return (
    <div>
      <h2>Home Page</h2>
      <CognitoLoginComponent />
      <GoogleOAuthComponent />
      <PromptBoxComponent />
      <CreateLabelComponent />
    </div>
  );
};

export default HomePage;
