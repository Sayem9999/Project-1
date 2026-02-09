import { test, expect } from '@playwright/test';

test.describe('Landing Page', () => {
    test('should load landing page', async ({ page }) => {
        await page.goto('/');
        await expect(page).toHaveTitle(/proedit|edit|ai/i);
    });

    test('should have navigation links', async ({ page }) => {
        await page.goto('/');
        const loginLink = page.locator('a[href*="login"]');
        const signupLink = page.locator('a[href*="signup"]');

        expect(await loginLink.isVisible() || await signupLink.isVisible()).toBeTruthy();
    });

    test('should have call-to-action buttons', async ({ page }) => {
        await page.goto('/');
        const ctaButton = page.locator('a:has-text("Get Started"), a:has-text("Start"), button:has-text("Get Started")');
        await expect(ctaButton.first()).toBeVisible();
    });
});

test.describe('Dashboard (requires auth)', () => {
    // Note: These tests assume user is not authenticated
    // For authenticated tests, you would need to set up auth state

    test('dashboard page responds', async ({ page }) => {
        const response = await page.goto('/dashboard');
        // Should get some response (200, redirect, or auth prompt)
        expect(response?.status()).toBeLessThan(500);
    });
});

test.describe('Admin Page', () => {
    test('admin stats page responds', async ({ page }) => {
        const response = await page.goto('/admin');
        // Should get some response (may require auth)
        expect(response?.status()).toBeLessThan(500);
    });
});
