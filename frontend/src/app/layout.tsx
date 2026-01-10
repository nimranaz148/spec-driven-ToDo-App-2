import type { Metadata, Viewport } from 'next';
import Script from 'next/script';
import './globals.css';
import { Toaster } from 'sonner';

export const metadata: Metadata = {
  title: 'TodoAI - AI-Powered Task Management',
  description: 'Experience the future of task management with AI-powered insights, voice commands, and elegant design crafted for excellence.',
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#f8f5f0' },
    { media: '(prefers-color-scheme: dark)', color: '#1a1a1a' },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* ChatKit Web Component - Required for ChatKit to render */}
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="beforeInteractive"
        />
      </head>
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
        <Toaster richColors position="top-right" />
      </body>
    </html>
  );
}
