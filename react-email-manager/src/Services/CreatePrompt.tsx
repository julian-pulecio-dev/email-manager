import axios from "axios";
import type { AxiosResponse } from "axios";
import type { AuthGoogleTokens } from "../Types/AuthGoogleTokens";

const api = "https://cg08e6lye1.execute-api.us-east-1.amazonaws.com/test/";

export const createLabel = async (formData: FormData): Promise<AxiosResponse<AuthGoogleTokens>> => {
  const response = await axios.post(api + "label", formData);

  console.log("create_label");
  console.log(response.data);
  console.log(response.status);
  return response;
};
