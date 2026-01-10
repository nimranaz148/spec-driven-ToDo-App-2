'use client';

/**
 * Custom Chat Interface with full conversation history
 * Uses the ChatKitUI component with conversation management
 */

import { useState, useEffect, useCallback } from 'react';
import ChatKitUI, { ChatMessage } from './chatkit-ui';
import { useAuthStore } from '@/stores/auth-store';
import type { ConfirmationRequest } from '@/lib/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface CustomChatInterfaceProps {
  conversationId: number | null;
  onResponseEnd?: () => void;
}

export default function CustomChatInterface({
  conversationId,
  onResponseEnd,
}: CustomChatInterfaceProps) {
  const { user } = useAuthStore();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingConfirmation, setPendingConfirmation] = useState<ConfirmationRequest | null>(null);

  const loadConversationHistory = useCallback(async () => {
    // Only load history if we have a specific conversation
    if (conversationId === null) {
      return;
    }

    try {
      if (!user?.id) {
        console.log('No user ID available');
        return;
      }
      
      setIsLoading(true);
      const token = localStorage.getItem('bearer_token');
      console.log('Loading history for conversation:', conversationId);
      
      // Build URL with conversation_id query parameter if provided
      const url = conversationId 
        ? `${API_URL}/api/${user.id}/chat/history?conversation_id=${conversationId}`
        : `${API_URL}/api/${user.id}/chat/history`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      console.log('History response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('History error response:', errorText);
        throw new Error(`Failed to load: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log('Loaded messages:', data);
      
      const loadedMessages: ChatMessage[] = data.map((msg: { id: number; role: string; content: string; timestamp: string; created_at?: string }) => ({
        id: String(msg.id),
        role: msg.role,
        content: msg.content,
        timestamp: new Date(msg.created_at || msg.timestamp),
      }));

      setMessages(loadedMessages);
    } catch (err) {
      console.error('Error loading conversation:', err);
      setError(err instanceof Error ? err.message : 'Failed to load conversation history');
    } finally {
      setIsLoading(false);
    }
  }, [conversationId, user?.id]);

  // Load conversation history when conversationId changes
  useEffect(() => {
    if (conversationId === null) {
      // New chat - clear messages and show starter screen
      setMessages([]);
      setError(null);
      setIsLoading(false);
    } else {
      // Load existing conversation history
      loadConversationHistory();
    }
  }, [conversationId, loadConversationHistory]);

  const handleSendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    const token = localStorage.getItem('bearer_token');
    if (!token || !user?.id) {
      setError('Please log in to send messages');
      return;
    }

    // Add optimistic user message
    const userMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
      isOptimistic: true,
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/${user.id}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: content,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response stream');
      }

      let assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
        thinkingSteps: [],
        toolCalls: [],
      };

      setMessages(prev => {
        // Remove optimistic message and add both final user message and streaming assistant
        const withoutOptimistic = prev.filter(m => m.id !== userMessage.id);
        return [
          ...withoutOptimistic,
          { ...userMessage, isOptimistic: false, id: `user-${Date.now()}` },
          assistantMessage,
        ];
      });

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;

            try {
              const parsed = JSON.parse(data);
              
              // Handle error responses
              if (parsed.type === 'error') {
                const errorMessage = parsed.message || parsed.error || 'An error occurred';
                
                // Show user-friendly message for rate limits
                if (errorMessage.includes('quota') || errorMessage.includes('rate limit') || errorMessage.includes('429')) {
                  assistantMessage = {
                    ...assistantMessage,
                    content: '⚠️ **API Rate Limit Reached**\n\nThe AI service has reached its quota limit. This typically happens with free tier API keys.\n\n**Solutions:**\n- Wait a few minutes and try again\n- Check your API key quota at [Google AI Studio](https://ai.google.dev/)\n- Consider upgrading your API plan\n\nYour message has been saved and you can retry in a moment.',
                    isStreaming: false,
                  };
                } else {
                  assistantMessage = {
                    ...assistantMessage,
                    content: `⚠️ **Error**: ${errorMessage}`,
                    isStreaming: false,
                  };
                }
                
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastIndex = newMessages.length - 1;
                  if (newMessages[lastIndex]?.id === assistantMessage.id) {
                    newMessages[lastIndex] = assistantMessage;
                  }
                  return newMessages;
                });
                onResponseEnd?.();
                break;
              }
              // Handle thinking steps (agent phases)
              else if (parsed.type === 'thinking' && parsed.step) {
                assistantMessage = {
                  ...assistantMessage,
                  thinkingSteps: [...(assistantMessage.thinkingSteps || []), parsed.step],
                };
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastIndex = newMessages.length - 1;
                  if (newMessages[lastIndex]?.id === assistantMessage.id) {
                    newMessages[lastIndex] = assistantMessage;
                  }
                  return newMessages;
                });
              }
              // Handle tool calls (MCP server actions)
              else if (parsed.type === 'tool_call' && parsed.data) {
                assistantMessage = {
                  ...assistantMessage,
                  toolCalls: [...(assistantMessage.toolCalls || []), parsed.data],
                };
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastIndex = newMessages.length - 1;
                  if (newMessages[lastIndex]?.id === assistantMessage.id) {
                    newMessages[lastIndex] = assistantMessage;
                  }
                  return newMessages;
                });
              }
              // Handle token/content streaming
              else if (parsed.type === 'token' || parsed.type === 'content') {
                const chunk = parsed.content || parsed.delta || '';
                assistantMessage = {
                  ...assistantMessage,
                  content: assistantMessage.content + chunk,
                };
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastIndex = newMessages.length - 1;
                  if (newMessages[lastIndex]?.id === assistantMessage.id) {
                    newMessages[lastIndex] = assistantMessage;
                  }
                  return newMessages;
                });
              }
              // Handle completion
              else if (parsed.type === 'done') {
                assistantMessage = {
                  ...assistantMessage,
                  isStreaming: false,
                  processingTimeMs: parsed.processing_time_ms,
                };
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastIndex = newMessages.length - 1;
                  if (newMessages[lastIndex]?.id === assistantMessage.id) {
                    newMessages[lastIndex] = assistantMessage;
                  }
                  return newMessages;
                });
                onResponseEnd?.();
              }
            } catch (e) {
              console.error('Error parsing SSE:', e);
            }
          }
        }
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
      // Remove optimistic and failed messages
      setMessages(prev => prev.filter(m => m.id !== userMessage.id));
    } finally {
      setIsTyping(false);
    }
  }, [conversationId, onResponseEnd, user?.id]);

  const suggestedPrompts = user && messages.length === 0 ? [
    'Show my tasks',
    'Add a new task',
    'What tasks are due today?',
    'Mark a task as complete',
  ] : undefined;

  return (
    <ChatKitUI
      messages={messages}
      isLoading={isLoading}
      isTyping={isTyping}
      error={error}
      pendingConfirmation={pendingConfirmation}
      userAvatar={user?.image || undefined}
      assistantName="Todo Assistant"
      onSendMessage={handleSendMessage}
      onConfirm={() => setPendingConfirmation(null)}
      onCancel={() => setPendingConfirmation(null)}
      placeholder="Ask me to add, list, complete, or update your tasks..."
      suggestedPrompts={suggestedPrompts}
      className="h-full"
    />
  );
}
