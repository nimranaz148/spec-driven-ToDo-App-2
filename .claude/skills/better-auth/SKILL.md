---
name: better-auth
description: Better Auth authentication framework patterns for Next.js. Use when implementing user authentication, JWT tokens, session management, or OAuth integration for the Todo frontend.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# Better Auth Skill

## Quick Reference

Better Auth is an authentication framework for TypeScript/JavaScript apps with built-in JWT support and OAuth providers.

## Basic Setup

```typescript
// lib/auth.ts
import { createAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = createAuth({
  plugins: [
    jwt({
      jwt: {
        secret: process.env.BETTER_AUTH_SECRET!,
        expiry: "7d",
      },
    }),
  ],
  providers: {
    credentials: {
      providerName: "credentials",
      credentials: {
        email: { type: "email", label: "Email" },
        password: { type: "password", label: "Password" },
      },
    },
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
  },
  advanced: {
    cookiePrefix: "todo-app",
  },
})
```

## Provider Configuration

### Email/Password (Credentials)
```typescript
providers: {
  credentials: {
    providerName: "credentials",
    credentials: {
      email: { type: "email", label: "Email", required: true },
      password: { type: "password", label: "Password", required: true },
    },
  },
}
```

### OAuth Providers
```typescript
providers: {
  google: {
    clientId: process.env.GOOGLE_CLIENT_ID!,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  },
  github: {
    clientId: process.env.GITHUB_CLIENT_ID!,
    clientSecret: process.env.GITHUB_CLIENT_SECRET!,
  },
}
```

## Server Session

```typescript
import { getServerSession } from "better-auth/server"

export async function getSession() {
  return await getServerSession()
}

export async function requireAuth() {
  const session = await getServerSession()
  if (!session) {
    throw new Error("Unauthorized")
  }
  return session
}
```

## Client Session

```typescript
import { useSession, signIn, signOut } from "better-auth/react"

function UserMenu() {
  const { data: session, isLoading } = useSession()

  if (isLoading) return null

  if (session) {
    return (
      <div>
        <span>Welcome, {session.user.name}</span>
        <button onClick={() => signOut()}>Sign Out</button>
      </div>
    )
  }

  return <button onClick={() => signIn("google")}>Sign In</button>
}
```

## JWT Plugin

```typescript
import { jwt } from "better-auth/plugins"

const auth = createAuth({
  plugins: [
    jwt({
      jwt: {
        secret: process.env.BETTER_AUTH_SECRET!,
        expiry: "7d",
      },
      // Custom jwt Claims
      signIn: {
        cache: true,
      },
    }),
  ],
})

// Access token in session
const session = await getServerSession()
const token = session.accessToken // JWT token for API calls
```

## Protected Routes

```typescript
import { redirect } from "next/navigation"
import { getServerSession } from "better-auth/server"

export default async function ProtectedPage() {
  const session = await getServerSession()

  if (!session) {
    redirect("/auth/signin?callbackUrl=/protected")
  }

  return <div>Protected content</div>
}
```

## Environment Variables

```bash
# .env.local
BETTER_AUTH_SECRET=your-32-character-secret-key
BETTER_AUTH_URL=http://localhost:3000

# OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## For Detailed Reference

See [REFERENCE.md](REFERENCE.md) for:
- Advanced JWT configuration
- OAuth setup walkthrough
- Session management
- Custom providers
- Error handling
