import axios from "axios";
import type { AxiosResponse } from "axios";
import type { AuthGoogleTokens } from "../Types/AuthGoogleTokens";

const api = "https://cg08e6lye1.execute-api.us-east-1.amazonaws.com/test/";

export const callbackSocialLogin = async (code:string, provider:string) => {
  console.log(code)
    const response: AxiosResponse<AuthGoogleTokens> = await axios.post(api + "email_manager_social_auth_callback", {
      code,
      provider
    });
    console.log('callbackSocialLogin');
    console.log(response.data);
    console.log(response.status)
    return response;
    
  };