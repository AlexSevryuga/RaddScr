'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from './api';
import type { User, LoginCredentials, RegisterData } from '@/types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Load user on mount
  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const userData = await authApi.getMe();
      setUser(userData);
    } catch (error) {
      localStorage.removeItem('access_token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials: LoginCredentials) => {
    await authApi.login(credentials);
    await loadUser();
    router.push('/dashboard');
  };

  const register = async (data: RegisterData) => {
    const newUser = await authApi.register(data);
    // After registration, auto-login
    await login({ email: data.email, password: data.password });
  };

  const logout = () => {
    authApi.logout();
    setUser(null);
    router.push('/login');
  };

  const refreshUser = async () => {
    if (user) {
      const userData = await authApi.getMe();
      setUser(userData);
    }
  };

  return (
    <AuthContext.Provider
      value={{ user, loading, login, register, logout, refreshUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
