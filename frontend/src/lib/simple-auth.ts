// Simple backend API auth client
// Calls backend directly instead of using Better Auth

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterCredentials {
  email: string;
  password: string;
  name: string;
}

interface AuthResponse {
  user?: {
    id: string;
    email: string;
    name: string;
  };
  token?: string;
  error?: {
    message: string;
  };
}

export async function loginUser(credentials: LoginCredentials): Promise<AuthResponse> {
  try {
    console.log('[Auth] Calling backend login...');
    
    // Call backend login endpoint
    const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.text();
      return { error: { message: error || 'Login failed' } };
    }

    const data = await response.json();
    
    // Store token
    if (data.token) {
      localStorage.setItem('bearer_token', data.token);
      document.cookie = `bearer_token=${data.token};path=/;SameSite=Lax;max-age=${60*60*24*7}`;
    }

    return data;
  } catch (error) {
    console.error('[Auth] Login error:', error);
    return { error: { message: 'Network error' } };
  }
}

export async function registerUser(credentials: RegisterCredentials): Promise<AuthResponse> {
  try {
    console.log('[Auth] Calling backend register...');
    
    // Call backend register endpoint
    const response = await fetch(`${BACKEND_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.text();
      return { error: { message: error || 'Registration failed' } };
    }

    const data = await response.json();
    
    // Store token
    if (data.token) {
      localStorage.setItem('bearer_token', data.token);
      document.cookie = `bearer_token=${data.token};path=/;SameSite=Lax;max-age=${60*60*24*7}`;
    }

    return data;
  } catch (error) {
    console.error('[Auth] Register error:', error);
    return { error: { message: 'Network error' } };
  }
}

export function logoutUser(): void {
  localStorage.removeItem('bearer_token');
  localStorage.removeItem('auth-storage');
  document.cookie = 'bearer_token=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';
}

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('bearer_token');
}

// Export compatibility functions for existing code
export const authClient = {
  signIn: {
    email: loginUser,
  },
  signUp: {
    email: registerUser,
  },
  signOut: logoutUser,
};

export async function generateAndStoreJwtToken(): Promise<string | null> {
  // Token is already stored in loginUser
  return getToken();
}

export function storeJwtToken(token: string): void {
  localStorage.setItem('bearer_token', token);
  document.cookie = `bearer_token=${token};path=/;SameSite=Lax;max-age=${60*60*24*7}`;
}

export function getJwtToken(): string | null {
  return getToken();
}

export function clearJwtToken(): void {
  logoutUser();
}

export function syncTokenCookie(): void {
  // Token already synced in login
}
