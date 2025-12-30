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
