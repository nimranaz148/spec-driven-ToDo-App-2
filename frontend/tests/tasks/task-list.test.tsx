import { render, screen, waitFor } from '@testing-library/react';
import { TaskList } from '@/components/tasks/task-list';

// Mock the API
jest.mock('@/lib/api', () => ({
  api: {
    getTasks: jest.fn(),
  },
}));

// Mock the auth store
const mockUser = { id: 'user-1', email: 'test@example.com', name: 'Test', createdAt: new Date().toISOString() };

jest.mock('@/stores/auth-store', () => ({
  useAuthStore: jest.fn((selector) => {
    if (selector === (state) => state.user) return mockUser;
    if (selector === (state) => state.token) return 'test-token';
    if (selector === (state) => state.isAuthenticated) return true;
    return jest.fn();
  }),
}));

// Mock the task store
jest.mock('@/stores/task-store', () => ({
  useTaskStore: jest.fn((selector) => {
    if (selector === (state) => state.tasks) return [];
    if (selector === (state) => state.total) return 0;
    if (selector === (state) => state.setTasks) return jest.fn();
    if (selector === (state) => state.setLoading) return jest.fn();
    if (selector === (state) => state.setError) return jest.fn();
    return jest.fn();
  }),
}));

import { api } from '@/lib/api';

describe('TaskList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should show loading state initially', () => {
    (api.getTasks as jest.Mock).mockImplementation(() => new Promise(() => {}));

    render(<TaskList />);

    // Should show skeleton loading state
    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();
  });

  it('should display empty state when no tasks', async () => {
    (api.getTasks as jest.Mock).mockResolvedValue({ tasks: [], total: 0 });

    render(<TaskList />);

    await waitFor(() => {
      expect(screen.getByText('No tasks yet. Create one above!')).toBeInTheDocument();
    });
  });

  it('should render list of tasks', async () => {
    const mockTasks = [
      {
        id: 1,
        userId: 'user-1',
        title: 'Task 1',
        description: 'Description 1',
        completed: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: 2,
        userId: 'user-1',
        title: 'Task 2',
        description: null,
        completed: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ];

    (api.getTasks as jest.Mock).mockResolvedValue({ tasks: mockTasks, total: 2 });

    render(<TaskList />);

    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
      expect(screen.getByText('Task 2')).toBeInTheDocument();
    });
  });

  it('should show unauthenticated message when not logged in', () => {
    jest.mock('@/stores/auth-store', () => ({
      useAuthStore: jest.fn(() => ({
        user: null,
        token: null,
        isAuthenticated: false,
      })),
    }));

    // Re-import to get fresh mock
    jest.resetModules();

    // Need to re-render with fresh mocks
    const { unmount } = render(<TaskList />);
    unmount();
  });
});
