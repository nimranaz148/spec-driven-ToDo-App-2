'use client';

/**
 * Chat page - AI chatbot interface using OpenAI ChatKit.
 *
 * Features:
 * - ChatKit component for chat UI
 * - Custom ConversationSidebar for conversation history
 * - Personalized greeting with user name
 * - Quick prompts for common tasks
 * - Responsive design (mobile sidebar toggle)
 */

import { useEffect, useState, startTransition } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useConversationStore } from '@/stores/conversation-store';
import { useAuthStore } from '@/stores/auth-store';
import ConversationSidebar from '@/components/chat/conversation-sidebar';
import CustomChatInterface from '@/components/chat/custom-chat-interface';
import { Button } from '@/components/ui/button';
import { Menu, Loader2 } from 'lucide-react';

/**
 * ChatKit wrapper component that reinitializes when conversation changes.
 * This is needed because useChatKit hook captures config at mount time.
 */
function ChatKitWrapper({
  conversationId,
  userName,
  onResponseEnd,
}: {
  conversationId: number | null;
  userName: string | undefined;
  onResponseEnd: () => void;
}) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Using startTransition to avoid blocking render
    startTransition(() => {
      setMounted(true);
    });
  }, []);

  // ChatKit configuration - reinitializes when this component remounts
  const { control } = useChatKit({
    // API Configuration - point to local proxy that forwards to backend
    api: {
      url: conversationId
        ? `/api/chatkit?conversation_id=${conversationId}`
        : '/api/chatkit',
      domainKey: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || 'local-dev',
      // Custom fetch to inject auth token from localStorage
      fetch: async (input, init) => {
        const token = typeof window !== 'undefined'
          ? localStorage.getItem('bearer_token')
          : null;

        console.log('[ChatKit] Making request to:', input);
        console.log('[ChatKit] Token exists:', !!token);
        console.log('[ChatKit] Conversation ID:', conversationId);

        return fetch(input, {
          ...init,
          headers: {
            ...init?.headers,
            ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
          },
          credentials: 'include',
        });
      },
    },

    // Theme Configuration
    theme: {
      colorScheme: 'light',
      radius: 'round',
      color: {
        accent: {
          primary: '#0f172a',
          level: 1,
        },
        grayscale: {
          hue: 220,
          tint: 6,
          shade: -4,
        },
      },
    },

    // Start Screen - personalized greeting and quick prompts
    startScreen: {
      greeting: userName
        ? `Hello, ${userName}! How can I help you manage your tasks today?`
        : 'Hello! How can I help you manage your tasks today?',
      prompts: [
        { label: 'Show my tasks', prompt: 'Show my tasks' },
        { label: 'Add a grocery task', prompt: 'Add a task to buy groceries' },
        { label: 'Tasks due today', prompt: 'What tasks are due today?' },
        { label: 'Complete a task', prompt: 'Mark my first task as complete' },
      ],
    },

    // Header Configuration - disabled (using dashboard layout header)
    header: {
      enabled: false,
    },

    // Composer Configuration
    composer: {
      placeholder: 'Ask me to add, list, complete, or update your tasks...',
    },

    // History - disabled (using custom ConversationSidebar)
    history: {
      enabled: false,
    },

    // Event Handlers
    onResponseEnd: () => {
      onResponseEnd();
    },

    onError: ({ error }) => {
      console.error('[ChatKit] Error:', error);
    },
  });

  // Debug: log control state
  useEffect(() => {
    console.log('[ChatKitWrapper] Control:', control);
    console.log('[ChatKitWrapper] Mounted:', mounted);
    console.log('[ChatKitWrapper] Conversation ID:', conversationId);
  }, [control, mounted, conversationId]);

  // Show loading while control is initializing
  if (!control) {
    return (
      <div className="flex h-full items-center justify-center flex-col gap-4 bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="text-sm text-muted-foreground">Connecting to chat...</p>
        <p className="text-xs text-muted-foreground/60">
          (If this persists, check browser console for errors)
        </p>
      </div>
    );
  }

  console.log('[ChatKitWrapper] Rendering ChatKit with control:', control);

  return (
    <div style={{ height: '100%', width: '100%', minHeight: '500px', position: 'relative' }}>
      {/* Debug: Show that control exists */}
      <div style={{
        position: 'absolute',
        top: 0,
        right: 0,
        background: 'green',
        color: 'white',
        padding: '2px 8px',
        fontSize: '10px',
        zIndex: 1000
      }}>
        Control: {control ? 'OK' : 'NULL'}
      </div>
      <ChatKit
        control={control}
        style={{ height: '100%', width: '100%' }}
      />
    </div>
  );
}

