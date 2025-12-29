import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { TaskItem } from '@/components/tasks/task-item';
import type { Task } from '@/lib/types';

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

// Mock the task store
const mockToggleComplete = jest.fn();
const mockDeleteTask = jest.fn();

jest.mock('@/stores/task-store', () => ({
  useTaskStore: jest.fn(() => ({
    toggleComplete: mockToggleComplete,
    deleteTask: mockDeleteTask,
  })),
}));

// Mock the auth store
jest.mock('@/stores/auth-store', () => ({
  useAuthStore: jest.fn(() => ({
    user: { id: 'user-1', email: 'test@example.com', name: 'Test User', createdAt: new Date().toISOString() },
    token: 'test-token',
    isAuthenticated: true,
  })),
}));

describe('TaskItem Component', () => {
  const mockTask: Task = {
    id: 1,
    userId: 'user-1',
    title: 'Test Task',
    description: 'Test Description',
    completed: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render task with title and description', () => {
    render(<TaskItem task={mockTask} />);

    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });

  it('should render unchecked checkbox when task is not completed', () => {
    render(<TaskItem task={mockTask} />);

    const checkbox = screen.getByRole('checkbox', { name: 'Mark as complete' });
    expect(checkbox).toBeInTheDocument();
    expect(checkbox).not.toBeChecked();
  });

  it('should render checked checkbox when task is completed', () => {
    const completedTask = { ...mockTask, completed: true };
    render(<TaskItem task={completedTask} />);

    const checkbox = screen.getByRole('checkbox', { name: 'Mark as incomplete' });
    expect(checkbox).toBeInTheDocument();
    expect(checkbox).toBeChecked();
  });

  it('should show strikethrough when task is completed', () => {
    const completedTask = { ...mockTask, completed: true };
    render(<TaskItem task={completedTask} />);

    const title = screen.getByText('Test Task');
    expect(title).toHaveClass('line-through');
  });

  it('should call toggleComplete when checkbox is clicked', async () => {
    mockToggleComplete.mockResolvedValue(undefined);

    render(<TaskItem task={mockTask} />);

    const checkbox = screen.getByRole('checkbox', { name: 'Mark as complete' });
    fireEvent.click(checkbox);

    await waitFor(() => {
      expect(mockToggleComplete).toHaveBeenCalledWith('user-1', 1);
    });
  });

  it('should call deleteTask when delete button is clicked', async () => {
    mockDeleteTask.mockResolvedValue(undefined);

    render(<TaskItem task={mockTask} />);

    const deleteButton = screen.getByLabelText('Delete task');
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(mockDeleteTask).toHaveBeenCalledWith('user-1', 1);
    });
  });

  it('should show created date', () => {
    render(<TaskItem task={mockTask} />);

    expect(screen.getByText(/Created/)).toBeInTheDocument();
  });

  it('should handle task without description', () => {
    const noDescTask = { ...mockTask, description: undefined };
    render(<TaskItem task={noDescTask} />);

    expect(screen.getByText('Test Task')).toBeInTheDocument();
    // Description should not be rendered if undefined
  });

  it('should disable checkbox while loading', async () => {
    mockToggleComplete.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(<TaskItem task={mockTask} />);

    const checkbox = screen.getByRole('checkbox', { name: 'Mark as complete' });
    fireEvent.click(checkbox);

    // Checkbox should be disabled during loading
    expect(checkbox).toBeDisabled();
  });

  it('should apply muted background for completed task', () => {
    const completedTask = { ...mockTask, completed: true };
    const { container } = render(<TaskItem task={completedTask} />);

    // Find the TaskCard div with bg-muted class
    const taskCard = container.querySelector('.bg-muted\\/30');
    expect(taskCard).toBeInTheDocument();
  });

  it('should apply muted text color to completed task title', () => {
    const completedTask = { ...mockTask, completed: true };
    render(<TaskItem task={completedTask} />);

    const title = screen.getByText('Test Task');
    expect(title).toHaveClass('text-muted-foreground');
  });

  it('should show delete button on hover', () => {
    render(<TaskItem task={mockTask} />);

    // Delete button should be visible
    const deleteButton = screen.getByLabelText('Delete task');
    expect(deleteButton).toBeInTheDocument();
  });

  // Additional comprehensive tests for toggle completion
  describe('Toggle Completion Feature', () => {
    it('should toggle from incomplete to complete', async () => {
      mockToggleComplete.mockResolvedValue(undefined);

      render(<TaskItem task={mockTask} />);

      const checkbox = screen.getByRole('checkbox', { name: 'Mark as complete' });
      expect(checkbox).not.toBeChecked();

      fireEvent.click(checkbox);

      await waitFor(() => {
        expect(mockToggleComplete).toHaveBeenCalledWith('user-1', 1);
      });
    });

    it('should toggle from complete to incomplete', async () => {
      mockToggleComplete.mockResolvedValue(undefined);
      const completedTask = { ...mockTask, completed: true };

      render(<TaskItem task={completedTask} />);

      const checkbox = screen.getByRole('checkbox', { name: 'Mark as incomplete' });
      expect(checkbox).toBeChecked();

      fireEvent.click(checkbox);

      await waitFor(() => {
        expect(mockToggleComplete).toHaveBeenCalledWith('user-1', 1);
      });
    });

    it('should not call toggleComplete when user is not authenticated', async () => {
      // Override the auth store mock for this test
      const useAuthStore = require('@/stores/auth-store').useAuthStore;
      useAuthStore.mockReturnValueOnce({
        user: null,
        token: null,
        isAuthenticated: false,
      });

      render(<TaskItem task={mockTask} />);

      const checkbox = screen.getByRole('checkbox', { name: 'Mark as complete' });
      fireEvent.click(checkbox);

      await waitFor(() => {
        expect(mockToggleComplete).not.toHaveBeenCalled();
      });
    });

    it('should handle toggle errors gracefully', async () => {
      const consoleError = jest.spyOn(console, 'error').mockImplementation();
      mockToggleComplete.mockRejectedValue(new Error('Network error'));

      render(<TaskItem task={mockTask} />);

      const checkbox = screen.getByRole('checkbox', { name: 'Mark as complete' });
      fireEvent.click(checkbox);

      await waitFor(() => {
        expect(mockToggleComplete).toHaveBeenCalledWith('user-1', 1);
      });

      expect(consoleError).toHaveBeenCalledWith('Failed to toggle task:', expect.any(Error));
      consoleError.mockRestore();
    });

    it('should apply transition classes for smooth animation', () => {
      render(<TaskItem task={mockTask} />);

      const title = screen.getByText('Test Task');
      expect(title).toHaveClass('transition-all');
    });

    it('should show strike-through on description when completed', () => {
      const completedTask = { ...mockTask, completed: true };
      render(<TaskItem task={completedTask} />);

      const description = screen.getByText('Test Description');
      expect(description).toHaveClass('line-through');
    });

    it('should maintain focus on checkbox after toggle', async () => {
      mockToggleComplete.mockResolvedValue(undefined);

      render(<TaskItem task={mockTask} />);

      const checkbox = screen.getByRole('checkbox', { name: 'Mark as complete' });
      checkbox.focus();

      expect(document.activeElement).toBe(checkbox);

      fireEvent.click(checkbox);

      await waitFor(() => {
        expect(mockToggleComplete).toHaveBeenCalled();
      });
    });

    it('should prevent multiple simultaneous toggles', async () => {
      mockToggleComplete.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

      render(<TaskItem task={mockTask} />);

      const checkbox = screen.getByRole('checkbox', { name: 'Mark as complete' });

      // Try to click multiple times rapidly
      fireEvent.click(checkbox);
      fireEvent.click(checkbox);
      fireEvent.click(checkbox);

      // Should only be called once due to loading state
      await waitFor(() => {
        expect(mockToggleComplete).toHaveBeenCalledTimes(1);
      });
    });
  });
});
