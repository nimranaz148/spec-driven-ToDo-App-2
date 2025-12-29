import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

// Better Auth API route handler
// This creates these endpoints automatically:
// - POST /api/auth/sign-up/email
// - POST /api/auth/sign-in/email
// - POST /api/auth/sign-out
// - GET /api/auth/session
// - GET /api/auth/jwks
// - GET /api/auth/token (for JWT generation)
export const { GET, POST } = toNextJsHandler(auth);
