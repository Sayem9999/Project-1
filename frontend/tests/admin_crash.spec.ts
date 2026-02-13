import { test, expect } from '@playwright/test';

test('Admin panel should load or show specific error', async ({ page }) => {
    // Navigate to admin (it might redirect to login if not auth'd, but we want to see if it Crashes first)
    // We'll mock the auth in the next step if needed, but often "Something went wrong" happens
    // during hydration or right after mount.

    page.on('console', msg => {
        console.log(`BROWSER CONSOLE [${msg.type()}]: ${msg.text()}`);
    });

    page.on('pageerror', err => {
        console.log(`BROWSER PAGE ERROR: ${err.message}`);
    });

    try {
        await page.goto('/admin', { waitUntil: 'networkidle' });

        // Wait for potential hydration and mount
        await page.waitForTimeout(5000);

        const bodyText = await page.textContent('body');
        if (bodyText?.includes('Something went wrong')) {
            console.log('CONFIRMED: Admin panel hit the Global Error Boundary');
        } else {
            console.log('Admin panel did not hit the Global Error Boundary or redirected elsewhere');
        }
    } catch (e) {
        console.log('Test caught navigation error:', e.message);
    }
});
