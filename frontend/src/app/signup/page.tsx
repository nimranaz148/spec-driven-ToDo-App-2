'use client';

import { AuthForm } from '@/components/auth/auth-form';

export default function SignupPage() {
  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4">
      <AuthForm mode="register" />
    </div>
  );
}
