# Better Auth Reference Guide

## Table of Contents
1. [Advanced JWT Configuration](#advanced-jwt-configuration)
2. [OAuth Setup Walkthrough](#oauth-setup-walkthrough)
3. [Session Management](#session-management)
4. [Custom Providers](#custom-providers)
5. [Error Handling](#error-handling)

---

## Advanced JWT Configuration

### Custom Token Claims

```typescript
import { createAuth } from "better-auth"
import { jwt } from "better-auth/plugins"
import { type inferAsyncReturnType } from "@tanstack/react-query"

export const auth = createAuth({
  plugins: [
    jwt({
      jwt: {
        secret: process.env.BETTER_AUTH_SECRET!,
        expiry: "7d",
      },
      // Custom claims for JWT payload
      async signIn({ user, session }) {
        return {
          sub: user.id,
          email: user.email,
          name: user.name,
          role: user.role, // Custom field
          iat: Math.floor(Date.now() / 1000),
          exp: Math.floor(Date.now() / 1000) + 60 * 60 * 24 * 7, // 7 days
        }
      },
    }),
  ],
})

// Infer session type
type Session = inferAsyncReturnType<typeof auth.api.getSession>
```

### Token Verification on Backend

```python
# backend/auth.py
import jwt
from jwt.exceptions import PyJWTError
from fastapi import HTTPException, status

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

async def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
        return payload
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    payload = await verify_token(credentials.credentials)
    return payload.get("sub")
```

### Refresh Tokens

```typescript
import { createAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = createAuth({
  plugins: [
    jwt({
      jwt: {
        secret: process.env.BETTER_AUTH_SECRET!,
        expiry: "15m", // Access token: 15 minutes
        refreshExpiry: "7d", // Refresh token: 7 days
      },
      signIn: {
        enableRefreshToken: true,
      },
    }),
  ],
})
```

---

## OAuth Setup Walkthrough

### Google OAuth

1. **Create OAuth Credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Navigate to APIs & Services > Credentials
   - Create OAuth 2.0 Client ID
   - Add authorized redirect URIs:
     - `http://localhost:3000/api/auth/callback/google`
     - `https://yourdomain.com/api/auth/callback/google`

2. **Configure Better Auth:**
```typescript
// lib/auth.ts
import { google } from "better-auth/providers"

export const auth = createAuth({
  providers: [
    google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      // Request additional scopes
      authorizationParams: {
        scope: "openid email profile",
        prompt: "consent",
      },
    }),
  ],
})
```

3. **Environment Variables:**
```bash
# .env.local
GOOGLE_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxx
```

### GitHub OAuth

1. **Create OAuth App:**
   - Go to GitHub Settings > Developer settings > OAuth Apps
   - Create new OAuth App
   - Add callback URL: `http://localhost:3000/api/auth/callback/github`

2. **Configure Better Auth:**
```typescript
import { github } from "better-auth/providers"

export const auth = createAuth({
  providers: [
    github({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
  ],
})
```

### Callback Handler

```typescript
// app/api/auth/[...nextauth]/route.ts
import { auth } from "@/lib/auth"

export const { GET, POST } = auth
```

---

## Session Management

### Session Configuration

```typescript
export const auth = createAuth({
  advanced: {
    cookiePrefix: "todo-app",
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24, // 24 hours
    },
  },
  session: {
    cookie: {
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      httpOnly: true,
    },
  },
})
```

### Getting Session Data

```typescript
import { getServerSession } from "better-auth/server"
import type { inferAsyncReturnType } from "@tanstack/react-query"

type Session = inferAsyncReturnType<typeof getServerSession>

// In API route
export async function GET(req: Request) {
  const session = await getServerSession()
  return Response.json(session)
}

// In Server Component
export default async function Page() {
  const session = await getServerSession()
  if (!session) {
    return <div>Not signed in</div>
  }
  return <div>Signed in as {session.user.name}</div>
}
```

### Session Callbacks

```typescript
export const auth = createAuth({
  callbacks: {
    async signIn({ user, session }) {
      // Run after successful sign in
      console.log(`${user.email} signed in`)
      return true
    },
    async session({ session, user }) {
      // Modify session before returning
      return {
        ...session,
        user: {
          ...session.user,
          role: user.role, // Add custom field
        }
      }
    },
  },
})
```

### Revoking Sessions

```typescript
import { useSession, signOut } from "better-auth/react"

function SessionManager() {
  const { data: sessions } = useSession()

  return (
    <div>
      <h2>Active Sessions</h2>
      {sessions?.sessions.map((session) => (
        <div key={session.id}>
          <span>{session.device}</span>
          <button
            onClick={() => signOut({ sessionId: session.id })}
          >
            Revoke
          </button>
        </div>
      ))}
    </div>
  )
}
```

---

## Custom Providers

### Credentials Provider (Email/Password)

```typescript
import { credentials } from "better-auth/providers"

export const auth = createAuth({
  providers: [
    credentials({
      providerName: "credentials",
      credentials: {
        email: { type: "email", label: "Email", required: true },
        password: { type: "password", label: "Password", required: true },
      },
      async authorize(credentials) {
        // Validate credentials
        const user = await db.user.findUnique({
          where: { email: credentials.email }
        })

        if (!user) {
          throw new Error("Invalid email or password")
        }

        const valid = await verifyPassword(
          credentials.password,
          user.passwordHash
        )

        if (!valid) {
          throw new Error("Invalid email or password")
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name,
        }
      },
    }),
  ],
})
```

### Custom OAuth Provider

```typescript
import type { OAuthProvider } from "better-auth/providers"

const customProvider: OAuthProvider = (ctx) => {
  return {
    id: "custom",
    name: "Custom OAuth",
    type: "oauth",
    clientId: process.env.CUSTOM_CLIENT_ID!,
    clientSecret: process.env.CUSTOM_CLIENT_SECRET!,
    authorizationParams: {
      url: "https://custom.auth.com/oauth/authorize",
      client_id: process.env.CUSTOM_CLIENT_ID!,
      redirect_uri: `${process.env.BETTER_AUTH_URL}/api/auth/callback/custom`,
      response_type: "code",
      scope: "openid profile email",
    },
    tokenParams: {
      url: "https://custom.auth.com/oauth/token",
      grant_type: "authorization_code",
    },
    userInfo: {
      url: "https://custom.auth.com/userinfo",
      params: {
        access_token: "{accessToken}",
      },
    },
    profile(profile) {
      return {
        id: profile.sub,
        name: profile.name,
        email: profile.email,
        image: profile.picture,
      }
    },
  }
}

export const auth = createAuth({
  providers: [customProvider],
})
```

---

## Error Handling

### Client-Side Errors

```typescript
import { signIn, signOut } from "better-auth/react"

async function handleSignIn(email: string, password: string) {
  try {
    const { error } = await signIn("credentials", {
      email,
      password,
    })

    if (error) {
      // Handle specific errors
      switch (error.status) {
        case 401:
          console.error("Invalid credentials")
          break
        case 429:
          console.error("Too many attempts")
          break
        default:
          console.error("Sign in failed")
      }
      return
    }

    // Success - redirect or update UI
    window.location.href = "/"
  } catch (err) {
    console.error("Unexpected error:", err)
  }
}
```

### Server-Side Errors

```typescript
import { auth } from "@/lib/auth"
import { headers } from "next/headers"

export async function protectedAction() {
  try {
    const session = await auth.api.getSession({
      headers: await headers(),
    })

    if (!session) {
      return { error: "Unauthorized", status: 401 }
    }

    // Do something with session
    return { success: true }
  } catch (error) {
    console.error("Auth error:", error)
    return { error: "Authentication failed", status: 500 }
  }
}
```

### Error Response Types

```typescript
interface AuthError {
  status: number
  message: string
  code?: string
}

// Common errors
const errors = {
  SESSION_EXPIRED: { status: 401, message: "Session expired" },
  INVALID_TOKEN: { status: 401, message: "Invalid token" },
  USER_NOT_FOUND: { status: 404, message: "User not found" },
  INVALID_CREDENTIALS: { status: 401, message: "Invalid credentials" },
  RATE_LIMITED: { status: 429, message: "Too many requests" },
}
```

### Rate Limiting

```typescript
import { createAuth } from "better-auth"

export const auth = createAuth({
  plugins: [
    {
      id: "rate-limit",
      init(client) {
        // Implement rate limiting logic
        // This is a simplified example
        const requests = new Map<string, number[]>()

        client.api.router.onBefore(async (ctx) => {
          const ip = ctx.headers.get("x-forwarded-for") || "unknown"
          const now = Date.now()
          const window = 60 * 1000 // 1 minute
          const limit = 10 // requests per window

          const timestamps = requests.get(ip) || []
          const recent = timestamps.filter(t => now - t < window)
          requests.set(ip, [...recent, now])

          if (recent.length >= limit) {
            throw new Error("Rate limited")
          }
        })
      },
    },
  ],
})
```

### Security Best Practices

```typescript
export const auth = createAuth({
  advanced: {
    // Enable CSRF protection
    csrf: true,

    // Password requirements
    password: {
      minLength: 8,
      requireUppercase: true,
      requireLowercase: true,
      requireNumber: true,
      requireSpecialChar: true,
    },

    // Account security
    account: {
      enableVerification: true, // Require email verification
      deleteAccount: {
        enabled: true,
        requirePassword: true,
      },
    },
  },

  // Secure cookies in production
  session: {
    cookie: {
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      httpOnly: true,
    },
  },
})
```
