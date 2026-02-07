import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const { toast } = useToast();

  // Check if user is logged in on app load
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('authToken');
      const savedUser = localStorage.getItem('user');
      
      if (token && savedUser) {
        try {
          // Verify token is still valid
          const userData = await authAPI.getMe();
          setUser(userData);
          setIsAuthenticated(true);
        } catch (error) {
          // Token is invalid, clear storage
          localStorage.removeItem('authToken');
          localStorage.removeItem('user');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials) => {
    try {
      setLoading(true);
      const response = await authAPI.login(credentials);
      
      // Store token and user data
      localStorage.setItem('authToken', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      
      setUser(response.user);
      setIsAuthenticated(true);
      
      toast({
        title: "Success",
        description: "Successfully logged in!",
      });
      
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed';
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      const response = await authAPI.register(userData);
      
      // Store token and user data
      localStorage.setItem('authToken', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      
      setUser(response.user);
      setIsAuthenticated(true);
      
      toast({
        title: "Success",
        description: "Account created successfully!",
      });
      
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Registration failed';
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      // Continue with logout even if API call fails
      console.error('Logout API error:', error);
    } finally {
      // Clear local storage and state
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      setUser(null);
      setIsAuthenticated(false);
      
      toast({
        title: "Success",
        description: "Successfully logged out!",
      });
    }
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};