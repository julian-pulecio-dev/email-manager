import { createContext, useEffect, useState } from "react";
import { callbackSocialLogin } from "../Services/Auth/CallbackSocialLogin";
import type { UserProfile } from "../Types/User";
import { decodeToken } from "../Helpers/DecodeJWT";
import React from "react";
import axios from "axios";

type UserContextType = {
  user: UserProfile | null;
  token: string | null;
  error: string | null;
  callbackSocialLoginUser: (code: string, provider: string) => Promise<boolean>;
  logoutUser: () => void;
  isLoggedIn: () => boolean;
  setError: (error: string | null) => void;
};

type Props = { children: React.ReactNode };

const UserContext = createContext<UserContextType>({} as UserContextType);

export const UserProvider = ({ children }: Props) => {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    console.log("UserProvider useEffect called");
    const user = localStorage.getItem("user");
    const token = localStorage.getItem("token");
    if (user && token) {
      console.log("User and token found in localStorage");
      setUser(JSON.parse(user));
      setToken(token);
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    }
    setIsReady(true);
  }, []);


  const callbackSocialLoginUser = async (code: string, provider: string) => {
    const res = await callbackSocialLogin(code, provider);
    if (res?.status == 200) {
      const decodedToken = decodeToken(res?.data.idToken!);
      if (!decodedToken?.email) {
        throw new Error("Decoded token does not contain a valid email.");
      }
      const userObj = {
        userName: decodedToken.email,
        email: decodedToken.email,
      };
      localStorage.setItem("user", JSON.stringify(userObj));
      localStorage.setItem("token", res?.data.idToken);
      setToken(res?.data.idToken!);
      setUser(userObj!);
      axios.defaults.headers.common["Authorization"] = `Bearer ${res?.data.idToken!}`;
      return true
    }
    return false;
  };

  const logoutUser = async () => {
  };

  const isLoggedIn = () => {
    return !!user;
  };

  return (
    <UserContext.Provider
      value={{
        callbackSocialLoginUser,
        user,
        token,
        logoutUser,
        isLoggedIn,
        error,
        setError,
      }}
    >
      {isReady ? children : null}
    </UserContext.Provider>
  );
};

export const useAuth = () => React.useContext(UserContext);