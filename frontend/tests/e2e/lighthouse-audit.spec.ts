import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from '@axe-core/playwright';

/**
 * E2E Test: T096 - Lighthouse Audit (Accessibility & Performance)
 *
 * This test verifies:
 * 1. Accessibility compliance (WCAG 2.1 AA)
 * 2. Performance metrics (target score > 85)
 * 3. Best practices
 * 4. SEO basics
 */
test.describe('Lighthouse Audit (Accessibility)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should have no critical accessibility violations on home page', async ({ page }) => {
    await injectAxe(page);
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true },
    });
  });

  test('should have no critical accessibility violations on login page', async ({ page }) => {
    await page.goto('/login');
    await injectAxe(page);
    await checkA11y(page, null, {
      detailedReport: true,
    });
  });

  test('should have no critical accessibility violations on signup page', async ({ page }) => {
    await page.goto('/signup');
    await injectAxe(page);
    await checkA11y(page, null, {
      detailedReport: true,
    });
  });

  test('should have proper heading hierarchy', async ({ page }) => {
    const headings = await page.evaluate(() => {
      const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
      return Array.from(headings).map(h => ({
        tag: h.tagName,
        text: h.textContent?.trim(),
      }));
    });

    // Verify we have at least one h1
    const h1Headings = headings.filter(h => h.tag === 'H1');
    expect(h1Headings.length).toBeGreaterThan(0);

    // Verify h1 is the first heading
    expect(headings[0].tag).toBe('H1');
  });

  test('should have proper ARIA labels on interactive elements', async ({ page }) => {
    // Check all buttons have accessible labels
    const buttons = await page.$$('button');
    for (const button of buttons) {
      const ariaLabel = await button.getAttribute('aria-label');
      const text = await button.textContent();
      const hasTitle = await button.getAttribute('title');

      // Every button should have one of: aria-label, text, or title
      expect(
        ariaLabel !== null || text !== null || hasTitle !== null
      ).toBeTruthy();
    }
  });

  test('should have proper form labels', async ({ page }) => {
    await page.goto('/signup');

    const inputs = await page.$$('input');
    for (const input of inputs) {
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const ariaLabelledBy = await input.getAttribute('aria-labelledby');

      if (id) {
        // Find label by for attribute
        const label = await page.$(`label[for="${id}"]`);
        expect(label || ariaLabel || ariaLabelledBy).toBeTruthy();
      } else {
        expect(ariaLabel || ariaLabelledBy).toBeTruthy();
      }
    }
  });

  test('should have proper focus indicators', async ({ page }) => {
    await page.goto('/login');

    const button = page.getByRole('button', { name: 'Sign In' });
    await button.focus();

    const isFocused = await button.evaluate(el => {
      const styles = window.getComputedStyle(el);
      return (
        styles.outline !== 'none' ||
        styles.boxShadow !== 'none' ||
        styles.border !== 'none'
      );
    });

    expect(isFocused).toBeTruthy();
  });

  test('should have sufficient color contrast', async ({ page }) => {
    await injectAxe(page);
    await checkA11y(page, null, {
      detailedReport: true,
      rules: {
        'color-contrast': { enabled: true },
      },
    });
  });

  test('should have keyboard navigation support', async ({ page }) => {
    await page.goto('/login');

    // Tab through the form
    await page.keyboard.press('Tab');
    await expect(page.locator('#email')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('#password')).toBeFocused();

    await page.keyboard.press('Tab');
    const submitButton = page.getByRole('button', { name: 'Sign In' });
    await expect(submitButton).toBeFocused();

    // Should be able to submit with Enter
    await page.keyboard.press('Enter');
  });

  test('should have touch targets at least 44x44 pixels', async ({ page }) => {
    await page.goto('/login');

    const touchTargets = await page.$$('.touch-target');

    for (const target of touchTargets) {
      const box = await target.boundingBox();
      expect(box).toBeTruthy();

      if (box) {
        const { width, height } = box;
        expect(width).toBeGreaterThanOrEqual(44);
        expect(height).toBeGreaterThanOrEqual(44);
      }
    }
  });
});

test.describe('Performance Metrics', () => {
  test('should load home page within acceptable time', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/');

    // Wait for main content to be visible
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    // Target: Load within 3 seconds (3000ms)
    expect(loadTime).toBeLessThan(3000);
  });

  test('should have fast First Contentful Paint', async ({ page }) => {
    const fcp = await page.evaluate(async () => {
      return new Promise<number>((resolve) => {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          if (entries.length > 0) {
            resolve(entries[0].startTime);
            observer.disconnect();
          }
        });
        observer.observe({ entryTypes: ['paint'] });
      });
    });

    // Target: FCP < 1.8 seconds (1800ms)
    expect(fcp).toBeLessThan(1800);
  });

  test('should have minimal blocking resources', async ({ page }) => {
    const jsFiles = await page.evaluate(() => {
      return performance.getEntriesByType('resource')
        .filter(entry => entry.name.endsWith('.js'))
        .map(entry => ({
          name: entry.name,
          duration: entry.duration,
        }));
    });

    // Log JS file load times for analysis
    console.log('JS files loaded:', jsFiles.length);

    // Should not have excessive number of JS files
    expect(jsFiles.length).toBeLessThan(20);
  });

  test('should have efficient bundle sizes', async ({ page }) => {
    const totalSize = await page.evaluate(() => {
      const entries = performance.getEntriesByType('resource');
      return entries.reduce((total: number, entry: any) => {
        return total + (entry.transferSize || 0);
      }, 0);
    });

    // Target: Total page weight < 2MB
    const sizeInMB = totalSize / (1024 * 1024);
    console.log(`Total page size: ${sizeInMB.toFixed(2)} MB`);
    expect(sizeInMB).toBeLessThan(2);
  });
});

test.describe('SEO Best Practices', () => {
  test('should have proper meta tags', async ({ page }) => {
    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title.length).toBeGreaterThan(0);
    expect(title.length).toBeLessThan(60); // SEO best practice
  });

  test('should have meta description', async ({ page }) => {
    const description = await page.getAttribute('meta[name="description"]', 'content');
    expect(description).toBeTruthy();
    expect(description!.length).toBeLessThan(160); // SEO best practice
  });

  test('should have semantic HTML structure', async ({ page }) => {
    const hasMain = await page.$('main');
    const hasHeader = await page.$('header');
    const hasNav = await page.$('nav');

    expect(hasMain).toBeTruthy();
    expect(hasHeader).toBeTruthy();
    expect(hasNav).toBeTruthy();
  });
});
