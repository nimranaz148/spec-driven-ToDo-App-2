'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';

/**
 * ProtectedRoute component - Middleware for protecting routes that require authentication
 *
 * This component checks if the user is authenticated by verifying the presence of a JWT token
 * in the Zustand auth store. If not authenticated, it redirects to the login page.
 *
 * @example
 * ```tsx
 * export default function DashboardPage() {
 *   return (
 *     <ProtectedRoute>
 *       <div>Protected content here</div>
 *     </ProtectedRoute>
 *   );
 * }
 * ```
 */
interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const { isAuthenticated, token } = useAuthStore();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Check authentication status
    const checkAuth = () => {
      // If not authenticated or no token, redirect to login
      if (!isAuthenticated || !token) {
        router.push('/login');
        return;
      }

      // Authentication check complete
      setIsChecking(false);
    };

    checkAuth();
  }, [isAuthenticated, token, router]);

  // Show loading state while checking authentication
  if (isChecking) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          <p className="text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // If authenticated, render the protected content
  return <>{children}</>;
}
