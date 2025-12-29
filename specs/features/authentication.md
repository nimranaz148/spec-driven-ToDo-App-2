# Feature: User Authentication

## User Stories
- As a user, I can sign up with email/password
- As a user, I can sign in with email/password
- As a user, I remain authenticated across sessions
- As a user, my tasks are private to me

## Technology
- Better Auth (TypeScript auth library)
- JWT tokens for stateless authentication
- bcrypt for password hashing

## Better Auth Configuration

### Plugins Required
- Email/password credentials plugin
- JWT plugin for token generation

### Environment Variables
```
BETTER_AUTH_SECRET=<secret-key-at-least-32-chars>
BETTER_AUTH_URL=http://localhost:3000
```

## JWT Token Flow

1. User logs in on Frontend → Better Auth creates session and issues JWT
2. Frontend makes API call → Includes JWT in Authorization: Bearer <token> header
3. Backend receives request → Extracts token, verifies signature using shared secret
4. Backend identifies user → Decodes token to get user ID
5. Backend filters data → Returns only tasks belonging to that user

## API Security Requirements
- All endpoints require valid JWT token
- Requests without token receive 401 Unauthorized
- Each user only sees/modifies their own tasks
- Task ownership is enforced on every operation
