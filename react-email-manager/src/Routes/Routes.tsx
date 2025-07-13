import { createBrowserRouter } from "react-router-dom";
import App from "../App";
import CallbackSocialLoginPage from "../Pages/CallbackSocialLoginPage";
import HomePage from "../Pages/HomePage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { path: "", element: <HomePage /> },
      { path: "social-login-confirm-code", element: <CallbackSocialLoginPage /> },
    ],
  },
]);
