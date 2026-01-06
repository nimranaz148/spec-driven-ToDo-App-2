import { create } from 'zustand';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import type { ChatMessage, ChatResponse, ToolCall, ThinkingStep, ConfirmationRequest } from '@/lib/types';
import { useAuthStore } from './auth-store';

// Extended message type with metadata
export interface Message extends ChatMessage {
  id: string;
  timestamp: Date;
  isOptimistic?: boolean;
  isStreaming?: boolean;
  toolCalls?: ToolCall[];
  thinkingSteps?: ThinkingStep[];
  processingTimeMs?: number;
}

// Conversation type
export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface ChatState {
  // Messages for current conversation
  messages: Message[];
  
  // Conversation management
  conversations: Conversation[];
  activeConversationId: number | null;
  
  // UI state
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  isHistoryLoaded: boolean;
  pendingConfirmation: ConfirmationRequest | null;

  // Actions
  setMessages: (messages: Message[]) => void;
  setActiveConversation: (id: number | null) => void;
  setConversations: (conversations: Conversation[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearChat: () => void;
  setPendingConfirmation: (confirmation: ConfirmationRequest | null) => void;

  // Async Actions
  fetchConversations: () => Promise<void>;
  createConversation: (title?: string) => Promise<number>;
  deleteConversation: (id: number) => Promise<void>;
  renameConversation: (id: number, title: string) => Promise<void>;
  switchConversation: (id: number) => Promise<void>;
  fetchHistory: (conversationId?: number) => Promise<void>;
  sendMessage: (content: string, confirmToken?: string) => Promise<void>;
  sendMessageStreaming: (content: string, confirmToken?: string) => Promise<void>;
  confirmAction: () => Promise<void>;
  cancelConfirmation: () => void;
}

// Helper to get user ID
const getUserId = (): string | null => {
  const authState = useAuthStore.getState();
  console.log('[Chat Store] getUserId - authState:', authState);
  
  // Check if JWT token exists in localStorage
  const token = typeof window !== 'undefined' ? localStorage.getItem('bearer_token') : null;
  console.log('[Chat Store] JWT token exists:', !!token);
  
  const userId = authState.user?.id || null;
  console.log('[Chat Store] getUserId - returning:', userId);
  return userId;
};

// Helper to generate unique message ID
const generateMessageId = (): string => `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  conversations: [],
  activeConversationId: null,
  isLoading: false,
  isStreaming: false,
  error: null,
  isHistoryLoaded: false,
  pendingConfirmation: null,

  setMessages: (messages) => {
    set({ messages });
  },

  setActiveConversation: (id) => {
    set({ activeConversationId: id, messages: [], isHistoryLoaded: false });
  },

  setConversations: (conversations) => {
    set({ conversations });
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  setError: (error) => {
    set({ error });
  },

  clearChat: () => {
    set({
      messages: [],
      activeConversationId: null,
      error: null,
      isHistoryLoaded: false,
      isStreaming: false,
      pendingConfirmation: null,
    });
  },

  setPendingConfirmation: (confirmation) => {
    set({ pendingConfirmation: confirmation });
  },

  // Fetch all conversations for the user
  fetchConversations: async () => {
    const userId = getUserId();
    console.log('[Chat Store] fetchConversations - userId:', userId);
    if (!userId) {
      set({ error: 'User not authenticated' });
      return;
    }

    try {
      console.log('[Chat Store] Calling api.getConversations...');
      const conversations = await api.getConversations(userId);
      console.log('[Chat Store] Got conversations:', conversations);
      set({ conversations });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load conversations';
      set({ error: errorMessage });
      console.error('[Chat Store] Failed to fetch conversations:', errorMessage, error);
    }
  },

  // Create a new conversation
  createConversation: async (title?: string) => {
    const userId = getUserId();
    console.log('[Chat Store] createConversation - userId:', userId, 'title:', title);
    if (!userId) {
      toast.error('User not authenticated');
      throw new Error('User not authenticated');
    }

    try {
      console.log('[Chat Store] Calling api.createConversation...');
      const conversation = await api.createConversation(userId, title);
      console.log('[Chat Store] Created conversation:', conversation);
      
      // Add to conversations list
      set((state) => ({
        conversations: [conversation, ...state.conversations],
        activeConversationId: conversation.id,
        messages: [],
        isHistoryLoaded: true, // New conversation has no history
      }));

      console.log('[Chat Store] Conversation added to state, ID:', conversation.id);
      return conversation.id;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create conversation';
      console.error('[Chat Store] Failed to create conversation:', errorMessage, error);
      toast.error(`Failed to create conversation: ${errorMessage}`);
      throw error;
    }
  },

  // Delete a conversation
  deleteConversation: async (id: number) => {
    const userId = getUserId();
    if (!userId) {
      toast.error('User not authenticated');
      return;
    }

    try {
      await api.deleteConversation(userId, id);
      
      set((state) => {
        const newConversations = state.conversations.filter(c => c.id !== id);
        const wasActive = state.activeConversationId === id;
        
        return {
          conversations: newConversations,
          activeConversationId: wasActive ? (newConversations[0]?.id || null) : state.activeConversationId,
          messages: wasActive ? [] : state.messages,
          isHistoryLoaded: wasActive ? false : state.isHistoryLoaded,
        };
      });

      toast.success('Conversation deleted');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete conversation';
      toast.error(`Failed to delete conversation: ${errorMessage}`);
      throw error;
    }
  },

  // Rename a conversation
  renameConversation: async (id: number, title: string) => {
    const userId = getUserId();
    if (!userId) {
      toast.error('User not authenticated');
      return;
    }

    try {
      const updatedConversation = await api.updateConversation(userId, id, title);
      
      set((state) => ({
        conversations: state.conversations.map(c => 
          c.id === id ? { ...c, title: updatedConversation.title } : c
        ),
      }));

      toast.success('Conversation renamed');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to rename conversation';
      toast.error(`Failed to rename conversation: ${errorMessage}`);
      throw error;
    }
  },

  // Switch to a different conversation
  switchConversation: async (id: number) => {
    set({ 
      activeConversationId: id, 
      messages: [], 
      isHistoryLoaded: false,
      error: null,
      pendingConfirmation: null,
    });
    
    // Load history for the new conversation
    await get().fetchHistory(id);
  },

  // Fetch chat history from server
  fetchHistory: async (conversationId?: number) => {
    const userId = getUserId();
    if (!userId) {
      set({ error: 'User not authenticated' });
      return;
    }

    const targetConversationId = conversationId || get().activeConversationId;
    if (!targetConversationId) {
      set({ error: 'No conversation selected' });
      return;
    }

    // Don't refetch if already loaded
    if (get().isHistoryLoaded) {
      return;
    }

    set({ isLoading: true, error: null });

    try {
      const history = await api.getChatHistory(userId);

      const messages: Message[] = history.map((msg) => ({
        id: `server_${msg.id}`,
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
        timestamp: new Date(msg.created_at),
        isOptimistic: false,
      }));

      set({
        messages,
        isLoading: false,
        isHistoryLoaded: true,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load chat history';
      set({
        error: errorMessage,
        isLoading: false,
        isHistoryLoaded: true, // Mark as loaded even on error to prevent retry loops
      });
      // Don't show toast for empty history (404 is expected for new users)
      if (errorMessage !== 'Request failed with status code 404') {
        console.error('[Chat Store]:', errorMessage);
      }
    }
  },

  // Send a message with optimistic update
  sendMessage: async (content: string, confirmToken?: string) => {
    const userId = getUserId();
    if (!userId) {
      toast.error('User not authenticated');
      return;
    }

    if (!content.trim() && !confirmToken) {
      return;
    }

    const conversationId = get().activeConversationId;

    // Create optimistic user message (only if not a confirmation)
    const optimisticUserMessage: Message | null = confirmToken ? null : {
      id: generateMessageId(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
      isOptimistic: true,
    };

    // Save previous state for rollback
    const previousMessages = get().messages;

    // Add user message optimistically (if not confirmation)
    if (optimisticUserMessage) {
      set((state) => ({
        messages: [...state.messages, optimisticUserMessage],
        isLoading: true,
        error: null,
        pendingConfirmation: null,
      }));
    } else {
      set({ isLoading: true, error: null });
    }

    try {
      // Call API
      const response: ChatResponse = await api.sendChatMessage(
        userId,
        content.trim() || 'confirm',
        activeConversationId,
        confirmToken
      );

      // Check if confirmation is required
      if (response.confirmation_required) {
        set({
          pendingConfirmation: response.confirmation_required,
          isLoading: false,
        });

        // Add the confirmation request as an assistant message
        const confirmMessage: Message = {
          id: generateMessageId(),
          role: 'assistant',
          content: response.response,
          timestamp: new Date(),
          isOptimistic: false,
          thinkingSteps: response.thinking_steps,
        };

        set((state) => ({
          messages: [
            ...state.messages.map((m) =>
              m.id === optimisticUserMessage?.id
                ? { ...m, isOptimistic: false }
                : m
            ),
            confirmMessage,
          ],
          activeConversationId: response.conversation_id,
        }));
        return;
      }

      // Create assistant message from response
      const assistantMessage: Message = {
        id: generateMessageId(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        isOptimistic: false,
        toolCalls: response.tool_calls,
        thinkingSteps: response.thinking_steps,
        processingTimeMs: response.processing_time_ms,
      };

      // Update state with real messages
      set((state) => ({
        messages: [
          ...state.messages.map((m) =>
            m.id === optimisticUserMessage?.id
              ? { ...m, isOptimistic: false }
              : m
          ),
          assistantMessage,
        ],
        activeConversationId: response.conversation_id,
        isLoading: false,
        pendingConfirmation: null,
      }));
    } catch (error) {
      // Rollback on error
      set({
        messages: previousMessages,
        isLoading: false,
        error: 'Failed to send message',
      });

      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      toast.error(`Failed to send message: ${errorMessage}`);
      throw error;
    }
  },

  // Send a message with streaming response
  sendMessageStreaming: async (content: string, confirmToken?: string) => {
    const userId = getUserId();
    if (!userId) {
      toast.error('User not authenticated');
      return;
    }

    if (!content.trim() && !confirmToken) {
      return;
    }

    const activeConversationId = get().activeConversationId;

    // Create optimistic user message (only if not a confirmation)
    const optimisticUserMessage: Message | null = confirmToken ? null : {
      id: generateMessageId(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
      isOptimistic: true,
    };

    // Create streaming assistant message placeholder
    const streamingMessageId = generateMessageId();
    const streamingMessage: Message = {
      id: streamingMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
      thinkingSteps: [],
      toolCalls: [],
    };

    // Save previous state for rollback
    const previousMessages = get().messages;

    // Add user message and streaming placeholder
    if (optimisticUserMessage) {
      set((state) => ({
        messages: [...state.messages, optimisticUserMessage, streamingMessage],
        isLoading: true,
        isStreaming: true,
        error: null,
        pendingConfirmation: null,
      }));
    } else {
      set((state) => ({
        messages: [...state.messages, streamingMessage],
        isLoading: true,
        isStreaming: true,
        error: null,
      }));
    }

    try {
      // Stream the response
      const stream = api.streamChatMessage(
        userId,
        content.trim() || 'confirm',
        activeConversationId,
        confirmToken
      );

      let fullContent = '';
      const thinkingSteps: ThinkingStep[] = [];
      const toolCalls: ToolCall[] = [];
      let processingTimeMs: number | undefined;

      for await (const event of stream) {
        switch (event.type) {
          case 'start':
            set({ activeConversationId: event.conversation_id });
            break;

          case 'thinking':
            thinkingSteps.push({
              type: event.step.type as ThinkingStep['type'],
              content: event.step.content,
              timestamp: event.step.timestamp,
            });
            // Update message with new thinking step
            set((state) => ({
              messages: state.messages.map((m) =>
                m.id === streamingMessageId
                  ? { ...m, thinkingSteps: [...thinkingSteps] }
                  : m
              ),
            }));
            break;

          case 'tool_call':
            toolCalls.push({
              tool: event.data.tool,
              parameters: event.data.parameters,
              result: event.data.result,
              duration_ms: event.data.duration_ms,
            });
            // Update message with new tool call
            set((state) => ({
              messages: state.messages.map((m) =>
                m.id === streamingMessageId
                  ? { ...m, toolCalls: [...toolCalls] }
                  : m
              ),
            }));
            break;

          case 'token':
            fullContent += event.content;
            // Update message content
            set((state) => ({
              messages: state.messages.map((m) =>
                m.id === streamingMessageId
                  ? { ...m, content: fullContent }
                  : m
              ),
            }));
            break;

          case 'done':
            processingTimeMs = event.processing_time_ms;
            // Handle confirmation if needed
            if (event.confirmation_required) {
              set({
                pendingConfirmation: {
                  action: event.confirmation_required.action,
                  message: event.confirmation_required.message,
                  affected_items: event.confirmation_required.affected_items,
                  confirm_token: event.confirmation_required.confirm_token,
                },
              });
            }
            break;

          case 'error':
            throw new Error(event.message);
        }
      }

      // Finalize the message
      set((state) => ({
        messages: state.messages.map((m) => {
          if (m.id === streamingMessageId) {
            return {
              ...m,
              content: fullContent,
              isStreaming: false,
              thinkingSteps,
              toolCalls,
              processingTimeMs,
            };
          }
          if (m.id === optimisticUserMessage?.id) {
            return { ...m, isOptimistic: false };
          }
          return m;
        }),
        isLoading: false,
        isStreaming: false,
      }));

    } catch (error) {
      // Rollback on error
      set({
        messages: previousMessages,
        isLoading: false,
        isStreaming: false,
        error: 'Failed to send message',
      });

      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      toast.error(`Failed to send message: ${errorMessage}`);
      throw error;
    }
  },

  // Confirm a pending bulk action
  confirmAction: async () => {
    const confirmation = get().pendingConfirmation;
    if (!confirmation) {
      toast.error('No pending action to confirm');
      return;
    }

    // Add user confirmation message
    const confirmUserMessage: Message = {
      id: generateMessageId(),
      role: 'user',
      content: 'Yes, proceed',
      timestamp: new Date(),
      isOptimistic: false,
    };

    set((state) => ({
      messages: [...state.messages, confirmUserMessage],
    }));

    // Send with confirmation token
    await get().sendMessage('confirm', confirmation.confirm_token);
  },

  // Cancel pending confirmation
  cancelConfirmation: () => {
    const confirmation = get().pendingConfirmation;
    if (confirmation) {
      // Add cancellation message
      const cancelMessage: Message = {
        id: generateMessageId(),
        role: 'assistant',
        content: 'Action cancelled. No changes were made.',
        timestamp: new Date(),
        isOptimistic: false,
      };

      set((state) => ({
        messages: [...state.messages, cancelMessage],
        pendingConfirmation: null,
      }));
    }
  },
}));
