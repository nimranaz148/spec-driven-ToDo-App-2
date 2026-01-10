/**
 * Conversation store for ChatKit integration.
 *
 * This store manages conversation list and selection for the ChatKit-based chat.
 * Message handling is done by ChatKit itself - this store only handles
 * conversation management (list, select, rename, delete).
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { chatApi } from '@/lib/api/chat';
import type { Conversation } from '@/lib/types';

interface ConversationState {
  // Data
  conversations: Conversation[];
  currentConversation: Conversation | null;

  // Loading states
  isLoading: boolean;
  error: string | null;

  // UI state (mobile sidebar)
  isSidebarOpen: boolean;

  // Hydration flag
  _hasHydrated: boolean;
}

interface ConversationActions {
  // Conversation management
  fetchConversations: () => Promise<void>;
  refreshConversationsSilently: () => Promise<void>;
  selectConversation: (id: number) => void;
  createNewConversation: () => Promise<void>;
  deleteConversation: (id: number) => Promise<void>;
  renameConversation: (id: number, title: string) => Promise<void>;

  // State management
  clearError: () => void;
  reset: () => void;
  setHydrated: () => void;

  // UI state
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
}

type ConversationStore = ConversationState & ConversationActions;

const initialState: ConversationState = {
  conversations: [],
  currentConversation: null,
  isLoading: false,
  error: null,
  isSidebarOpen: false,
  _hasHydrated: false,
};

export const useConversationStore = create<ConversationStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      // Fetch all conversations (with loading state - for initial load)
      fetchConversations: async () => {
        set({ isLoading: true, error: null });
        try {
          const response = await chatApi.getConversations();
          set({
            conversations: response.conversations,
            isLoading: false,
          });
        } catch (error) {
          console.error('[ConversationStore] Failed to fetch conversations:', error);
          // Don't set error for network issues - just log and continue
          // The user can still start a new conversation
          set({
            conversations: [],
            isLoading: false,
          });
        }
      },

      // Refresh conversations silently (no loading state - for background updates)
      refreshConversationsSilently: async () => {
        try {
          const response = await chatApi.getConversations();
          set({ conversations: response.conversations });
        } catch (error) {
          console.error('[ConversationStore] Silent refresh failed:', error);
          // Don't set error for silent refresh
        }
      },

      // Select a conversation
      selectConversation: (id: number) => {
        const { conversations } = get();
        const conversation = conversations.find((c) => c.id === id) || null;
        set({
          currentConversation: conversation,
          isSidebarOpen: false, // Close sidebar on mobile
          error: null,
        });
      },

      // Create a new conversation thread
      createNewConversation: async () => {
        try {
          const newConversation = await chatApi.createConversation();
          const { conversations } = get();
          
          set({
            conversations: [newConversation, ...conversations],
            currentConversation: newConversation,
            error: null,
            isSidebarOpen: false,
          });
        } catch (error) {
          console.error('[ConversationStore] Failed to create conversation:', error);
          // If creation fails, just clear current (fallback behavior)
          set({
            currentConversation: null,
            error: null,
            isSidebarOpen: false,
          });
        }
      },

      // Delete a conversation
      deleteConversation: async (id: number) => {
        try {
          await chatApi.deleteConversation(id);
          const { currentConversation, conversations } = get();

          set({
            conversations: conversations.filter((c) => c.id !== id),
            // Clear current if it was deleted
            ...(currentConversation?.id === id
              ? { currentConversation: null }
              : {}),
          });
        } catch (error) {
          console.error('[ConversationStore] Failed to delete conversation:', error);
          set({ error: 'Failed to delete conversation' });
        }
      },

      // Rename a conversation
      renameConversation: async (id: number, title: string) => {
        try {
          const updated = await chatApi.updateConversation(id, { title });
          const { conversations, currentConversation } = get();

          set({
            conversations: conversations.map((c) =>
              c.id === id ? { ...c, title: updated.title } : c
            ),
            ...(currentConversation?.id === id
              ? { currentConversation: { ...currentConversation, title: updated.title } }
              : {}),
          });
        } catch (error) {
          console.error('[ConversationStore] Failed to rename conversation:', error);
          set({ error: 'Failed to rename conversation' });
        }
      },

      // Clear error
      clearError: () => {
        set({ error: null });
      },

      // Reset store
      reset: () => {
        set(initialState);
      },

      // Set hydration complete
      setHydrated: () => {
        set({ _hasHydrated: true });
      },

      // Toggle sidebar (for mobile)
      toggleSidebar: () => {
        set((state) => ({ isSidebarOpen: !state.isSidebarOpen }));
      },

      // Set sidebar open state
      setSidebarOpen: (open: boolean) => {
        set({ isSidebarOpen: open });
      },
    }),
    {
      name: 'conversation-storage',
      storage: createJSONStorage(() => localStorage),
      // Only persist conversation list, not current conversation or loading state
      partialize: (state) => ({
        conversations: state.conversations,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHydrated();
      },
    }
  )
);

// Selector hooks for optimized re-renders
export const useConversations = () =>
  useConversationStore((state) => state.conversations);

export const useCurrentConversation = () =>
  useConversationStore((state) => state.currentConversation);

export const useIsLoading = () =>
  useConversationStore((state) => state.isLoading);

export const useConversationError = () =>
  useConversationStore((state) => state.error);

export const useIsSidebarOpen = () =>
  useConversationStore((state) => state.isSidebarOpen);
