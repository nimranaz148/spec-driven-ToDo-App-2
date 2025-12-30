import { createAuthClient } from "better-auth/client";
import { jwtClient } from "better-auth/client/plugins";

// Create auth client
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  plugins: [
    jwtClient(), // Enables authClient.token() method
  ],
});

/**
 * Generate JWT and store in localStorage + cookie
 * CALL THIS AFTER SUCCESSFUL LOGIN/SIGNUP
 */
export async function generateAndStoreJwtToken(): Promise<string | null> {
  try {
    // Primary method: authClient.token()
    console.log('[JWT] Trying authClient.token()...');
    const response = await (authClient as unknown as { token: () => Promise<{ error?: unknown; data?: { token: string } }> }).token();
    console.log('[JWT] authClient.token() response:', JSON.stringify(response, null, 2));

    if (!response.error && response.data?.token) {
      storeJwtToken(response.data.token);
      return response.data.token;
    }

    // Fallback: direct fetch to /api/auth/token
    console.log('[JWT] Fallback: fetching /api/auth/token...');
    const fetchResponse = await fetch(`/api/auth/token`, {
      method: 'GET',
      credentials: 'include',
    });

    console.log('[JWT] Fetch response status:', fetchResponse.status);

    if (fetchResponse.ok) {
      const data = await fetchResponse.json();
      console.log('[JWT] Token data:', data);
      if (data?.token) {
        storeJwtToken(data.token);
        return data.token;
      }
    } else {
      const errorText = await fetchResponse.text();
      console.error('[JWT] Fetch error:', errorText);
    }

    return null;
  } catch (error) {
    console.error('[JWT] Error generating token:', error);
    return null;
  }
}

/**
 * Store token in BOTH localStorage AND cookie
 * - localStorage: for Axios requests
 * - cookie: for Edge runtime (middleware, etc.)
 */
export function storeJwtToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("bearer_token", token);
    document.cookie = `bearer_token=${token};path=/;SameSite=Lax;max-age=${60*60*24*7}`;
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
 * Clear all auth tokens - CALL ON LOGOUT
 */
export function clearJwtToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("bearer_token");
    document.cookie = "bearer_token=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
  }
}
