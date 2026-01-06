'use client';

import { useEffect, useState } from 'react';
import { MessageSquare, Zap } from 'lucide-react';
import { useAuthStore } from '@/stores/auth-store';
import { useChatStore } from '@/stores/chat-store';
import { ChatKitUI, type ChatMessage } from '@/components/chat/chatkit-ui';
import ConversationSidebar from '@/components/chat/conversation-sidebar';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

const suggestedPrompts = [
  'Add a task to buy groceries',
  'Show me my pending tasks',
  'Mark task 1 as complete',
  'What tasks do I have?',
];

export default function ChatPage() {
  const { user } = useAuthStore();
  const [useStreaming, setUseStreaming] = useState(true);
  const {
    messages,
    conversations,
    activeConversationId,
    isLoading,
    isStreaming,
    error,
    isHistoryLoaded,
    pendingConfirmation,
    fetchConversations,
    createConversation,
    deleteConversation,
    renameConversation,
    switchConversation,
    fetchHistory,
    sendMessage,
    sendMessageStreaming,
    confirmAction,
    cancelConfirmation,
  } = useChatStore();

  // Initialize conversations and active conversation on mount
  useEffect(() => {
    if (user) {
      console.log('[Chat Page] User found:', user);
      console.log('[Chat Page] Fetching conversations...');
      fetchConversations().then(() => {
        const state = useChatStore.getState();
        if (state.conversations.length > 0 && !state.activeConversationId) {
          // Set the first conversation as active
          switchConversation(state.conversations[0].id);
        }
      }).catch((error) => {
        console.error('[Chat Page] Failed to fetch conversations:', error);
      });
    } else {
      console.log('[Chat Page] No user found - user needs to login');
    }
  }, [user, fetchConversations, switchConversation]);

  // Fetch history when active conversation changes
  useEffect(() => {
    if (activeConversationId && !isHistoryLoaded) {
      fetchHistory(activeConversationId);
    }
  }, [activeConversationId, isHistoryLoaded, fetchHistory]);

  // Convert store messages to ChatKit format
  const chatMessages: ChatMessage[] = messages.map((msg) => ({
    id: msg.id,
    role: msg.role,
    content: msg.content,
    timestamp: msg.timestamp,
    isOptimistic: msg.isOptimistic,
    isStreaming: msg.isStreaming,
    thinkingSteps: msg.thinkingSteps,
    toolCalls: msg.toolCalls,
    processingTimeMs: msg.processingTimeMs,
  }));

  const handleSendMessage = async (content: string) => {
    try {
      console.log('[Chat] Sending message:', content);
      console.log('[Chat] Active conversation ID:', activeConversationId);
      
      // Create a new conversation if none is active
      if (!activeConversationId) {
        console.log('[Chat] No active conversation, creating new one...');
        const newConversationId = await createConversation();
        console.log('[Chat] Created conversation:', newConversationId);
        // The store will automatically switch to the new conversation
      }

      if (useStreaming) {
        console.log('[Chat] Using streaming...');
        await sendMessageStreaming(content);
      } else {
        console.log('[Chat] Using regular send...');
        await sendMessage(content);
      }
      console.log('[Chat] Message sent successfully');
    } catch (error) {
      console.error('[Chat] Failed to send message:', error);
      toast.error('Failed to send message');
    }
  };

  const handleCreateConversation = async () => {
    try {
      console.log('[Chat] Creating new conversation...');
      const newConversationId = await createConversation();
      console.log('[Chat] New conversation created:', newConversationId);
      toast.success('New conversation created');
    } catch (error) {
      console.error('[Chat] Failed to create conversation:', error);
      toast.error('Failed to create conversation');
    }
  };

  const handleDeleteConversation = async (id: number) => {
    try {
      await deleteConversation(id);
    } catch (error) {
      // Error is handled by the store
    }
  };

  const handleRenameConversation = async (id: number, title: string) => {
    try {
      await renameConversation(id, title);
    } catch (error) {
      // Error is handled by the store
    }
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex">
      {/* Conversation Sidebar */}
      <ConversationSidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={switchConversation}
        onCreateConversation={handleCreateConversation}
        onDeleteConversation={handleDeleteConversation}
        onRenameConversation={handleRenameConversation}
        isLoading={isLoading}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto">
        {/* Header */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <MessageSquare className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold">AI Chat</h1>
                {activeConversationId && (
                  <p className="text-sm text-muted-foreground">
                    {conversations.find(c => c.id === activeConversationId)?.title || 'Untitled Chat'}
                  </p>
                )}
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setUseStreaming(!useStreaming)}
              className={cn(
                'gap-2 transition-colors',
                useStreaming && 'bg-primary/10 border-primary/50 text-primary'
              )}
            >
              <Zap className={cn('h-4 w-4', useStreaming && 'text-primary')} />
              {useStreaming ? 'Streaming' : 'Standard'}
            </Button>
          </div>
          <p className="text-muted-foreground mt-2">
            Manage your tasks using natural language
          </p>
        </div>

        {/* Chat Interface */}
        <div className="flex-1 min-h-0">
          {activeConversationId ? (
            <ChatKitUI
              messages={chatMessages}
              isLoading={isLoading}
              isTyping={(isLoading || isStreaming) && messages.length > 0 && !messages[messages.length - 1]?.isStreaming}
              error={error}
              pendingConfirmation={pendingConfirmation}
              assistantName="Task Assistant"
              onSendMessage={handleSendMessage}
              onConfirm={confirmAction}
              onCancel={cancelConfirmation}
              placeholder="Ask me to manage your tasks..."
              suggestedPrompts={suggestedPrompts}
            />
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 text-muted-foreground/50" />
                {!user ? (
                  <>
                    <h3 className="text-lg font-medium mb-2">Please log in</h3>
                    <p className="text-muted-foreground mb-4">
                      You need to be logged in to use the chat feature
                    </p>
                    <Button onClick={() => window.location.href = '/login'}>
                      Go to Login
                    </Button>
                  </>
                ) : (
                  <>
                    <h3 className="text-lg font-medium mb-2">No conversation selected</h3>
                    <p className="text-muted-foreground mb-4">
                      Create a new conversation to start chatting with your AI assistant
                    </p>
                    <Button onClick={handleCreateConversation}>
                      Start New Chat
                    </Button>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
