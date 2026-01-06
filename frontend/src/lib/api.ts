import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import type {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskListResponse,
  User,
  ChatRequest,
  ChatResponse,
  ChatMessage
} from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;
  private static instance: ApiClient;

  private constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add Bearer token from localStorage
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = typeof window !== 'undefined' ? localStorage.getItem('bearer_token') : null;
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid - clear storage and redirect to login
          if (typeof window !== 'undefined') {
            localStorage.removeItem('bearer_token');
            document.cookie = "bearer_token=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  public static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient();
    }
    return ApiClient.instance;
  }

  // Note: Auth methods (login, register, logout) are handled by Better Auth
  // through the auth-client.ts module. This API client only handles
  // backend API calls for tasks and other resources.

  // Get current user from Better Auth session
  async getCurrentUser(): Promise<User> {
    const response = await fetch('/api/auth/session', {
      credentials: 'include',
    });
    if (!response.ok) {
      throw new Error('Failed to get user session');
    }
    const session = await response.json();
    return session.user;
  }

  // Task methods
  async getTasks(userId: string, completed?: boolean, skip = 0, limit = 100): Promise<TaskListResponse> {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() });
    if (completed !== undefined) {
      params.append('completed', completed.toString());
    }
    const response = await this.client.get<TaskListResponse>(`/api/${userId}/tasks?${params}`);
    return response.data;
  }

  async getTask(userId: string, taskId: number): Promise<Task> {
    const response = await this.client.get<Task>(`/api/${userId}/tasks/${taskId}`);
    return response.data;
  }

  async createTask(userId: string, data: TaskCreate): Promise<Task> {
    const response = await this.client.post<Task>(`/api/${userId}/tasks`, data);
    return response.data;
  }

  async updateTask(userId: string, taskId: number, data: TaskUpdate): Promise<Task> {
    const response = await this.client.put<Task>(`/api/${userId}/tasks/${taskId}`, data);
    return response.data;
  }

  async deleteTask(userId: string, taskId: number): Promise<void> {
    await this.client.delete(`/api/${userId}/tasks/${taskId}`);
  }

  async toggleComplete(userId: string, taskId: number): Promise<Task> {
    const response = await this.client.patch<Task>(`/api/${userId}/tasks/${taskId}/complete`);
    return response.data;
  }

  // Conversation management methods
  async getConversations(userId: string): Promise<Array<{
    id: number;
    title: string;
    created_at: string;
    updated_at: string;
    message_count: number;
  }>> {
    const response = await this.client.get(`/api/${userId}/conversations`);
    return response.data;
  }

  async createConversation(userId: string, title?: string): Promise<{
    id: number;
    title: string;
    created_at: string;
    updated_at: string;
    message_count: number;
  }> {
    const response = await this.client.post(`/api/${userId}/conversations`, {
      title,
    });
    return response.data;
  }

  async deleteConversation(userId: string, conversationId: number): Promise<void> {
    await this.client.delete(`/api/${userId}/conversations/${conversationId}`);
  }

  async updateConversation(userId: string, conversationId: number, title: string): Promise<{
    id: number;
    title: string;
    created_at: string;
    updated_at: string;
  }> {
    const response = await this.client.put(`/api/${userId}/conversations/${conversationId}`, {
      title,
    });
    return response.data;
  }

  // Chat methods (Phase 3)
  async sendChatMessage(
    userId: string,
    message: string,
    conversationId?: number | null,
    confirmToken?: string
  ): Promise<ChatResponse> {
    const request: ChatRequest = {
      conversation_id: conversationId,
      message,
      confirm_token: confirmToken,
    };
    const response = await this.client.post<ChatResponse>(`/api/${userId}/chat`, request);
    return response.data;
  }

  async getChatHistory(userId: string): Promise<Array<ChatMessage & { id: number; created_at: string }>> {
    const response = await this.client.get<Array<ChatMessage & { id: number; created_at: string }>>(`/api/${userId}/chat/history`);
    return response.data;
  }

  // Streaming chat methods
  async *streamChatMessage(
    userId: string,
    message: string,
    conversationId?: number | null,
    confirmToken?: string
  ): AsyncGenerator<StreamEvent, void, unknown> {
    const token = typeof window !== 'undefined' ? localStorage.getItem('bearer_token') : null;

    const response = await fetch(`${API_URL}/api/${userId}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        message,
        confirm_token: confirmToken,
      }),
    });

    if (!response.ok) {
      if (response.status === 401) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('bearer_token');
          document.cookie = "bearer_token=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
          window.location.href = '/login';
        }
      }
      throw new Error(`Stream request failed with status ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          console.log('[SSE] Stream done');
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              console.log('[SSE] Event:', data.type, data);
              yield data as StreamEvent;
            } catch {
              console.log('[SSE] Parse error for line:', line);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }
}

// Stream event types
export interface StreamEventStart {
  type: 'start';
  conversation_id: number;
}

export interface StreamEventThinking {
  type: 'thinking';
  step: {
    type: string;
    content: string;
    timestamp?: number;
  };
}

export interface StreamEventToolCall {
  type: 'tool_call';
  data: {
    tool: string;
    parameters: Record<string, unknown>;
    result: { success: boolean; id?: number };
    duration_ms?: number;
  };
}

export interface StreamEventToken {
  type: 'token';
  content: string;
}

export interface StreamEventDone {
  type: 'done';
  processing_time_ms?: number;
  confirmation_required?: {
    action: string;
    message: string;
    affected_items: Array<{ id: number; title: string }>;
    confirm_token: string;
  } | null;
}

export interface StreamEventError {
  type: 'error';
  message: string;
}

export type StreamEvent =
  | StreamEventStart
  | StreamEventThinking
  | StreamEventToolCall
  | StreamEventToken
  | StreamEventDone
  | StreamEventError;

export const api = ApiClient.getInstance();
