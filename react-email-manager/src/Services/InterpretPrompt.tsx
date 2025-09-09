import axios from "axios";
import type { AxiosResponse } from "axios";
import type { AuthGoogleTokens } from "../Types/AuthGoogleTokens";

const api = "https://cg08e6lye1.execute-api.us-east-1.amazonaws.com/test/";

export const interpretPrompt = async (formData: FormData): Promise<AxiosResponse<AuthGoogleTokens>> => {
  console.log('form data send_email')
  console.log(formData.values());
  const response = await axios.post(api + "send_email", formData);


  console.log("interpret_prompt");
  console.log(response.data);
  console.log(response.status);
  return response;
};
