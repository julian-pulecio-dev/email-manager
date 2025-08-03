import axios from "axios";
import type { AxiosResponse } from "axios";
import type { AuthGoogleTokens } from "../Types/AuthGoogleTokens";

const api = "https://iuhs6kem95.execute-api.us-east-1.amazonaws.com/dev/";

export const interpretPrompt = async (formData: FormData): Promise<AxiosResponse<AuthGoogleTokens>> => {
  const response = await axios.post(api + "send_email", formData);

  console.log("interpret_prompt");
  console.log(response.data);
  console.log(response.status);
  return response;
};
