import { test, expect } from '@playwright/test';

test('Verify navigation stability (No blank pages)', async ({ page }) => {
    // Start at dashboard
    await page.goto('/dashboard');
    await expect(page.getByText(/Studio Workspace/i)).toBeVisible({ timeout: 10000 });

    console.log('Navigating to Upload via link (Client-side)...');
    // Click "New Project" link to trigger client-side navigation
    await page.click('a[href="/dashboard/upload"]');

    // Should NOT be blank
    await expect(page.getByText(/Deploy Footage/i)).toBeVisible({ timeout: 10000 });

    console.log('Navigating back to Dashboard...');
    await page.click('a[href="/dashboard"]');
    await expect(page.getByText(/Studio Workspace/i)).toBeVisible({ timeout: 10000 });

    // Verify it doesn't crash on multiple toggles
    for (let i = 0; i < 3; i++) {
        await page.goto('/dashboard/upload');
        await expect(page.getByText(/Deploy Footage/i)).toBeVisible();
        await page.goto('/dashboard');
        await expect(page.getByText(/Studio Workspace/i)).toBeVisible();
    }
});
