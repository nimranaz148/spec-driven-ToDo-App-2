# JWT Reference Guide

## Table of Contents
1. [Token Refresh](#token-refresh)
2. [Token Revocation](#token-revocation)
3. [Security Best Practices](#security-best-practices)
4. [Debugging JWT Issues](#debugging-jwt-issues)

---

## Token Refresh

### Refresh Token Flow

```
1. User authenticates
   ─────────────────▶ Server
                     ◀────────────────
                     Returns access + refresh token

2. Access token expires
   ─────────────────▶ Server (with refresh token)
                     ◀────────────────
                     Returns new access token

3. Both tokens expire
   ─────────────────▶ Server
                     ◀────────────────
                     User must re-authenticate
```

### Implementing Refresh Tokens

```typescript
// frontend/lib/auth.ts
import { createAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = createAuth({
  plugins: [
    jwt({
      jwt: {
        secret: process.env.BETTER_AUTH_SECRET!,
        expiry: "15m",      // Access token: 15 minutes
        refreshExpiry: "7d" // Refresh token: 7 days
      },
      signIn: {
        enableRefreshToken: true,
      },
    }),
  ],
})

// Client usage
async function refreshAccessToken() {
  const session = await auth.api.getSession()
  if (session?.refreshToken) {
    const response = await fetch("/api/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refreshToken: session.refreshToken })
    })
    if (response.ok) {
      // Update session with new tokens
    }
  }
}
```

### Backend Refresh Endpoint (Python)

```python
# backend/routes/auth.py
from fastapi import APIRouter, HTTPException, status
import jwt

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/refresh")
async def refresh_token(refresh_request: RefreshRequest):
    try:
        payload = jwt.decode(
            refresh_request.refreshToken,
            REFRESH_SECRET,  # Separate secret for refresh tokens
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")

        # Generate new access token
        new_access_token = jwt.encode(
            {
                "sub": user_id,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(minutes=15)
            },
            BETTER_AUTH_SECRET,
            algorithm="HS256"
        )

        return {"accessToken": new_access_token}
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
```

---

## Token Revocation

### Token Blacklist (Simple)

```python
# backend/auth.py
import redis

# Redis for token blacklist
redis_client = redis.Redis(host="localhost", port=6379, db=0)

async def revoke_token(token: str):
    """Add token to blacklist until expiration."""
    payload = jwt.decode(token, options={"verify_signature": False})
    exp = payload.get("exp", 0)
    ttl = max(1, exp - int(datetime.utcnow().timestamp()))
    redis_client.setex(f"revoked:{token}", ttl, "true")

async def is_revoked(token: str) -> bool:
    return redis_client.exists(f"revoked:{token}") > 0
```

### Using Revocation in Middleware

```python
# backend/auth.py
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials

    # Check if token is revoked
    if await is_revoked(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    # Verify and decode token
    payload = await verify_jwt(token)
    return payload.get("sub")
```

### Sign Out (Revoke on Client)

```typescript
// frontend/lib/auth.ts
import { signOut } from "better-auth/react"

async function handleSignOut() {
  // Revoke token on backend
  await fetch("/api/auth/revoke", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` }
  })

  // Sign out locally
  await signOut()
}
```

---

## Security Best Practices

### 1. Use Strong Secrets

```bash
# Generate a secure secret (at least 32 characters)
openssl rand -base64 32
# Or: python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 2. Set Appropriate Expiration

```python
# Access token: short-lived (15 minutes)
access_token = jwt.encode(
    {"sub": user_id, "exp": datetime.utcnow() + timedelta(minutes=15)},
    secret,
    algorithm="HS256"
)

# Refresh token: longer-lived (7 days)
refresh_token = jwt.encode(
    {"sub": user_id, "type": "refresh", "exp": datetime.utcnow() + timedelta(days=7)},
    refresh_secret,
    algorithm="HS256"
)
```

### 3. Store Tokens Securely

