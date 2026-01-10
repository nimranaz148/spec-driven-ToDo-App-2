'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import { syncTokenCookie, getJwtToken } from '@/lib/auth-client';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const { isAuthenticated, token } = useAuthStore();
  const [hasHydrated, setHasHydrated] = useState(false);

  useEffect(() => {
    // Wait for zustand to hydrate from localStorage
    // Using setTimeout to defer state update
    const timer = setTimeout(() => {
      setHasHydrated(true);
    }, 0);
    // Sync token cookie for Edge runtime
    syncTokenCookie();
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!hasHydrated) return;

    // Check localStorage directly as backup
    const storedToken = getJwtToken();
    
    // Only redirect if truly not authenticated
    if (!isAuthenticated && !token && !storedToken) {
      console.log('[ProtectedRoute] No auth, redirecting to login');
      router.push('/login');
    }
  }, [hasHydrated, isAuthenticated, token, router]);

  // Show nothing while hydrating
  if (!hasHydrated) {
    return null;
  }

  // Check localStorage as backup
  const storedToken = getJwtToken();
  if (!isAuthenticated && !token && !storedToken) {
    return null;
  }

  return <>{children}</>;
}
