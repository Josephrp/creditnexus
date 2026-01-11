import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

interface User {
  id: number;
  email: string;
  display_name: string;
  profile_image: string | null;
  role: string;
  is_active: boolean;
  last_login: string | null;
  created_at: string | null;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  display_name: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  authError: string | null;
  login: (credentials: LoginCredentials) => Promise<boolean>;
  register: (data: RegisterData) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  clearError: () => void;
}

const TOKEN_KEY = 'creditnexus_access_token';
const REFRESH_TOKEN_KEY = 'creditnexus_refresh_token';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

function getStoredRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

function storeTokens(tokens: AuthTokens): void {
  localStorage.setItem(TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

function clearTokens(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  const token = getStoredToken();
  const headers = new Headers(options.headers);
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  const response = await fetch(url, { ...options, headers });
  
  return response;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [authError, setAuthError] = useState<string | null>(null);

  // #region agent log
  const logData3 = {location:'AuthContext.tsx:79',message:'AuthProvider initializing',data:{isLoading,hasToken:!!getStoredToken()},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'};
  console.log('[DEBUG]', logData3);
  fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(logData3)}).catch((e)=>console.error('[DEBUG] Fetch failed:',e));
  // #endregion

  const refreshUser = async () => {
    const token = getStoredToken();
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.tsx:84',message:'refreshUser called',data:{hasToken:!!token},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    if (!token) {
      setUser(null);
      setIsLoading(false);
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.tsx:88',message:'No token, setting loading false',data:{timestamp:Date.now()},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      return;
    }

    try {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.tsx:93',message:'Calling /api/auth/me',data:{url:'/api/auth/me'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      const response = await fetchWithAuth('/api/auth/me');
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.tsx:94',message:'API response received',data:{status:response.status,ok:response.ok,statusText:response.statusText},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      
      if (response.ok) {
        const data = await response.json();
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.tsx:97',message:'Response data parsed',data:{authenticated:data.authenticated,hasUser:!!data.user},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
        // #endregion
        if (data.authenticated && data.user) {
          setUser(data.user);
        } else {
          setUser(null);
          clearTokens();
        }
      } else if (response.status === 401) {
        const refreshToken = getStoredRefreshToken();
        if (refreshToken) {
          const refreshed = await refreshTokens(refreshToken);
          if (refreshed) {
            await refreshUser();
            return;
          }
        }
        setUser(null);
        clearTokens();
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Error fetching user:', error);
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.tsx:117',message:'Error in refreshUser',data:{error:error instanceof Error?error.message:String(error),errorName:error instanceof Error?error.name:'Unknown'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      setUser(null);
    } finally {
      setIsLoading(false);
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/b4962ed0-f261-4fa9-86f3-a557335b330a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.tsx:121',message:'refreshUser completed, loading set to false',data:{isLoading:false,hasUser:!!user},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
    }
  };

  const refreshTokens = async (refreshToken: string): Promise<boolean> => {
    try {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (response.ok) {
        const tokens: AuthTokens = await response.json();
        storeTokens(tokens);
        return true;
      }
    } catch (error) {
      console.error('Error refreshing token:', error);
    }
    return false;
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    setAuthError(null);
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        const tokens: AuthTokens = await response.json();
        storeTokens(tokens);
        await refreshUser();
        return true;
      } else {
        const error = await response.json().catch(() => ({ detail: 'Login failed' }));
        // Handle Pydantic validation errors (422)
        if (response.status === 422 && error.detail) {
          if (Array.isArray(error.detail)) {
            // Pydantic validation errors are arrays
            const errorMessages = error.detail.map((e: any) => {
              const field = e.loc ? e.loc.join('.') : 'field';
              return `${field}: ${e.msg || e.message || String(e)}`;
            });
            setAuthError(errorMessages.join('; '));
          } else if (typeof error.detail === 'string') {
            setAuthError(error.detail);
          } else {
            setAuthError('Invalid email or password format');
          }
        } else {
          setAuthError(error.detail || 'Login failed');
        }
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      setAuthError('Network error. Please try again.');
      return false;
    }
  };

  const register = async (data: RegisterData): Promise<boolean> => {
    setAuthError(null);
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        const tokens: AuthTokens = await response.json();
        storeTokens(tokens);
        await refreshUser();
        return true;
      } else {
        const error = await response.json();
        let errorMessage = 'Registration failed';
        if (error.detail) {
          if (typeof error.detail === 'string') {
            errorMessage = error.detail;
          } else if (Array.isArray(error.detail)) {
            errorMessage = error.detail.map((e: any) => e.msg || e.message || String(e)).join('; ');
          }
        }
        setAuthError(errorMessage);
        return false;
      }
    } catch (error) {
      console.error('Registration error:', error);
      setAuthError('Network error. Please try again.');
      return false;
    }
  };

  const logout = async () => {
    try {
      await fetchWithAuth('/api/auth/logout', { method: 'POST' });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearTokens();
      setUser(null);
    }
  };

  const clearError = () => setAuthError(null);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        authError,
        login,
        register,
        logout,
        refreshUser,
        clearError,
      }}
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

export { fetchWithAuth };
