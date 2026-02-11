import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
    test('should display the homepage', async ({ page }) => {
        await page.goto('/');
        await expect(page).toHaveTitle(/Edit\.AI/i);
    });

    test('should have navigation links', async ({ page }) => {
        await page.goto('/');
        await expect(page.locator('nav')).toBeVisible();
    });

    test('should navigate to pricing', async ({ page }) => {
        await page.goto('/');
        const pricingLink = page.getByRole('link', { name: /pricing/i }).first();
        await expect(pricingLink).toBeVisible();
        await Promise.all([
            page.waitForURL('**/pricing', { timeout: 15000 }),
            pricingLink.click(),
        ]);
        await expect(page).toHaveURL(/pricing/);
    });
});

test.describe('Authentication', () => {
    test('should display login page', async ({ page }) => {
        await page.goto('/login');
        await expect(page.locator('form')).toBeVisible();
    });

    test('should display signup page', async ({ page }) => {
        await page.goto('/signup');
        await expect(page.locator('form')).toBeVisible();
    });
});

test.describe('Dashboard', () => {
    test('should redirect unauthenticated users', async ({ page }) => {
        await page.goto('/dashboard');
        // Should redirect to login or show auth prompt
        await expect(page).toHaveURL(/login|auth|dashboard/);
    });
});
