import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Header } from '@/components/layout/header';
import { api } from '@/lib/api';

// Mock the API
jest.mock('@/lib/api', () => ({
  api: {
    logout: jest.fn(),
  },
}));

// Mock the auth store
const mockClearAuth = jest.fn();
const mockUser = { id: 'user-1', email: 'test@example.com', name: 'Test User', createdAt: new Date().toISOString() };

jest.mock('@/stores/auth-store', () => ({
  useAuthStore: jest.fn(() => ({
    user: mockUser,
    token: 'test-token',
    isAuthenticated: true,
    clearAuth: mockClearAuth,
  })),
}));

// Mock the router
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

// Mock the UI store
jest.mock('@/stores/ui-store', () => ({
  useUIStore: jest.fn(() => ({
    theme: 'light',
    toggleTheme: jest.fn(),
  })),
}));

describe('Logout Functionality', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (api.logout as jest.Mock).mockResolvedValue(undefined);
  });

  it('should show user name when authenticated', () => {
    render(<Header />);

    expect(screen.getByText('Test User')).toBeInTheDocument();
  });

  it('should show logout button when authenticated', () => {
    render(<Header />);

    expect(screen.getByRole('button', { name: 'Logout' })).toBeInTheDocument();
  });

  it('should call logout API, clearAuth and redirect on successful logout', async () => {
    render(<Header />);

    const logoutButton = screen.getByRole('button', { name: 'Logout' });
    fireEvent.click(logoutButton);

    // Should show loading state
    expect(screen.getByText('Logging out...')).toBeInTheDocument();

    await waitFor(() => {
      expect(api.logout).toHaveBeenCalledTimes(1);
      expect(mockClearAuth).toHaveBeenCalledTimes(1);
      expect(mockPush).toHaveBeenCalledWith('/login');
    });
  });

  it('should still clear auth and redirect even if API call fails', async () => {
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    (api.logout as jest.Mock).mockRejectedValue(new Error('Network error'));

    render(<Header />);

    const logoutButton = screen.getByRole('button', { name: 'Logout' });
    fireEvent.click(logoutButton);

    await waitFor(() => {
      expect(api.logout).toHaveBeenCalledTimes(1);
      expect(consoleErrorSpy).toHaveBeenCalledWith('Logout API call failed:', expect.any(Error));
      expect(mockClearAuth).toHaveBeenCalledTimes(1);
      expect(mockPush).toHaveBeenCalledWith('/login');
    });

    consoleErrorSpy.mockRestore();
  });

  it('should disable logout button while logging out', async () => {
    render(<Header />);

    const logoutButton = screen.getByRole('button', { name: 'Logout' });
    fireEvent.click(logoutButton);

    expect(logoutButton).toBeDisabled();
    expect(screen.getByText('Logging out...')).toBeInTheDocument();

    await waitFor(() => {
      expect(mockClearAuth).toHaveBeenCalled();
    });
  });

  it('should prevent multiple logout clicks', async () => {
    render(<Header />);

    const logoutButton = screen.getByRole('button', { name: 'Logout' });

    // Click multiple times quickly
    fireEvent.click(logoutButton);
    fireEvent.click(logoutButton);
    fireEvent.click(logoutButton);

    await waitFor(() => {
      expect(api.logout).toHaveBeenCalledTimes(1);
      expect(mockClearAuth).toHaveBeenCalledTimes(1);
    });
  });

  it('should display user email in header when name is not available', () => {
    const mockUserWithoutName = {
      id: 'user-2',
      email: 'test2@example.com',
      name: 'test2@example.com',
      createdAt: new Date().toISOString()
    };

    jest.mocked(require('@/stores/auth-store').useAuthStore).mockImplementation(() => ({
      user: mockUserWithoutName,
      token: 'test-token',
      isAuthenticated: true,
      clearAuth: mockClearAuth,
    }));

    const { rerender } = render(<Header />);
    rerender(<Header />);

    expect(screen.getByText('test2@example.com')).toBeInTheDocument();
  });
});
