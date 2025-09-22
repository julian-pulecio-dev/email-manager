import axios from "axios";
import type { AxiosResponse } from "axios";
import type { AuthGoogleTokens } from "../Types/AuthGoogleTokens";

const api = "https://cg08e6lye1.execute-api.us-east-1.amazonaws.com/test/";

export const getLabels = async (): Promise<AxiosResponse<AuthGoogleTokens>> => {
  console.log("Fetching labels from API...");
  const response = await axios.post(api + "list_categories", {}, {
    headers: {
      "Content-Type": "application/json",
    },
  });

  console.log("list_categories");
  console.log(response.data);
  console.log(response.status);
  return response;

};
