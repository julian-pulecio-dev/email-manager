import axios from "axios";
import type { AxiosResponse } from "axios";
import type { AuthGoogleTokens } from "../../Types/AuthGoogleTokens";

const api = "https://8ay9rilai8.execute-api.us-east-1.amazonaws.com/dev/";

export const getGoogleOauthTokens = async (code:string) => {
  console.log(code)
    const response: AxiosResponse<AuthGoogleTokens> = await axios.post(api + "get_google_oauth_tokens", {
      code
    });
    console.log('get_google_oauth_tokens');
    console.log(response.data);
    console.log(response.status)
    return response;
    
  };