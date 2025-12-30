'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { authClient } from '@/lib/auth-client';
import { generateAndStoreJwtToken } from '@/lib/auth-client';
import { useAuthStore } from '@/stores/auth-store';
import { cn } from '@/lib/utils';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
});

const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  name: z.string().min(1, 'Name is required'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;
type RegisterFormData = z.infer<typeof registerSchema>;

interface AuthFormProps {
  mode: 'login' | 'register';
}

export function AuthForm({ mode }: AuthFormProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setAuth } = useAuthStore();

  const loginForm = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const registerForm = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const handleLogin = async (data: LoginFormData) => {
    setIsLoading(true);
    setError(null);
    try {
      // Step 1: Sign in with Better Auth
      console.log('[Login] Attempting sign in for:', data.email);
      const signInResponse = await authClient.signIn.email({
        email: data.email,
        password: data.password,
      });

      console.log('[Login] Sign in response:', JSON.stringify(signInResponse, null, 2));

      if (signInResponse.error) {
        console.error('[Login] Sign in error:', signInResponse.error);
        throw new Error(signInResponse.error.message || signInResponse.error.code || 'Login failed');
      }

      // Step 2: Generate and store JWT token
      console.log('[Login] Generating JWT token...');
      const token = await generateAndStoreJwtToken();
      console.log('[Login] Token generated:', token ? 'yes' : 'no');

      if (!token) {
        throw new Error('Failed to generate authentication token. Please try again.');
      }

      // Step 3: Update auth store
      const user = signInResponse.data?.user;
      if (user) {
        setAuth(
          {
            id: user.id,
            email: user.email,
            name: user.name || '',
            image: user.image || null,
            created_at: user.createdAt?.toString() || null,
          },
          token
        );
      }

      // Step 4: Navigate to dashboard
      await new Promise(resolve => setTimeout(resolve, 100));
      router.push('/dashboard');
    } catch (err) {
      // Show detailed error for debugging
      console.error('Better Auth login error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (data: RegisterFormData) => {
    setIsLoading(true);
    setError(null);
    try {
      // Step 1: Sign up with Better Auth
      const signUpResponse = await authClient.signUp.email({
        email: data.email,
        password: data.password,
        name: data.name,
      });

      if (signUpResponse.error) {
        // Show detailed error for debugging
        console.error('Better Auth signup error:', signUpResponse.error);
        const errorMessage = signUpResponse.error.message || 'Registration failed';
        // Add more details if available
        const details = signUpResponse.error.status ? ` (${signUpResponse.error.status})` : '';
        throw new Error(errorMessage + details);
      }

      // Step 2: Redirect to login page - user needs to sign in to get JWT
      // Signup creates the user but doesn't establish a session with JWT
      router.push('/login?registered=true');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-3xl font-bold">
          {mode === 'login' ? 'Welcome back' : 'Create an account'}
        </h1>
        <p className="text-muted-foreground">
          {mode === 'login'
            ? 'Enter your credentials to access your tasks'
            : 'Enter your details to create a new account'}
        </p>
      </div>

      {error && (
        <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
          {error}
        </div>
      )}

      {mode === 'login' ? (
        <form onSubmit={loginForm.handleSubmit(handleLogin)} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium">Email</label>
            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              className={cn(
                "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                loginForm.formState.errors.email && "border-destructive"
              )}
              {...loginForm.register('email')}
            />
            {loginForm.formState.errors.email && (
              <p className="text-sm text-destructive">{loginForm.formState.errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium">Password</label>
            <input
              id="password"
              type="password"
              className={cn(
                "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                loginForm.formState.errors.password && "border-destructive"
              )}
              {...loginForm.register('password')}
            />
            {loginForm.formState.errors.password && (
              <p className="text-sm text-destructive">{loginForm.formState.errors.password.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 w-full touch-target"
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      ) : (
        <form onSubmit={registerForm.handleSubmit(handleRegister)} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="name" className="text-sm font-medium">Name</label>
            <input
              id="name"
              type="text"
              placeholder="John Doe"
              className={cn(
                "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                registerForm.formState.errors.name && "border-destructive"
              )}
              {...registerForm.register('name')}
            />
            {registerForm.formState.errors.name && (
              <p className="text-sm text-destructive">{registerForm.formState.errors.name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium">Email</label>
            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              className={cn(
                "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                registerForm.formState.errors.email && "border-destructive"
              )}
              {...registerForm.register('email')}
            />
            {registerForm.formState.errors.email && (
              <p className="text-sm text-destructive">{registerForm.formState.errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium">Password</label>
            <input
              id="password"
              type="password"
              className={cn(
                "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                registerForm.formState.errors.password && "border-destructive"
              )}
              {...registerForm.register('password')}
            />
            {registerForm.formState.errors.password && (
              <p className="text-sm text-destructive">{registerForm.formState.errors.password.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 w-full touch-target"
          >
            {isLoading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
      )}

      <p className="text-center text-sm text-muted-foreground">
        {mode === 'login' ? (
          <>
            Don&apos;t have an account?{' '}
            <Link href="/signup" className="text-primary hover:underline">
              Sign up
            </Link>
          </>
        ) : (
          <>
            Already have an account?{' '}
            <Link href="/login" className="text-primary hover:underline">
              Sign in
            </Link>
          </>
        )}
      </p>
    </div>
  );
}
