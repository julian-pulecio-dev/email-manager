import { createContext, useEffect, useState } from "react";
import { callbackSocialLogin } from "../Services/CallbackSocialLogin";
import { getGoogleOauthTokens } from "../Services/GetGoogleOauthTokens";
import type { UserProfile } from "../Types/User";
import { decodeToken } from "../Helpers/DecodeJWT";
import React from "react";
import axios from "axios";

type UserContextType = {
  user: UserProfile | null;
  token: string | null;
  error: string | null;
  callbackSocialLoginUser: (code: string, provider: string) => Promise<boolean>;
  getGoogleOauthTokensUser: (code: string, provider: string) => Promise<boolean>;
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
    const storedUser = localStorage.getItem("user");
    const storedToken = localStorage.getItem("token");
    if (storedUser && storedToken) {
      console.log("User and token found in localStorage");
      setUser(JSON.parse(storedUser));
      setToken(storedToken);
      axios.defaults.headers.common["Authorization"] = `Bearer ${storedToken}`;
    }
    setIsReady(true);
  }, []);

  const callbackSocialLoginUser = async (code: string, provider: string) => {
    try {
      const res = await callbackSocialLogin(code, provider);
      if (res?.status === 200) {
        const decodedToken = decodeToken(res?.data.idToken!);
        if (!decodedToken?.email) {
          setError("El token no contiene un email válido");
          return false;
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
        return true;
      }
      return false;
    } catch (err: any) {
      setError(err.message || "Error en callbackSocialLoginUser");
      return false;
    }
  };

  const getGoogleOauthTokensUser = async (code: string, provider: string) => {
    try {
      const res = await getGoogleOauthTokens(code, provider);
      if (res?.status === 200) {
        // Guarda tokens en localStorage (no solo "approved")
        localStorage.setItem("google_oauth", JSON.stringify(res.data));
        return true;
      }
      return false;
    } catch (err: any) {
      setError(err.message || "Error en getGoogleOauthTokensUser");
      return false;
    }
  };

  const logoutUser = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    localStorage.removeItem("google_oauth");
    setUser(null);
    setToken(null);
    delete axios.defaults.headers.common["Authorization"];
  };

  const isLoggedIn = () => {
    if (!token) return false;
    try {
      const decoded = decodeToken(token);
      if (!decoded?.exp) return false;
      return decoded.exp * 1000 > Date.now(); // token no expirado
    } catch {
      return false;
    }
  };

  return (
    <UserContext.Provider
      value={{
        callbackSocialLoginUser,
        getGoogleOauthTokensUser,
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
