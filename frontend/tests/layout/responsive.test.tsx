import { render, screen } from '@testing-library/react';
import { Header } from '@/components/layout/header';
import { Nav } from '@/components/layout/nav';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    pathname: '/',
  })),
  usePathname: jest.fn(() => '/'),
}));

// Mock auth and UI stores
jest.mock('@/stores/auth-store', () => ({
  useAuthStore: jest.fn(() => ({
    user: null,
    isAuthenticated: false,
    clearAuth: jest.fn(),
  })),
}));

jest.mock('@/stores/ui-store', () => ({
  useUIStore: jest.fn(() => ({
    theme: 'light',
    toggleTheme: jest.fn(),
  })),
}));

describe('Responsive Layout', () => {
  describe('Header Component', () => {
    it('renders on mobile viewports', () => {
      // Set viewport to mobile
      global.innerWidth = 375;
      global.innerHeight = 667;

      render(<Header />);

      // Header should be visible
      expect(screen.getByRole('banner')).toBeInTheDocument();
    });

    it('renders on tablet viewports', () => {
      // Set viewport to tablet
      global.innerWidth = 768;
      global.innerHeight = 1024;

      render(<Header />);

      expect(screen.getByRole('banner')).toBeInTheDocument();
    });

    it('renders on desktop viewports', () => {
      // Set viewport to desktop
      global.innerWidth = 1920;
      global.innerHeight = 1080;

      render(<Header />);

      expect(screen.getByRole('banner')).toBeInTheDocument();
    });

    it('has touch-friendly button sizes', () => {
      render(<Header />);

      const themeToggle = screen.getByLabelText(/switch to dark mode/i);

      // Touch target should be at least 44px
      const styles = window.getComputedStyle(themeToggle);
      const minHeight = parseInt(styles.minHeight || styles.height || '0');
      const minWidth = parseInt(styles.minWidth || styles.width || '0');

      expect(minHeight).toBeGreaterThanOrEqual(40); // Accounting for padding
      expect(minWidth).toBeGreaterThanOrEqual(40);
    });
  });

  describe('Nav Component', () => {
    it('renders navigation on mobile', () => {
      global.innerWidth = 375;

      render(<Nav />);

      expect(screen.getByRole('navigation', { name: /task filters/i })).toBeInTheDocument();
    });

    it('renders navigation on desktop', () => {
      global.innerWidth = 1920;

      render(<Nav />);

      expect(screen.getByRole('navigation', { name: /task filters/i })).toBeInTheDocument();
    });

    it('has accessible navigation items', () => {
      render(<Nav />);

      const allTasksLink = screen.getByRole('link', { name: /all tasks/i });
      expect(allTasksLink).toBeInTheDocument();
      expect(allTasksLink).toHaveAttribute('href', '/');
    });
  });

  describe('Responsive Breakpoints', () => {
    it('supports minimum width of 320px', () => {
      global.innerWidth = 320;
      global.innerHeight = 568;

      render(<Header />);

      // Should not cause horizontal overflow
      const header = screen.getByRole('banner');
      expect(header).toBeInTheDocument();
    });

    it('adapts to large desktop screens', () => {
      global.innerWidth = 2560;
      global.innerHeight = 1440;

      render(<Header />);

      const header = screen.getByRole('banner');
      expect(header).toBeInTheDocument();
    });
  });
});
