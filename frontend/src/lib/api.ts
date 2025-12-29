import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import type { Task, TaskCreate, TaskUpdate, TaskListResponse, User } from './types';

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
}

export const api = ApiClient.getInstance();