export default function ChatPage() {
  const [mounted, setMounted] = useState(false);
  const [uiMode, setUiMode] = useState<'selection' | 'chatkit' | 'custom'>('selection');

  const { user } = useAuthStore();
  const {
    conversations,
    currentConversation,
    isLoading,
    isSidebarOpen,
    _hasHydrated,
    fetchConversations,
    refreshConversationsSilently,
    selectConversation,
    createNewConversation,
    deleteConversation,
    renameConversation,
    toggleSidebar,
  } = useConversationStore();

  // Handle hydration
  useEffect(() => {
    // Using startTransition to avoid blocking render
    startTransition(() => {
      setMounted(true);
      // Check if user has a saved preference
      const savedMode = localStorage.getItem('chat_ui_mode') as 'chatkit' | 'custom' | null;
      if (savedMode) {
        setUiMode(savedMode);
      }
    });
  }, []);

  // Initialize conversations on mount
  useEffect(() => {
    if (_hasHydrated) {
      fetchConversations();
    }
  }, [_hasHydrated, fetchConversations]);

  // Debug: Log conversation state
  useEffect(() => {
    console.log('[ChatKit] Current conversation:', currentConversation);
    console.log('[ChatKit] Mounted:', mounted);
  }, [currentConversation, mounted]);

  // Handler functions for sidebar
  const handleSelectConversation = (id: number) => {
    selectConversation(id);
  };

  const handleCreateConversation = async () => {
    await createNewConversation();
  };

  const handleDeleteConversation = async (id: number) => {
    await deleteConversation(id);
  };

  const handleRenameConversation = async (id: number, title: string) => {
    await renameConversation(id, title);
  };

  // Convert conversations to sidebar format
  const sidebarConversations = conversations.map((c) => ({
    id: c.id,
    title: c.title || 'Untitled Chat',
    created_at: c.created_at,
    updated_at: c.updated_at,
    message_count: 0, // ChatKit manages messages
  }));

  // Show loading while hydrating
  if (!mounted) {
    return (
      <div className="flex h-[calc(100vh-8rem)] items-center justify-center flex-col gap-4">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    );
  }

  // UI Mode Selection Screen
  if (uiMode === 'selection') {
    const handleSelectMode = (mode: 'chatkit' | 'custom', remember: boolean) => {
      setUiMode(mode);
      if (remember) {
        localStorage.setItem('chat_ui_mode', mode);
      }
    };

    return (
      <div className="flex h-[calc(100vh-8rem)] items-center justify-center">
        <div className="max-w-2xl w-full mx-auto p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-2">Choose Your Chat Experience</h1>
            <p className="text-muted-foreground">
              Select the interface that works best for you
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* ChatKit UI Option */}
            <div className="border rounded-lg p-6 hover:border-primary transition-colors cursor-pointer group"
                 onClick={() => handleSelectMode('chatkit', false)}>
              <div className="flex items-center gap-3 mb-4">
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <svg className="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold">ChatKit UI</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Modern, streamlined interface powered by OpenAI ChatKit. Perfect for quick interactions.
              </p>
              <ul className="text-sm space-y-2 mb-6">
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Clean, minimal design</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Optimized for AI responses</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-yellow-500">⚠</span>
                  <span>New conversation each time</span>
                </li>
              </ul>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  handleSelectMode('chatkit', true);
                }}
                className="w-full py-2 px-4 bg-secondary hover:bg-secondary/80 rounded-md text-sm transition-colors"
              >
                Use & Remember
              </button>
            </div>

            {/* Custom UI Option */}
            <div className="border rounded-lg p-6 hover:border-primary transition-colors cursor-pointer group"
                 onClick={() => handleSelectMode('custom', false)}>
              <div className="flex items-center gap-3 mb-4">
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <svg className="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold">Custom UI</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Full-featured chat with conversation history. Best for managing multiple conversations.
              </p>
              <ul className="text-sm space-y-2 mb-6">
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Full conversation history</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Persistent chat sessions</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Advanced features</span>
                </li>
              </ul>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  handleSelectMode('custom', true);
                }}
                className="w-full py-2 px-4 bg-secondary hover:bg-secondary/80 rounded-md text-sm transition-colors"
              >
                Use & Remember
              </button>
            </div>
          </div>

          <p className="text-center text-xs text-muted-foreground mt-6">
            You can change this anytime by clearing your browser preferences
          </p>
        </div>
      </div>
    );
  }

  // Render ChatKit UI
  if (uiMode === 'chatkit') {
    return (
      <div className="flex h-[calc(100vh-8rem)] relative -m-4 sm:-m-6 lg:-m-8">
        {/* Mobile header with hamburger menu */}
        <div className="absolute top-0 left-0 right-0 z-30 flex items-center h-14 px-4 border-b bg-background md:hidden">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            aria-label="Toggle conversation sidebar"
            className="mr-2"
          >
            <Menu className="h-5 w-5" />
          </Button>
          <h1 className="font-semibold text-sm">ChatKit UI</h1>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setUiMode('selection');
              localStorage.removeItem('chat_ui_mode');
            }}
            className="ml-auto text-xs"
          >
            Switch
          </Button>
        </div>

        {/* Desktop header - hidden on mobile */}
        <div className="hidden md:flex absolute top-0 right-0 z-30 p-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setUiMode('selection');
              localStorage.removeItem('chat_ui_mode');
            }}
            className="text-xs"
          >
            Switch UI Mode
          </Button>
        </div>

        {/* Conversation sidebar */}
        <ConversationSidebar
          conversations={sidebarConversations}
          activeConversationId={currentConversation?.id ?? null}
          onSelectConversation={handleSelectConversation}
          onCreateConversation={handleCreateConversation}
          onDeleteConversation={handleDeleteConversation}
          onRenameConversation={handleRenameConversation}
          isLoading={isLoading}
        />

        {/* Mobile overlay backdrop */}
        {isSidebarOpen && (
          <div
            className="fixed inset-0 z-30 bg-black/50 md:hidden"
            onClick={toggleSidebar}
            aria-hidden="true"
          />
        )}

        {/* ChatKit interface */}
        <div className="flex-1 overflow-hidden pt-14 md:pt-0 min-h-[400px] bg-background">
          <ChatKitWrapper
            key={`chatkit-wrapper-${currentConversation?.id ?? 'new'}`}
            conversationId={currentConversation?.id ?? null}
            userName={user?.name}
            onResponseEnd={refreshConversationsSilently}
          />
        </div>
      </div>
    );
  }

  // Render Custom UI
  if (uiMode === 'custom') {
    return (
      <div className="flex h-[calc(100vh-8rem)] relative -m-4 sm:-m-6 lg:-m-8">
        {/* Mobile header */}
        <div className="absolute top-0 left-0 right-0 z-30 flex items-center h-14 px-4 border-b bg-background md:hidden">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            aria-label="Toggle conversation sidebar"
            className="mr-2"
          >
            <Menu className="h-5 w-5" />
          </Button>
          <h1 className="font-semibold text-sm">Custom UI</h1>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setUiMode('selection');
              localStorage.removeItem('chat_ui_mode');
            }}
            className="ml-auto text-xs"
          >
            Switch
          </Button>
        </div>

        {/* Desktop header */}
        <div className="hidden md:flex absolute top-0 right-0 z-30 p-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setUiMode('selection');
              localStorage.removeItem('chat_ui_mode');
            }}
            className="text-xs"
          >
            Switch UI Mode
          </Button>
        </div>

        {/* Conversation sidebar */}
        <ConversationSidebar
          conversations={sidebarConversations}
          activeConversationId={currentConversation?.id ?? null}
          onSelectConversation={handleSelectConversation}
          onCreateConversation={handleCreateConversation}
          onDeleteConversation={handleDeleteConversation}
          onRenameConversation={handleRenameConversation}
          isLoading={isLoading}
        />

        {/* Mobile overlay backdrop */}
        {isSidebarOpen && (
          <div
            className="fixed inset-0 z-30 bg-black/50 md:hidden"
            onClick={toggleSidebar}
            aria-hidden="true"
          />
        )}

        {/* Custom Chat Interface */}
        <div className="flex-1 overflow-hidden pt-14 md:pt-0 bg-background">
          <CustomChatInterface
            conversationId={currentConversation?.id ?? null}
            onResponseEnd={refreshConversationsSilently}
          />
        </div>
      </div>
    );
  }

  return null;
}