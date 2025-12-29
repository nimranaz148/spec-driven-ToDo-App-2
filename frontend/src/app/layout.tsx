import type { Metadata, Viewport } from 'next';
import '@/styles/globals.css';
import { Header } from '@/components/layout/header';
import { PageTransition } from '@/components/layout/page-transition';
import { Toaster } from 'sonner';

export const metadata: Metadata = {
  title: 'Todo App - Manage your tasks',
  description: 'A simple and effective way to manage your daily tasks',
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: '#0a0a0a' },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        <Header />
        <PageTransition>
          <main className="container py-4 sm:py-6 px-4 sm:px-6">
            {children}
          </main>
        </PageTransition>
        <Toaster richColors position="top-right" />
      </body>
    </html>
  );
}
