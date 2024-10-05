import React, { createContext, useState, useEffect, useContext } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    verifyToken();
  }, []);

  const verifyToken = async () => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      try {
        const response = await fetch('http://localhost:8000/auth/users/me/', {
          method: 'GET',
          headers: {
            'Authorization': `JWT ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const userData = await response.json();
          console.log("verification succesful");
          setUser(userData);
        } else {
          // If verification fails, log the user out
          logout();
        }
      } catch (error) {
        console.error('Token verification failed:', error);
        logout();
      }
    }
    setLoading(false);
  };

  const login = async (userData) => {
    setUser(userData);
    await verifyToken();
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setUser(null);
  };

  if (loading) {
    return <div>Loading...</div>; 
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, verifyToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);