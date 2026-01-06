import { betterAuth } from 'better-auth';
import { bearer, jwt } from 'better-auth/plugins';
import { nextCookies } from 'better-auth/next-js';
import pg from 'pg';

// Better Auth server configuration
// Better Auth creates these tables automatically:
// - user (id, name, email, emailVerified, image, createdAt, updatedAt)
// - session (id, userId, token, expiresAt, ipAddress, userAgent)
// - account (id, userId, providerId, accountId, providerType, etc.)
// - verification (id, identifier, value, expiresAt)

// Create PostgreSQL connection pool for Better Auth
const databaseUrl = process.env.DATABASE_URL || '';

// Log database connection attempt (only once at startup)
if (typeof process !== 'undefined' && databaseUrl) {
  console.log('[Better Auth] Connecting to database:', databaseUrl.substring(0, 40) + '...');
}

const pool = new pg.Pool({
  connectionString: databaseUrl,
  ssl: {
    rejectUnauthorized: false,
  },
  connectionTimeoutMillis: 60000,  // 60s for Neon cold starts
  idleTimeoutMillis: 30000,
  max: 3,
  min: 1,                          // Keep 1 connection warm
  keepAlive: true,
  keepAliveInitialDelayMillis: 1000,
});

// Handle pool errors gracefully
pool.on('error', (err) => {
  console.error('[Better Auth] Pool error:', err.message);
});

pool.on('connect', () => {
  console.log('[Better Auth] Database connected');
});

export const auth = betterAuth({
  // Database: Use pg Pool adapter
  database: pool,

  // Enable email/password auth
  emailAndPassword: {
    enabled: true,
  },

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24,     // Refresh daily
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // 5 min cache
    },
  },

  // Advanced options
  advanced: {
    useSecureCookies: process.env.NODE_ENV === 'production',
    // Disable database operations for debugging
    disableMigrations: false,
  },

  // CRITICAL PLUGINS (nextCookies must be LAST):
  plugins: [
    bearer(),      // Enables Bearer token auth
    jwt({          // Enables JWT token generation
      jwt: {
        expirationTime: "7d",
      },
    }),
    nextCookies(), // MUST be last - handles Next.js cookie management
  ],

  secret: process.env.BETTER_AUTH_SECRET!,
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
});

// JWT storage helpers - updated to use 'bearer_token' key
export function getTokenFromStorage(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('bearer_token');
}

export function setTokenStorage(token: string): void {
  if (typeof window === 'undefined') return;
  // Store in BOTH localStorage AND cookie
  localStorage.setItem('bearer_token', token);
  document.cookie = `bearer_token=${token};path=/;SameSite=Lax;max-age=${60*60*24*7}`;
}

export function removeTokenStorage(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('bearer_token');
  document.cookie = "bearer_token=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
}