```typescript
// Frontend: Use httpOnly cookies (recommended)
// Better Auth does this automatically

// If using localStorage (less secure):
localStorage.setItem("token", accessToken)

// Never store in:
// - URL query parameters
// - Local storage on shared computers
// - In-memory variables that persist too long
```

### 4. Validate All Claims

```python
from pydantic import BaseModel

class TokenPayload(BaseModel):
    sub: str
    email: str | None = None
    exp: int
    iat: int
    # Add any other expected claims

def validate_payload(payload: dict) -> TokenPayload:
    # Validate required claims
    if "sub" not in payload:
        raise HTTPException(status_code=401, detail="Missing subject claim")

    # Validate expiration exists and is in future
    if "exp" not in payload:
        raise HTTPException(status_code=401, detail="Missing expiration")

    if datetime.utcfromtimestamp(payload["exp"]) < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Token expired")

    return TokenPayload(**payload)
```

### 5. Use HTTPS

```python
# Always use HTTPS in production
# Cookies should have Secure flag
# Set in Better Auth config:
# advanced: { cookiePrefix: "app", secure: true }
```

### 6. Implement Rate Limiting

```python
# Rate limit auth endpoints
from fastapi import Request
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
async def login(credentials: LoginRequest):
    # Only 5 login attempts per minute
    pass
```

---

## Debugging JWT Issues

### Decode JWT (Debugging)

```python
import jwt

# Decode without verification (for debugging)
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
payload = jwt.decode(token, options={"verify_signature": False})
print(payload)
# {'sub': 'user_123', 'exp': 1700600000, ...}

# Check if token is expired (without raising exception)
try:
    jwt.decode(token, SECRET, algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    print("Token is expired")
except jwt.InvalidTokenError as e:
    print(f"Invalid token: {e}")
```

### Common JWT Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `SignatureVerificationFailed` | Wrong secret or algorithm mismatch | Verify secrets match |
| `ExpiredSignatureError` | Token past expiration time | Use refresh token |
| `InvalidAudienceError` | Wrong `aud` claim | Set correct audience |
| `InvalidIssuerError` | Wrong `iss` claim | Set correct issuer |
| `DecodeError` | Malformed token | Check token format |

### Verify Token Manually

```python
import jwt

def debug_verify_token(token: str, secret: str) -> dict:
    """Debug token verification step by step."""
    print(f"Token: {token[:50]}...")

    # Step 1: Split and decode header
    try:
        header_b64 = token.split(".")[0]
        header = jwt.utils.base64url_decode(header_b64)
        print(f"Header: {header}")
    except Exception as e:
        print(f"Header decode error: {e}")

    # Step 2: Decode payload (no verification)
    try:
        payload_b64 = token.split(".")[1]
        payload_json = jwt.utils.base64url_decode(payload_b64)
        import json
        payload = json.loads(payload_json)
        print(f"Payload: {payload}")
    except Exception as e:
        print(f"Payload decode error: {e}")

    # Step 3: Verify signature
    try:
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        print("Signature verified!")
        return decoded
    except jwt.InvalidSignatureError:
        print("Signature verification FAILED")
        print("Possible causes:")
        print("  - Wrong secret")
        print("  - Token was modified")
    except jwt.ExpiredSignatureError:
        print("Token has expired")

    return None
```

### Testing JWT in Development

```python
# Create a test token
def create_test_token(user_id: str = "test_user") -> str:
    return jwt.encode(
        {
            "sub": user_id,
            "email": "test@example.com",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=7)
        },
        BETTER_AUTH_SECRET,
        algorithm="HS256"
    )

# Use in tests
TEST_TOKEN = create_test_token("user_123")

# Test API call
def test_protected_endpoint():
    response = client.get(
        "/api/user_123/tasks",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    assert response.status_code == 200
```

### Environment Variables

```bash
# .env (NEVER commit to git!)
BETTER_AUTH_SECRET=your-super-secret-key-here-at-least-32-chars
REFRESH_SECRET=another-super-secret-key-for-refresh-tokens

# .env.example (committed - shows required vars)
BETTER_AUTH_SECRET=change-me-in-prod
```
