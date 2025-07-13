import { jwtDecode } from "jwt-decode";
import type { CustomJwtPayload } from "../Types/JwtPayload";

export function decodeToken(token:string) {
    try {
      return jwtDecode<CustomJwtPayload>(token)
    } catch (error) {
      console.error("Error decoding token:", error);
      return null;
    }
}