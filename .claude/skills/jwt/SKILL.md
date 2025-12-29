---
name: jwt
description: JWT (JSON Web Token) patterns for authentication. Use when implementing token-based authentication, verifying tokens, or configuring JWT in Better Auth.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# JWT Skill

## Quick Reference

JWT is used for stateless authentication between frontend (Better Auth) and backend (FastAPI).

## JWT Structure

```
Header.Payload.Signature

# Header
{
  "alg": "HS256",
  "typ": "JWT"
}

# Payload (Claims)
{
  "sub": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "iat": 1700000000,
  "exp": 1700600000
}

# Signature
HMAC-SHA256(header.payload, SECRET)
```

## Better Auth JWT Configuration

```typescript
// frontend/lib/auth.ts
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
})
```

## Backend JWT Verification (Python)

```python
# backend/auth.py
import jwt
from jwt.exceptions import PyJWTError

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

async def verify_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        return payload
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

async def get_current_user(credentials) -> str:
    payload = await verify_jwt(credentials.credentials)
    return payload.get("sub")
```

## Token Claims

| Claim | Meaning |
|-------|---------|
| `sub` | Subject (user ID) |
| `email` | User email |
| `name` | User name |
| `iat` | Issued at (timestamp) |
| `exp` | Expiration (timestamp) |
| `iss` | Issuer |
| `aud` | Audience |

## For Detailed Reference

See [REFERENCE.md](REFERENCE.md) for:
- Token refresh
- Token revocation
- Security best practices
- Debugging JWT issues
