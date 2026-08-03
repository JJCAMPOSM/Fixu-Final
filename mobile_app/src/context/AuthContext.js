import React, { createContext, useContext, useEffect, useState } from 'react';
import * as SecureStore from 'expo-secure-store';
import { login as apiLogin, register as apiRegister, logout as apiLogout } from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [booting, setBooting] = useState(true);
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    (async () => {
      const savedToken = await SecureStore.getItemAsync('fixu_token');
      const savedUser = await SecureStore.getItemAsync('fixu_user');
      if (savedToken && savedUser) {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      }
      setBooting(false);
    })();
  }, []);

  const persistSession = async (newToken, newUser) => {
    await SecureStore.setItemAsync('fixu_token', newToken);
    await SecureStore.setItemAsync('fixu_user', JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  };

  const login = async (email, password) => {
    const data = await apiLogin(email, password);
    await persistSession(data.token, data.user);
  };

  const register = async (name, email, password) => {
    const data = await apiRegister(name, email, password);
    await persistSession(data.token, data.user);
  };

  const logout = async () => {
    try {
      if (token) await apiLogout(token);
    } catch (e) {
      // Si el servidor no responde, igual cerramos sesión localmente
    }
    await SecureStore.deleteItemAsync('fixu_token');
    await SecureStore.deleteItemAsync('fixu_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ booting, token, user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
