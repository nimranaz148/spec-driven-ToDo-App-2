import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { TaskForm } from '@/components/tasks/task-form';

// Mock the API
jest.mock('@/lib/api', () => ({
  api: {
    createTask: jest.fn(),
  },
}));

// Mock the auth store
jest.mock('@/stores/auth-store', () => ({
  useAuthStore: jest.fn(() => ({
    user: { id: 'user-1', email: 'test@example.com', name: 'Test', createdAt: new Date().toISOString() },
    token: 'test-token',
    isAuthenticated: true,
  })),
}));

// Mock the task store
jest.mock('@/stores/task-store', () => ({
  useTaskStore: jest.fn(() => ({
    addTask: jest.fn(),
    updateTask: jest.fn(),
    removeTask: jest.fn(),
  })),
}));

import { api } from '@/lib/api';

describe('TaskForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render form with title and description fields', () => {
    render(<TaskForm />);

    expect(screen.getByLabelText('Title')).toBeInTheDocument();
    expect(screen.getByLabelText('Description (optional)')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Add Task' })).toBeInTheDocument();
  });

  it('should show validation error for empty title', async () => {
    render(<TaskForm />);

    const submitButton = screen.getByRole('button', { name: 'Add Task' });
    fireEvent.click(submitButton);

    expect(await screen.findByText('Title is required')).toBeInTheDocument();
  });

  it('should call createTask API with correct data', async () => {
    (api.createTask as jest.Mock).mockResolvedValue({
      id: 1,
      userId: 'user-1',
      title: 'Test Task',
      description: 'Test Description',
      completed: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    });

    render(<TaskForm />);

    const titleInput = screen.getByLabelText('Title');
    const descInput = screen.getByLabelText('Description (optional)');
    const submitButton = screen.getByRole('button', { name: 'Add Task' });

    fireEvent.change(titleInput, { target: { value: 'Test Task' } });
    fireEvent.change(descInput, { target: { value: 'Test Description' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(api.createTask).toHaveBeenCalledWith('user-1', {
        title: 'Test Task',
        description: 'Test Description',
      });
    });
  });

  it('should disable button while loading', async () => {
    (api.createTask as jest.Mock).mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(<TaskForm />);

    const titleInput = screen.getByLabelText('Title');
    const submitButton = screen.getByRole('button', { name: 'Add Task' });

    fireEvent.change(titleInput, { target: { value: 'Test Task' } });
    fireEvent.click(submitButton);

    expect(screen.getByRole('button', { name: 'Adding...' })).toBeDisabled();
  });
});
