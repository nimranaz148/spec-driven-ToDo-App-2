// TypeScript interfaces for the Todo application
// Note: Backend returns snake_case JSON, so we match that format

export interface User {
  id: string;
  email: string;
  name: string;
  image?: string | null;
  created_at: string | null;
}

export interface Task {
  id: number;
  userId: string;
  title: string;
  description?: string;
  completed: boolean;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  name: string;
  password: string;
}

// Chat-related types (Phase 3)
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  conversation_id?: number | null;
  message: string;
  confirm_token?: string;
}

export interface ToolCall {
  tool: string;
  parameters: Record<string, unknown>;
  result: { success: boolean; id?: number; message?: string; [key: string]: unknown };
  duration_ms?: number;
}

export type ThinkingStepType = 'analyzing' | 'planning' | 'tool_call' | 'processing' | 'clarifying';

export interface ThinkingStep {
  type: ThinkingStepType;
  content: string;
  timestamp?: number;
}

export interface ConfirmationRequest {
  action: string;
  message: string;
  affected_items: Array<{ id: number; title: string }>;
  confirm_token: string;
}

export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls?: ToolCall[];
  thinking_steps?: ThinkingStep[];
  confirmation_required?: ConfirmationRequest;
  processing_time_ms?: number;
}
