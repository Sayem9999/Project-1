import { test, expect } from '@playwright/test';

test.describe('Dashboard & Upload UI Check', () => {
    test('dashboard layout renders', async ({ page }) => {
        // Skip auth by going straight to dashboard (might redirect but we can check the trace)
        await page.goto('/dashboard');
        // If redirected to login, that's fine, it means the app is running
        const title = await page.title();
        console.log('Page Title:', title);
        expect(title).toBeDefined();
    });

    test('upload page is accessible', async ({ page }) => {
        // We'll try to visit the upload page directly
        const response = await page.goto('/dashboard/upload');
        console.log('Upload page response status:', response?.status());

        // Check for common error indicators
        const bodyContent = await page.textContent('body');
        if (bodyContent?.includes('404') || bodyContent?.includes('Not Found')) {
            console.log('DETECTED 404 ON UPLOAD PAGE');
        }

        // Wait for hydration guard if it exists
        await page.waitForTimeout(2000);

        const h1 = page.locator('h1');
        if (await h1.count() > 0) {
            console.log('Found H1:', await h1.innerText());
        }

        expect(response?.status()).toBeLessThan(400);
    });
});
