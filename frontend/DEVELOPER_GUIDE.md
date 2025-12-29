# Developer Guide - Responsive UI & Accessibility

Quick reference guide for maintaining responsive UI and accessibility standards in the Todo App.

## Responsive Design

### Breakpoints

```tsx
// Tailwind breakpoints
sm: 640px   // Small tablets
md: 768px   // Tablets
lg: 1024px  // Desktops
xl: 1280px  // Large desktops

// Usage
<div className="text-sm sm:text-base md:text-lg">
  Responsive text
</div>
```

### Mobile-First Pattern

```tsx
// ✅ Good: Mobile first
<div className="px-4 sm:px-6 lg:px-8">

// ❌ Bad: Desktop first
<div className="px-8 sm:px-6 px-4">
```

### Touch Targets

```tsx
// Always use touch-target class for interactive elements
<button className="touch-target min-h-[44px] min-w-[44px]">
  Click me
</button>
```

## Dark Mode

### Using Theme

```tsx
import { useUIStore } from '@/stores/ui-store';

function MyComponent() {
  const { theme, toggleTheme } = useUIStore();

  return (
    <button onClick={toggleTheme}>
      {theme === 'light' ? '🌙' : '☀️'}
    </button>
  );
}
```

### Color Classes

```tsx
// Use semantic color classes
<div className="bg-background text-foreground">
  <p className="text-muted-foreground">Muted text</p>
  <button className="bg-primary text-primary-foreground">
    Primary action
  </button>
</div>
```

### Custom Colors

```css
/* globals.css */
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
}

.dark {
  --background: 224 71% 4%;
  --foreground: 213 31% 91%;
}
```

## Animations

### Framer Motion Patterns

```tsx
import { motion } from 'framer-motion';

// Entry animation
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  Content
</motion.div>

// Exit animation
<motion.div
  exit={{ opacity: 0, x: -100 }}
  transition={{ duration: 0.2 }}
>
  Content
</motion.div>

// Layout animation
<motion.div layout>
  Reorderable content
</motion.div>
```

### Spring Animations

```tsx
// Natural spring physics
<motion.div
  animate={{ scale: 1 }}
  transition={{
    type: 'spring',
    stiffness: 300,
    damping: 30,
  }}
/>
```

### List Animations

```tsx
import { AnimatePresence } from 'framer-motion';

<AnimatePresence mode="popLayout">
  {items.map(item => (
    <motion.div
      key={item.id}
      layout
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {item.content}
    </motion.div>
  ))}
</AnimatePresence>
```

## Accessibility

### ARIA Labels

```tsx
// Buttons
<button aria-label="Delete task">
  <TrashIcon />
</button>

// Forms
<input
  id="email"
  aria-required="true"
  aria-invalid={hasError}
  aria-describedby={hasError ? 'email-error' : undefined}
/>
{hasError && (
  <p id="email-error" role="alert">
    {errorMessage}
  </p>
)}

// Navigation
<nav aria-label="Main navigation">
  <Link href="/" aria-current="page">Home</Link>
</nav>
```

### Semantic HTML

```tsx
// ✅ Good
<header>
  <nav aria-label="Main">
    <Link href="/">Home</Link>
  </nav>
</header>

<main>
  <article>
    <h1>Title</h1>
    <section>Content</section>
  </article>
</main>

// ❌ Bad
<div className="header">
  <div className="nav">
    <a href="/">Home</a>
  </div>
</div>
```

### Keyboard Navigation

```tsx
// Ensure all interactive elements are keyboard accessible
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
  Custom button
</div>

// Better: Use actual button
<button onClick={handleClick}>
  Semantic button
</button>
```

### Focus Management

```tsx
import { useRef, useEffect } from 'react';

function Modal({ onClose }) {
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    // Focus first element on mount
    closeButtonRef.current?.focus();

    // Return focus on unmount
    return () => {
      previouslyFocusedElement?.focus();
    };
  }, []);

  return (
    <div role="dialog" aria-modal="true">
      <button ref={closeButtonRef} onClick={onClose}>
        Close
      </button>
    </div>
  );
}
```

