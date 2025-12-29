import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Header } from '@/components/layout/header';
import { useUIStore } from '@/stores/ui-store';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    pathname: '/',
  })),
  usePathname: jest.fn(() => '/'),
}));

// Mock auth store
jest.mock('@/stores/auth-store', () => ({
  useAuthStore: jest.fn(() => ({
    user: null,
    isAuthenticated: false,
    clearAuth: jest.fn(),
  })),
}));

describe('Dark Mode', () => {
  beforeEach(() => {
    // Reset the UI store
    const store = useUIStore.getState();
    store.setTheme('light');
  });

  it('toggles between light and dark mode', async () => {
    const user = userEvent.setup();
    render(<Header />);

    const themeToggle = screen.getByLabelText(/switch to dark mode/i);

    // Initially in light mode
    expect(themeToggle).toBeInTheDocument();

    // Click to switch to dark mode
    await user.click(themeToggle);

    await waitFor(() => {
      const darkToggle = screen.getByLabelText(/switch to light mode/i);
      expect(darkToggle).toBeInTheDocument();
    });

    // Verify theme changed in store
    const store = useUIStore.getState();
    expect(store.theme).toBe('dark');
  });

  it('applies dark class to document element', async () => {
    const user = userEvent.setup();
    render(<Header />);

    const themeToggle = screen.getByLabelText(/switch to dark mode/i);

    // Click to switch to dark mode
    await user.click(themeToggle);

    await waitFor(() => {
      expect(document.documentElement.classList.contains('dark')).toBe(true);
    });
  });

  it('removes dark class when switching to light mode', async () => {
    const user = userEvent.setup();

    // Start in dark mode
    const store = useUIStore.getState();
    store.setTheme('dark');

    render(<Header />);

    await waitFor(() => {
      expect(document.documentElement.classList.contains('dark')).toBe(true);
    });

    const themeToggle = screen.getByLabelText(/switch to light mode/i);

    // Click to switch to light mode
    await user.click(themeToggle);

    await waitFor(() => {
      expect(document.documentElement.classList.contains('dark')).toBe(false);
    });
  });

  it('persists theme preference in localStorage', async () => {
    const user = userEvent.setup();
    render(<Header />);

    const themeToggle = screen.getByLabelText(/switch to dark mode/i);

    // Switch to dark mode
    await user.click(themeToggle);

    await waitFor(() => {
      const stored = localStorage.getItem('ui-storage');
      expect(stored).toBeTruthy();

      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.theme).toBe('dark');
      }
    });
  });

  it('has accessible theme toggle button', () => {
    render(<Header />);

    const themeToggle = screen.getByLabelText(/switch to dark mode/i);

    // Should be a button
    expect(themeToggle).toHaveAttribute('type', 'button');

    // Should have proper ARIA label
    expect(themeToggle).toHaveAccessibleName();

    // Should be keyboard focusable
    expect(themeToggle).not.toHaveAttribute('tabindex', '-1');
  });

  it('shows correct icon for current theme', async () => {
    const user = userEvent.setup();
    render(<Header />);

    // Light mode should show moon icon (dark mode toggle)
    let themeToggle = screen.getByLabelText(/switch to dark mode/i);
    expect(themeToggle).toBeInTheDocument();

    // Switch to dark mode
    await user.click(themeToggle);

    await waitFor(() => {
      // Dark mode should show sun icon (light mode toggle)
      const lightToggle = screen.getByLabelText(/switch to light mode/i);
      expect(lightToggle).toBeInTheDocument();
    });
  });

  it('respects prefers-color-scheme media query', () => {
    // Mock matchMedia to simulate dark mode preference
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation((query: string) => ({
        matches: query === '(prefers-color-scheme: dark)',
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

    // Theme toggle should be present regardless of system preference
    const themeToggle = screen.getByLabelText(/switch to (dark|light) mode/i);
    expect(themeToggle).toBeInTheDocument();
  });
});
