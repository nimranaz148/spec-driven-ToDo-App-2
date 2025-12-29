# E2E Tests with Playwright

This directory contains end-to-end tests for the Todo App using Playwright.

## Test Coverage

### User Authentication
- **register.spec.ts** (T091): Tests user registration flow, validation, and redirect
- **login.spec.ts** (T092): Tests login/logout flow, session persistence, and error handling

### Task Management
- **create-task.spec.ts** (T093): Tests task creation, form validation, and loading states
- **complete-task.spec.ts** (T094): Tests task completion toggle, counters, and filters
- **delete-task.spec.ts** (T095): Tests task deletion, counter updates, and persistence

### Performance & Quality
- **lighthouse-audit.spec.ts** (T096): Accessibility compliance, performance metrics, and SEO
- **api-response-time.spec.ts** (T097): API endpoint performance (target: p95 < 200ms)
- **slow-network.spec.ts** (T098): App behavior under 3G network conditions

## Prerequisites

1. Backend server running at `http://localhost:8000`
2. PostgreSQL database configured

## Running Tests

### Run all E2E tests
```bash
cd frontend
npm run test:e2e
```

### Run tests with UI (watch mode)
```bash
npm run test:e2e:ui
```

### Debug a specific test
```bash
npm run test:e2e:debug
```

### Run specific test file
```bash
npx playwright test register.spec.ts
```

### Run specific test project (browser)
```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### Run specific viewport
```bash
npx playwright test --project="Mobile Chrome"
npx playwright test --project="Mobile Safari"
```

## Viewing Test Reports

After running tests, view the HTML report:
```bash
npm run test:e2e:report
```

## Test Configuration

The `playwright.config.ts` file configures:

- **Browsers**: Chromium, Firefox, WebKit
- **Mobile Viewports**: Pixel 5, iPhone 12
- **Base URL**: `http://localhost:3000`
- **Web Server**: Automatically starts Next.js dev server
- **Retry**: 2 retries on CI, 0 locally
- **Screenshots**: Captured on failure
- **Video**: Captured on failure
- **Trace**: Captured on first retry

## Network Profiles

The slow-network tests use the following 3G profiles:

### Slow 3G
- Download: 750 Kbps
- Upload: 250 Kbps
- Latency: 100ms

### Fast 3G
- Download: 1.6 Mbps
- Upload: 750 Kbps
- Latency: 100ms

## Test Scenarios

### Full Workflow (slow-network.spec.ts)
The most comprehensive test runs a complete workflow:
1. Register user
2. Login
3. Create task
4. Complete task
5. Delete task
6. Logout

All steps are tested under slow 3G network conditions.

## Performance Targets

- **API Response Time**: p95 < 200ms
- **First Contentful Paint**: < 1.8s
- **Page Load Time**: < 3s
- **Total Page Weight**: < 2MB
- **Accessibility**: WCAG 2.1 AA compliance

## Troubleshooting

### Tests fail with "Network error"
Ensure the backend server is running:
```bash
cd backend
python -m uvicorn src.main:app --reload --port 8000
```

### Tests timeout on slow network
Adjust timeout in `playwright.config.ts` or increase network speed in test profiles.

### Browser not found
Install Playwright browsers:
```bash
npm run test:e2e:install
```

## Adding New Tests

1. Create a new spec file in `tests/e2e/`
2. Use the following structure:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test('should do something', async ({ page }) => {
    // Your test code
  });
});
```

3. Run tests to verify

## CI/CD Integration

For GitHub Actions, add:

```yaml
- name: Run E2E tests
  run: cd frontend && npm run test:e2e
```

## Notes

- Tests use unique email addresses to avoid conflicts
- Tests create users via API before UI interactions
- Mobile viewport tests ensure responsive design
- Accessibility tests use Axe Core
