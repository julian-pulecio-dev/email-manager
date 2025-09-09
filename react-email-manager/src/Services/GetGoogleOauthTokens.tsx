import axios from "axios";
import type { AxiosResponse } from "axios";
import type { AuthGoogleTokens } from "../Types/AuthGoogleTokens";

const api = "https://cg08e6lye1.execute-api.us-east-1.amazonaws.com/test/";

export const getGoogleOauthTokens = async (code:string) => {
  console.log(code)
    const response: AxiosResponse<AuthGoogleTokens> = await axios.post(api + "google_access_tokens", {
      code
    });
    console.log('get_google_oauth_tokens');
    console.log(response.data);
    console.log(response.status)
    return response;
    
  };