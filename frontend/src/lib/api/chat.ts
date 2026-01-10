/**
 * Chat API module for ChatKit integration.
 *
 * This module provides conversation management functions:
 * - getConversations: List user's conversations
 * - getConversation: Get a conversation with messages
 * - updateConversation: Rename a conversation
 * - deleteConversation: Delete a conversation
 *
 * Note: Message handling is done by ChatKit through the /api/chatkit endpoint.
 */

import type {
  Conversation,
  ConversationWithMessages,
} from '@/lib/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Get auth token from localStorage.
 */
function getAuthToken(): string | null {
  return typeof window !== 'undefined' ? localStorage.getItem('bearer_token') : null;
}

/**
 * Get headers for API requests.
 */
function getHeaders(): HeadersInit {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

/**
 * Get user ID from auth store.
 */
function getUserId(): string | null {
  // Try to get from localStorage (auth-storage)
  if (typeof window === 'undefined') return null;

  try {
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage) {
      const parsed = JSON.parse(authStorage);
      return parsed?.state?.user?.id || null;
    }
  } catch {
    console.error('[ChatAPI] Failed to parse auth-storage');
  }
  return null;
}

interface ConversationListResponse {
  conversations: Conversation[];
  total: number;
}

/**
 * Get all conversations for the current user.
 */
export async function getConversations(): Promise<ConversationListResponse> {
  const userId = getUserId();
  if (!userId) {
    throw new Error('User not authenticated');
  }

  const response = await fetch(`${API_URL}/api/${userId}/conversations`, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Handle unauthorized
      if (typeof window !== 'undefined') {
        localStorage.removeItem('bearer_token');
        window.location.href = '/login';
      }
    }
    throw new Error(`Failed to get conversations: ${response.status}`);
  }

  const conversations = await response.json();
  return {
    conversations,
    total: conversations.length,
  };
}

/**
 * Get a single conversation with its messages.
 */
export async function getConversation(
  conversationId: number
): Promise<ConversationWithMessages> {
  const userId = getUserId();
  if (!userId) {
    throw new Error('User not authenticated');
  }

  const response = await fetch(
    `${API_URL}/api/${userId}/conversations/${conversationId}`,
    {
      headers: getHeaders(),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to get conversation: ${response.status}`);
  }

  return response.json();
}

/**
 * Update a conversation (rename).
 */
export async function updateConversation(
  conversationId: number,
  update: { title: string }
): Promise<Conversation> {
  const userId = getUserId();
  if (!userId) {
    throw new Error('User not authenticated');
  }

  const response = await fetch(
    `${API_URL}/api/${userId}/conversations/${conversationId}`,
    {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(update),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to update conversation: ${response.status}`);
  }

  return response.json();
}

/**
 * Create a new conversation.
 */
export async function createConversation(title?: string): Promise<Conversation> {
  const userId = getUserId();
  if (!userId) {
    throw new Error('User not authenticated');
  }

  const response = await fetch(`${API_URL}/api/${userId}/conversations`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ title: title || null }),
  });

  if (!response.ok) {
    throw new Error(`Failed to create conversation: ${response.status}`);
  }

  return response.json();
}

/**
 * Delete a conversation.
 */
export async function deleteConversation(conversationId: number): Promise<void> {
  const userId = getUserId();
  if (!userId) {
    throw new Error('User not authenticated');
  }

  const response = await fetch(
    `${API_URL}/api/${userId}/conversations/${conversationId}`,
    {
      method: 'DELETE',
      headers: getHeaders(),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to delete conversation: ${response.status}`);
  }
}

/**
 * Get the most recent conversation for the current user.
 */
export async function getMostRecentConversation(): Promise<Conversation | null> {
  const { conversations } = await getConversations();
  return conversations.length > 0 ? conversations[0] : null;
}

// Export all functions as a chatApi object for convenience
export const chatApi = {
  getConversations,
  getConversation,
  createConversation,
  updateConversation,
  deleteConversation,
  getMostRecentConversation,
};
