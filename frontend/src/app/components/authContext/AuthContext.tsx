import React, { createContext, useContext, useState } from "react";
import { UserRole } from "../../types/user";

type AuthContextType = {
  user: string | null;
  role: UserRole | null;   // ✅ FIXED
  accessToken: string | null;
  login: (data: { user: string; role: UserRole; token: string }) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);



export const AuthProvider = ({children}:any) => {
  const [user, setUser] = useState<string | null>(null);
  const [role, setRole] = useState<UserRole | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  
 const login = ({ user, role, token }: { user: string; role: UserRole; token: string }) => {
  setUser(user);
  setRole(role);
  setAccessToken(token);
};

  const logout = () => {
    setUser(null);
    setRole(null);
    setAccessToken(null);
  };

 return (
    <AuthContext.Provider value={{ user, role, accessToken, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext)!;
};