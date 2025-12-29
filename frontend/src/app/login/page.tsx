'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { AuthForm } from '@/components/auth/auth-form';

function LoginContent() {
  const searchParams = useSearchParams();
  const justRegistered = searchParams.get('registered') === 'true';

  return (
    <div className="w-full max-w-md space-y-4">
      {justRegistered && (
        <div className="p-3 rounded-md bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-sm text-center">
          Account created successfully! Please sign in to continue.
        </div>
      )}
      <AuthForm mode="login" />
    </div>
  );
}

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4">
      <Suspense fallback={<div className="w-full max-w-md"><AuthForm mode="login" /></div>}>
        <LoginContent />
      </Suspense>
    </div>
  );
}
