import { test, expect } from '@playwright/test';

test('Upload page should render content and not be blank', async ({ page }) => {
    // Navigate to upload page
    console.log('Navigating to upload page...');

    page.on('console', msg => {
        console.log(`BROWSER CONSOLE [${msg.type()}]: ${msg.text()}`);
    });

    page.on('pageerror', err => {
        console.log(`BROWSER PAGE ERROR: ${err.message}`);
    });

    try {
        const response = await page.goto('/dashboard/upload', { waitUntil: 'networkidle' });
        console.log('Response status:', response?.status());

        // Wait for hydration (mounted state in React)
        await page.waitForTimeout(3000);

        // Check for specific text that should be visible
        const h2 = page.locator('h2:has-text("Deploy Footage")');
        const isVisible = await h2.isVisible();
        console.log('H2 "Deploy Footage" visible:', isVisible);

        const bodyContent = await page.textContent('body');
        console.log('Body length:', bodyContent?.length);

        if (!isVisible && bodyContent?.length && bodyContent.length < 500) {
            console.log('WARNING: Body content seems very short, might be a blank page or error.');
        }

        expect(isVisible).toBeTruthy();
    } catch (e) {
        console.log('Test caught error:', e.message);
        throw e;
    }
});
