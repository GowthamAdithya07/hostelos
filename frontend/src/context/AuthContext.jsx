import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('user');
      return saved && saved !== 'undefined' && saved !== 'null' ? JSON.parse(saved) : null;
    } catch (err) {
      console.warn('Failed to parse cached user:', err);
      localStorage.removeItem('user');
      return null;
    }
  });

  const [token, setToken] = useState(() => {
    const t = localStorage.getItem('token');
    return t && t !== 'undefined' && t !== 'null' ? t : null;
  });

  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAccounts = async () => {
    try {
      const res = await api.get('/auth/accounts');
      setAccounts(res.data || []);
    } catch (err) {
      console.warn('Failed to fetch interconnected accounts:', err?.message);
    }
  };

  // Sync and verify current user on mount
  useEffect(() => {
    let isMounted = true;

    const verifyUser = async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken && storedToken !== 'undefined' && storedToken !== 'null') {
        try {
          const res = await api.get('/auth/me');
          if (isMounted) {
            setUser(res.data);
            localStorage.setItem('user', JSON.stringify(res.data));
          }
        } catch (err) {
          console.warn('Session verification failed on mount:', err?.message);
          if (isMounted) {
            setUser(null);
            setToken(null);
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('user');
          }
        }
      } else {
        if (isMounted) {
          setUser(null);
          setToken(null);
        }
      }

      if (isMounted) {
        setLoading(false);
      }
    };

    verifyUser();
    fetchAccounts();

    return () => {
      isMounted = false;
    };
  }, []);

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const { access_token, refresh_token, user: loggedUser } = res.data;

    localStorage.setItem('token', access_token);
    localStorage.setItem('refreshToken', refresh_token);
    localStorage.setItem('user', JSON.stringify(loggedUser));

    setToken(access_token);
    setUser(loggedUser);
    fetchAccounts();
    return loggedUser;
  };

  const switchAccount = async (email) => {
    const res = await api.post('/auth/switch', { email });
    const { access_token, refresh_token, user: loggedUser } = res.data;

    localStorage.setItem('token', access_token);
    localStorage.setItem('refreshToken', refresh_token);
    localStorage.setItem('user', JSON.stringify(loggedUser));

    setToken(access_token);
    setUser(loggedUser);
    return loggedUser;
  };

  const register = async (name, email, password, role = 'USER') => {
    await api.post('/auth/register', { name, email, password, role });
    // Auto login after successful registration
    const user = await login(email, password);
    fetchAccounts();
    return user;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  const isAdmin = user?.role === 'INSTITUTE_HEAD';
  const isWarden = user?.role === 'WARDEN';
  const isStudent = user?.role === 'STUDENT';
  const isWardenOrAdmin = user?.role === 'WARDEN' || user?.role === 'INSTITUTE_HEAD';

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        accounts,
        loading,
        login,
        switchAccount,
        fetchAccounts,
        register,
        logout,
        isAdmin,
        isWarden,
        isStudent,
        isWardenOrAdmin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
