import { createAuthClient } from "better-auth/client";
import { jwtClient } from "better-auth/client/plugins";

// Create auth client with JWT plugin for backend API authentication
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  plugins: [
    jwtClient(), // Enable JWT token generation via authClient.token()
  ],
});

/**
 * Decode a JWT token to see its payload (for debugging)
 */
function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

/**
 * Generate and store a JWT token for backend API authentication.
 * Call this after successful login/signup.
 *
 * Uses Better Auth's jwtClient plugin - the correct method is authClient.token()
 */
export async function generateAndStoreJwtToken(): Promise<string | null> {
  try {
    console.log('[Auth] ========== GENERATING JWT TOKEN ==========');

    // Method 1: Use authClient.token() - the correct Better Auth way
    console.log('[Auth] Calling authClient.token()...');
    const response = await (authClient as unknown as { token: () => Promise<{ error?: unknown; data?: { token: string } }> }).token();
    console.log('[Auth] Token response:', response);

    if (!response.error && response.data?.token) {
      const token = response.data.token;
      if (typeof window !== "undefined") {
        // Decode and log the token payload to verify correct user
        const payload = decodeJwtPayload(token);
        console.log('[Auth] JWT token payload:', payload);
        console.log('[Auth] Token user ID (sub):', payload?.sub);
        console.log('[Auth] Token user email:', payload?.email);

        // Store in both localStorage AND cookie (for Edge runtime access)
        storeJwtToken(token);
        console.log('[Auth] JWT token stored successfully, length:', token.length);
        return token;
      }
    }

    if (response.error) {
      console.warn('[Auth] authClient.token() failed:', response.error);
    }

    // Fallback: direct fetch to /api/auth/token with credentials
    console.log('[Auth] Attempting direct fetch to /api/auth/token...');
    const baseURL = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
    const fetchResponse = await fetch(`${baseURL}/api/auth/token`, {
      method: 'GET',
      credentials: 'include', // Important: include cookies for session
    });

    console.log('[Auth] Direct fetch response status:', fetchResponse.status);

    if (fetchResponse.ok) {
      const data = await fetchResponse.json();
      console.log('[Auth] Direct fetch response data:', data);
      if (data?.token) {
        // Decode and log the token payload to verify correct user
        const payload = decodeJwtPayload(data.token);
        console.log('[Auth] JWT token payload (direct fetch):', payload);
        console.log('[Auth] Token user ID (sub):', payload?.sub);

        // Store in both localStorage AND cookie (for Edge runtime access)
        storeJwtToken(data.token);
        console.log('[Auth] JWT token stored via direct fetch, length:', data.token.length);
        return data.token;
      }
    } else {
      const errorText = await fetchResponse.text();
      console.error('[Auth] Direct fetch failed:', fetchResponse.status, errorText);
    }

    console.warn('[Auth] All token generation methods failed');
    return null;
  } catch (error) {
    console.error('[Auth] Error generating JWT token:', error);
    return null;
  }
}

/**
 * Set a cookie with the given name and value.
 * Used to store the JWT token for Edge runtime access (e.g., ChatKit proxy).
 */
function setCookie(name: string, value: string, days: number = 7): void {
  if (typeof document !== "undefined") {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    // Set cookie with SameSite=Lax for security, not HttpOnly so JS can clear it
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
    console.log(`[Auth] Cookie '${name}' set, expires in ${days} days`);
  }
}

/**
 * Clear a cookie by setting its expiration to the past.
 */
function clearCookie(name: string): void {
  if (typeof document !== "undefined") {
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
    console.log(`[Auth] Cookie '${name}' cleared`);
  }
}

/**
 * Store JWT token in both localStorage AND as a cookie.
 * localStorage is for client-side API calls (Axios, SSE).
 * Cookie is for Edge runtime access (ChatKit proxy).
 */
export function storeJwtToken(token: string): void {
  if (typeof window !== "undefined") {
    // Store in localStorage for client-side access
    localStorage.setItem("bearer_token", token);
    // Also store as cookie for Edge runtime access (ChatKit proxy)
    setCookie("bearer_token", token, 7);
    console.log('[Auth] JWT token stored in localStorage AND cookie');
  }
}

/**
 * Sync the bearer_token cookie from localStorage.
 * Call this on app startup to ensure existing tokens are available to Edge runtime.
 */
export function syncTokenCookie(): void {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("bearer_token");
    if (token) {
      // Check if cookie already exists
      const cookieExists = document.cookie.includes("bearer_token=");
      if (!cookieExists) {
        console.log('[Auth] Syncing bearer_token cookie from localStorage');
        setCookie("bearer_token", token, 7);
      }
    }
  }
}

/**
 * Get JWT token from localStorage
 */
export function getJwtToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("bearer_token");
  }
  return null;
}

/**
 * Clear the stored JWT token and auth storage (call on logout)
 */
export function clearJwtToken(): void {
  if (typeof window !== "undefined") {
    console.log('[Auth] Clearing JWT token and auth storage');
    localStorage.removeItem("bearer_token");
    // Also clear the cookie
    clearCookie("bearer_token");
    // Also clear Zustand persist storage to prevent re-hydration of stale token
    localStorage.removeItem("auth-storage");
    console.log('[Auth] Cleared: bearer_token (localStorage + cookie), auth-storage');
  }
}
