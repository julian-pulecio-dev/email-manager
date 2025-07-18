import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { router } from "./Routes/Routes";
import "./index.css";

const rootElement = document.getElementById("root");
if (!rootElement) throw new Error("Failed to find the root element");

const root = ReactDOM.createRoot(rootElement);

root.render(
  <GoogleOAuthProvider clientId="TU_CLIENT_ID_AQUI">
    <RouterProvider router={router} />
  </GoogleOAuthProvider>
);
