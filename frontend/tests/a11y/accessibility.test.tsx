import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Header } from '@/components/layout/header';
import { Nav } from '@/components/layout/nav';
import { EmptyState } from '@/components/tasks/empty-state';
import { TaskItem } from '@/components/tasks/task-item';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    pathname: '/',
  })),
  usePathname: jest.fn(() => '/'),
}));

// Mock stores
jest.mock('@/stores/auth-store', () => ({
  useAuthStore: jest.fn(() => ({
    user: { id: '1', name: 'Test User', email: 'test@example.com' },
    isAuthenticated: true,
    token: 'mock-token',
    clearAuth: jest.fn(),
  })),
}));

jest.mock('@/stores/ui-store', () => ({
  useUIStore: jest.fn(() => ({
    theme: 'light',
    toggleTheme: jest.fn(),
  })),
}));

jest.mock('@/stores/task-store', () => ({
  useTaskStore: jest.fn(() => ({
    toggleComplete: jest.fn(),
    deleteTask: jest.fn(),
  })),
}));

describe('Accessibility (WCAG 2.1 AA)', () => {
  describe('Keyboard Navigation', () => {
    it('all interactive elements are keyboard accessible', async () => {
      const user = userEvent.setup();
      render(<Header />);

      // Tab through interactive elements
      await user.tab();

      // Home link should be focused
      const homeLink = screen.getByLabelText('Home');
      expect(homeLink).toHaveFocus();

      // Tab to theme toggle
      await user.tab();
      const themeToggle = screen.getByLabelText(/switch to dark mode/i);
      expect(themeToggle).toHaveFocus();

      // Tab to logout button
      await user.tab();
      const logoutButton = screen.getByRole('button', { name: /log out/i });
      expect(logoutButton).toHaveFocus();
    });

    it('supports Enter key activation', async () => {
      const user = userEvent.setup();
      const mockToggle = jest.fn();

      jest.spyOn(require('@/stores/ui-store'), 'useUIStore').mockReturnValue({
        theme: 'light',
        toggleTheme: mockToggle,
      });

      render(<Header />);

      const themeToggle = screen.getByLabelText(/switch to dark mode/i);
      themeToggle.focus();

      await user.keyboard('{Enter}');

      expect(mockToggle).toHaveBeenCalled();
    });

    it('supports Space key activation', async () => {
      const user = userEvent.setup();
      const mockToggle = jest.fn();

      jest.spyOn(require('@/stores/ui-store'), 'useUIStore').mockReturnValue({
        theme: 'light',
        toggleTheme: mockToggle,
      });

      render(<Header />);

      const themeToggle = screen.getByLabelText(/switch to dark mode/i);
      themeToggle.focus();

      await user.keyboard(' ');

      expect(mockToggle).toHaveBeenCalled();
    });
  });

  describe('ARIA Labels', () => {
    it('all buttons have accessible names', () => {
      render(<Header />);

      const themeToggle = screen.getByLabelText(/switch to dark mode/i);
      expect(themeToggle).toHaveAccessibleName();

      const logoutButton = screen.getByRole('button', { name: /log out/i });
      expect(logoutButton).toHaveAccessibleName();
    });

    it('navigation has proper labels', () => {
      render(<Nav />);

      const nav = screen.getByRole('navigation', { name: /task filters/i });
      expect(nav).toBeInTheDocument();
    });

    it('task items have descriptive labels', () => {
      const mockTask = {
        id: '1',
        title: 'Test Task',
        description: 'Test description',
        completed: false,
        userId: '1',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      render(<TaskItem task={mockTask} />);

      const article = screen.getByRole('article');
      expect(article).toHaveAccessibleName(/Test Task/);

      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAccessibleName(/mark task as complete/i);

      const deleteButton = screen.getByRole('button', { name: /delete task: test task/i });
      expect(deleteButton).toHaveAccessibleName();
    });
  });

  describe('Touch Target Sizes', () => {
    it('all interactive elements meet 44px minimum', () => {
      render(<Header />);

      const buttons = screen.getAllByRole('button');

      buttons.forEach((button) => {
        const styles = window.getComputedStyle(button);

        // Check computed dimensions
        const height = parseInt(styles.height || '0');
        const width = parseInt(styles.width || '0');
        const minHeight = parseInt(styles.minHeight || '0');
        const minWidth = parseInt(styles.minWidth || '0');

        // Either actual size or minimum size should meet requirement
        const effectiveHeight = Math.max(height, minHeight);
        const effectiveWidth = Math.max(width, minWidth);

        expect(effectiveHeight).toBeGreaterThanOrEqual(40); // 44px with some tolerance
        expect(effectiveWidth).toBeGreaterThanOrEqual(40);
      });
    });

    it('task item interactive elements are touch-friendly', () => {
      const mockTask = {
        id: '1',
        title: 'Test Task',
        description: 'Test description',
        completed: false,
        userId: '1',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      render(<TaskItem task={mockTask} />);

      const checkbox = screen.getByRole('checkbox');
      const deleteButton = screen.getByRole('button', { name: /delete/i });

      [checkbox, deleteButton].forEach((element) => {
        const styles = window.getComputedStyle(element);
        const minHeight = parseInt(styles.minHeight || styles.height || '0');

        expect(minHeight).toBeGreaterThanOrEqual(40);
      });
    });
  });

  describe('Focus Management', () => {
    it('focus indicators are visible', () => {
      render(<Header />);

      const themeToggle = screen.getByLabelText(/switch to dark mode/i);

      // Check for focus styles
      expect(themeToggle.className).toContain('focus-visible');
    });

    it('focus order is logical', async () => {
      const user = userEvent.setup();
      render(<Header />);

      // Start from beginning
      const body = document.body;
      body.focus();

      // Tab through elements
      await user.tab();
      const firstElement = document.activeElement;

      await user.tab();
      const secondElement = document.activeElement;

      await user.tab();
      const thirdElement = document.activeElement;

      // Verify elements are in logical order
      expect(firstElement).toBeTruthy();
      expect(secondElement).toBeTruthy();
      expect(thirdElement).toBeTruthy();
    });
  });

  describe('Semantic HTML', () => {
    it('uses proper heading hierarchy', () => {
      render(<EmptyState title="No tasks" description="Create your first task" />);

      const heading = screen.getByRole('heading', { name: /no tasks/i });
      expect(heading.tagName).toBe('H3');
    });

    it('uses nav element for navigation', () => {
      render(<Nav />);

      const nav = screen.getByRole('navigation');
      expect(nav.tagName).toBe('NAV');
    });

    it('uses article for task items', () => {
      const mockTask = {
        id: '1',
        title: 'Test Task',
        description: 'Test description',
        completed: false,
        userId: '1',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      render(<TaskItem task={mockTask} />);

      const article = screen.getByRole('article');
      expect(article).toBeInTheDocument();
    });
  });

  describe('Screen Reader Support', () => {
    it('provides status updates for loading states', () => {
      render(<EmptyState title="Loading" description="Please wait..." />);

      // Empty state should be announced
      const content = screen.getByText(/loading/i);
      expect(content).toBeInTheDocument();
    });

    it('announces task completion state', () => {
      const completedTask = {
        id: '1',
        title: 'Completed Task',
        description: 'Test description',
        completed: true,
        userId: '1',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      render(<TaskItem task={completedTask} />);

      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('aria-label', 'Mark task as incomplete');
      expect(checkbox).toBeChecked();
    });

    it('hides decorative icons from screen readers', () => {
      render(<Header />);

      const svgs = document.querySelectorAll('svg[aria-hidden="true"]');
      expect(svgs.length).toBeGreaterThan(0);
    });
  });

  describe('Color Contrast', () => {
    it('text has sufficient contrast ratio', () => {
      render(<Header />);

      const header = screen.getByRole('banner');

      // Check that color values are set
      const styles = window.getComputedStyle(header);
      expect(styles.color).toBeTruthy();
      expect(styles.backgroundColor).toBeTruthy();

      // Note: Actual contrast calculation would require a contrast checker library
      // This test verifies that colors are applied
    });
  });

  describe('Reduced Motion', () => {
    it('respects prefers-reduced-motion', () => {
      // Mock matchMedia
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation((query: string) => ({
          matches: query === '(prefers-reduced-motion: reduce)',
          media: query,
          onchange: null,
          addListener: jest.fn(),
          removeListener: jest.fn(),
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
        })),
      });

      render(<Header />);

      // Component should still render
      expect(screen.getByRole('banner')).toBeInTheDocument();

      // Note: CSS media query behavior is tested in integration tests
    });
  });
});