## Loading States

### Skeleton Loaders

```tsx
import { TaskListSkeleton } from '@/components/tasks/skeleton';

function TaskList() {
  const [loading, setLoading] = useState(true);

  if (loading) {
    return <TaskListSkeleton count={3} />;
  }

  return <div>Content</div>;
}
```

### Empty States

```tsx
import { EmptyState } from '@/components/tasks/empty-state';

function TaskList() {
  if (tasks.length === 0) {
    return (
      <EmptyState
        title="No tasks yet"
        description="Create your first task to get started"
        action={<CreateTaskButton />}
      />
    );
  }

  return <div>Tasks</div>;
}
```

### Loading Indicators

```tsx
// With aria-busy
<div aria-busy={isLoading}>
  {isLoading ? 'Loading...' : 'Content'}
</div>

// With skeleton
{isLoading ? <Skeleton className="h-20 w-full" /> : <Content />}
```

## Forms

### Accessible Forms

```tsx
<form aria-label="Create task">
  <label htmlFor="title">
    Title <span aria-label="required">*</span>
  </label>
  <input
    id="title"
    type="text"
    required
    aria-required="true"
    aria-invalid={hasError}
    aria-describedby={hasError ? 'title-error' : undefined}
  />
  {hasError && (
    <p id="title-error" role="alert">
      {errorMessage}
    </p>
  )}

  <button type="submit" aria-busy={isSubmitting}>
    {isSubmitting ? 'Creating...' : 'Create Task'}
  </button>
</form>
```

## Testing

### Testing Components

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('button is accessible', async () => {
  const user = userEvent.setup();
  render(<Button>Click me</Button>);

  const button = screen.getByRole('button', { name: 'Click me' });

  // Has accessible name
  expect(button).toHaveAccessibleName();

  // Is keyboard accessible
  await user.tab();
  expect(button).toHaveFocus();

  // Can be activated
  await user.keyboard('{Enter}');
  expect(mockFn).toHaveBeenCalled();
});
```

### Testing Responsive

```tsx
test('responsive layout', () => {
  global.innerWidth = 375;
  global.innerHeight = 667;

  render(<Header />);

  // Test mobile-specific behavior
  expect(screen.getByRole('banner')).toBeInTheDocument();
});
```

### Testing Dark Mode

```tsx
test('toggles dark mode', async () => {
  const user = userEvent.setup();
  render(<Header />);

  const toggle = screen.getByLabelText(/dark mode/i);
  await user.click(toggle);

  expect(document.documentElement).toHaveClass('dark');
});
```

## Common Patterns

### Conditional Styling

```tsx
import { cn } from '@/lib/utils';

<div className={cn(
  'base-class',
  isActive && 'active-class',
  isDisabled && 'disabled-class',
  className // Allow override
)}>
```

### Responsive Images

```tsx
<img
  src="/image.jpg"
  srcSet="/image-sm.jpg 640w, /image-md.jpg 768w, /image-lg.jpg 1024w"
  sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, 33vw"
  alt="Descriptive alt text"
/>
```

### Responsive Typography

```tsx
<h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold">
  Responsive heading
</h1>
```

## Checklist for New Components

- [ ] Responsive across all breakpoints (320px+)
- [ ] Touch targets minimum 44px
- [ ] Keyboard accessible
- [ ] ARIA labels on interactive elements
- [ ] Semantic HTML
- [ ] Focus indicators visible
- [ ] Loading/error states
- [ ] Dark mode compatible
- [ ] Animations respect reduced motion
- [ ] Tests written

## Tools

### Development
- Chrome DevTools (Lighthouse, Accessibility audit)
- React DevTools
- Tailwind CSS IntelliSense

### Accessibility
- axe DevTools browser extension
- WAVE browser extension
- Color contrast analyzer
- NVDA/JAWS screen readers

### Testing
- Jest + React Testing Library
- Chrome DevTools device emulation

## Resources

- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Framer Motion Docs](https://www.framer.com/motion/)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Practices](https://www.w3.org/WAI/ARIA/apg/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
