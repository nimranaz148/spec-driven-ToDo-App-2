import { create } from 'zustand';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import type { Task, TaskCreate, TaskUpdate } from '@/lib/types';
import { useAuthStore } from './auth-store';

// Helper function to show error notifications using sonner
const showErrorToast = (message: string) => {
  console.error('[Task Store Error]:', message);
  toast.error(message);
};

// Helper function to show success notifications
const showSuccessToast = (message: string) => {
  toast.success(message);
};

// Check if task ID is a temporary optimistic ID (negative number)
const isOptimisticId = (id: number): boolean => id < 0;

interface TaskState {
  tasks: Task[];
  total: number;
  isLoading: boolean;
  error: string | null;

  // Basic Actions (for external use)
  setTasks: (tasks: Task[], total: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearTasks: () => void;

  // Fetch Tasks
  fetchTasks: () => Promise<void>;

  // Optimistic Actions (with API calls)
  createTask: (data: TaskCreate) => Promise<void>;
  updateTask: (taskId: number, data: TaskUpdate) => Promise<void>;
  deleteTask: (taskId: number) => Promise<void>;
  toggleComplete: (taskId: number) => Promise<void>;
}

// Helper to get user ID
const getUserId = (): string | null => {
  return useAuthStore.getState().user?.id || null;
};

export const useTaskStore = create<TaskState>((set, get) => ({
  tasks: [],
  total: 0,
  isLoading: false,
  error: null,

  setTasks: (tasks, total) => {
    set({ tasks, total });
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  setError: (error) => {
    set({ error });
  },

  clearTasks: () => {
    set({ tasks: [], total: 0, error: null });
  },

  // Fetch Tasks from API
  fetchTasks: async () => {
    const userId = getUserId();
    if (!userId) {
      set({ error: 'User not authenticated' });
      return;
    }

    set({ isLoading: true, error: null });

    try {
      const response = await api.getTasks(userId);
      set({
        tasks: response.tasks,
        total: response.total,
        isLoading: false,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch tasks';
      set({
        error: errorMessage,
        isLoading: false,
      });
      showErrorToast(`Failed to load tasks: ${errorMessage}`);
    }
  },

  // Optimistic Create Task
  createTask: async (data: TaskCreate) => {
    const userId = getUserId();
    if (!userId) {
      showErrorToast('User not authenticated');
      return;
    }

    // Create temporary task with optimistic ID (negative to avoid conflicts)
    const optimisticTask: Task = {
      id: -Date.now(), // Temporary negative ID
      userId,
      title: data.title,
      description: data.description,
      completed: false,
      priority: data.priority,
      due_date: data.due_date,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Save previous state for rollback
    const previousTasks = get().tasks;
    const previousTotal = get().total;

    // Optimistically add task to local state
    set((state) => ({
      tasks: [optimisticTask, ...state.tasks],
      total: state.total + 1,
      error: null,
    }));

    try {
      // Make API call
      const realTask = await api.createTask(userId, data);

      // Replace optimistic task with real task from server
      set((state) => ({
        tasks: state.tasks.map((t) =>
          t.id === optimisticTask.id ? realTask : t
        ),
      }));

      showSuccessToast('Task created successfully');
    } catch (error) {
      // Rollback on error
      set({
        tasks: previousTasks,
        total: previousTotal,
        error: 'Failed to create task',
      });

      const errorMessage = error instanceof Error ? error.message : 'Failed to create task';
      showErrorToast(`Failed to create task: ${errorMessage}`);
      throw error;
    }
  },

  // Optimistic Update Task
  updateTask: async (taskId: number, data: TaskUpdate) => {
    const userId = getUserId();
    if (!userId) {
      showErrorToast('User not authenticated');
      return;
    }

    // Prevent actions on tasks still being created (optimistic IDs)
    if (isOptimisticId(taskId)) {
      toast.info('Please wait, task is still being saved...');
      return;
    }

    // Save previous state for rollback
    const previousTasks = get().tasks;

    // Find the task to update
    const taskToUpdate = previousTasks.find((t) => t.id === taskId);
    if (!taskToUpdate) {
      showErrorToast('Task not found');
      return;
    }

    // Optimistically update task in local state
    set((state) => ({
      tasks: state.tasks.map((t) =>
        t.id === taskId
          ? { ...t, ...data, updated_at: new Date().toISOString() }
          : t
      ),
      error: null,
    }));

    try {
      // Make API call
      const updatedTask = await api.updateTask(userId, taskId, data);

      // Update with real data from server
      set((state) => ({
        tasks: state.tasks.map((t) => (t.id === taskId ? updatedTask : t)),
      }));

      showSuccessToast('Task updated successfully');
    } catch (error) {
      // Rollback on error
      set({
        tasks: previousTasks,
        error: 'Failed to update task',
      });

      const errorMessage = error instanceof Error ? error.message : 'Failed to update task';
      showErrorToast(`Failed to update task: ${errorMessage}`);
      throw error;
    }
  },

  // Optimistic Delete Task
  deleteTask: async (taskId: number) => {
    const userId = getUserId();
    if (!userId) {
      showErrorToast('User not authenticated');
      return;
    }

    // Prevent actions on tasks still being created (optimistic IDs)
    if (isOptimisticId(taskId)) {
      toast.info('Please wait, task is still being saved...');
      return;
    }

    // Save previous state for rollback
    const previousTasks = get().tasks;
    const previousTotal = get().total;

    // Find the task to delete
    const taskToDelete = previousTasks.find((t) => t.id === taskId);
    if (!taskToDelete) {
      showErrorToast('Task not found');
      return;
    }

    // Optimistically remove task from local state
    set((state) => ({
      tasks: state.tasks.filter((t) => t.id !== taskId),
      total: state.total - 1,
      error: null,
    }));

    try {
      // Make API call
      await api.deleteTask(userId, taskId);
      showSuccessToast('Task deleted successfully');
    } catch (error) {
      // Rollback on error
      set({
        tasks: previousTasks,
        total: previousTotal,
        error: 'Failed to delete task',
      });

      const errorMessage = error instanceof Error ? error.message : 'Failed to delete task';
      showErrorToast(`Failed to delete task: ${errorMessage}`);
      throw error;
    }
  },

  // Optimistic Toggle Complete
  toggleComplete: async (taskId: number) => {
    const userId = getUserId();
    if (!userId) {
      showErrorToast('User not authenticated');
      return;
    }

    // Prevent actions on tasks still being created (optimistic IDs)
    if (isOptimisticId(taskId)) {
      toast.info('Please wait, task is still being saved...');
      return;
    }

    // Save previous state for rollback
    const previousTasks = get().tasks;

    // Find the task to toggle
    const taskToToggle = previousTasks.find((t) => t.id === taskId);
    if (!taskToToggle) {
      showErrorToast('Task not found');
      return;
    }

    // Optimistically toggle completion in local state
    set((state) => ({
      tasks: state.tasks.map((t) =>
        t.id === taskId
          ? {
              ...t,
              completed: !t.completed,
              updated_at: new Date().toISOString(),
            }
          : t
      ),
      error: null,
    }));

    try {
      // Make API call
      const updatedTask = await api.toggleComplete(userId, taskId);

      // Update with real data from server
      set((state) => ({
        tasks: state.tasks.map((t) => (t.id === taskId ? updatedTask : t)),
      }));

      showSuccessToast(updatedTask.completed ? 'Task completed!' : 'Task marked incomplete');
    } catch (error) {
      // Rollback on error
      set({
        tasks: previousTasks,
        error: 'Failed to toggle task completion',
      });

      const errorMessage = error instanceof Error ? error.message : 'Failed to toggle task completion';
      showErrorToast(`Failed to toggle task: ${errorMessage}`);
      throw error;
    }
  },
}));
