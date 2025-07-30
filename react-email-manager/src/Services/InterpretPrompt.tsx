import axios from "axios";
import type { AxiosResponse } from "axios";
import type { AuthGoogleTokens } from "../Types/AuthGoogleTokens";

const api = "https://lbc5na0ke4.execute-api.us-east-1.amazonaws.com/dev/";

export const interpretPrompt = async (prompt:string) => {
  console.log(prompt)
    const response: AxiosResponse<AuthGoogleTokens> = await axios.post(api + "send_email", {
      prompt
    });
    console.log('interpret_prompt');
    console.log(response.data);
    console.log(response.status)
    return response;
};