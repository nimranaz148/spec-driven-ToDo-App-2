import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AuthForm } from '@/components/auth/auth-form';

// Mock the API
jest.mock('@/lib/api', () => ({
  api: {
    login: jest.fn(),
    register: jest.fn(),
  },
}));

// Mock the auth store
jest.mock('@/stores/auth-store', () => ({
  useAuthStore: jest.fn(() => ({
    user: null,
    token: null,
    isAuthenticated: false,
    setAuth: jest.fn(),
  })),
}));

// Mock the router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

import { api } from '@/lib/api';

describe('AuthForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Login Mode', () => {
    it('should render login form correctly', () => {
      render(<AuthForm mode="login" />);

      expect(screen.getByText('Welcome back')).toBeInTheDocument();
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
    });

    it('should show validation errors for invalid email', async () => {
      render(<AuthForm mode="login" />);

      const emailInput = screen.getByLabelText('Email');
      const submitButton = screen.getByRole('button', { name: 'Sign In' });

      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
      fireEvent.click(submitButton);

      expect(await screen.findByText('Invalid email address')).toBeInTheDocument();
    });

    it('should call login API with correct data', async () => {
      (api.login as jest.Mock).mockResolvedValue({
        accessToken: 'test-token',
        user: { id: '1', email: 'test@example.com', name: 'Test User', createdAt: new Date().toISOString() },
      });

      render(<AuthForm mode="login" />);

      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: 'Sign In' });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(api.login).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password123',
        });
      });
    });
  });

  describe('Register Mode', () => {
    it('should render register form correctly', () => {
      render(<AuthForm mode="register" />);

      expect(screen.getByText('Create an account')).toBeInTheDocument();
      expect(screen.getByLabelText('Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Create Account' })).toBeInTheDocument();
    });

    it('should show validation error for short password', async () => {
      render(<AuthForm mode="register" />);

      const nameInput = screen.getByLabelText('Name');
      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: 'Create Account' });

      fireEvent.change(nameInput, { target: { value: 'Test User' } });
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'short' } });
      fireEvent.click(submitButton);

      expect(await screen.findByText('Password must be at least 8 characters')).toBeInTheDocument();
    });
  });
});
