import { test, expect } from '@playwright/test';

test.describe('E2E Flow', () => {
    test('should sign up and upload a video', async ({ page }) => {
        // Enable debug logging
        page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));
        page.on('pageerror', exception => console.log(`BROWSER EXCEPTION: "${exception}"`));
        page.on('response', response => {
            if (response.status() >= 400) {
                console.log(`<< API ERROR: ${response.status()} ${response.url()}`);
            }
        });

        // Mock auth + upload endpoints for local E2E stability
        await page.route('**/auth/signup', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ access_token: 'test-token' }),
            });
        });
        await page.route('**/jobs/upload', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ id: 123 }),
            });
        });

        const timestamp = Date.now();
        const email = `testuser${timestamp}@example.com`;
        const password = 'Password123!';

        console.log(`Testing signup with email: ${email}`);

        await page.goto('/signup');

        // Fill form
        await page.fill('input[type="email"]', email);
        await page.fill('input[type="password"]', password);

        // Click signup
        await page.click('button[type="submit"]');

        // Expect redirection to dashboard/upload
        try {
            await expect(page).toHaveURL(/.*\/dashboard\/upload/, { timeout: 15000 });
            console.log('Successfully redirected to dashboard/upload');
        } catch (e) {
            console.log('Redirect failed. Checking for error messages...');
            const errorMsg = await page.locator('.bg-red-500\\/10').textContent().catch(() => null);
            if (errorMsg) {
                console.log(`Signup Error Message: ${errorMsg}`);
            }
            throw e;
        }

        // --- UPLOAD FLOW ---
        console.log('Starting upload flow...');

        // Upload file
        // Ensure the dummy file exists in the directory where playwright runs (frontend/)
        await page.setInputFiles('input[type="file"]', 'dummy_video.mp4');

        // Wait for "Launch Pipeline" button to appear (it's in the preview overlay)
        const launchButton = page.getByRole('button', { name: 'Launch Pipeline' });
        await expect(launchButton).toBeVisible({ timeout: 5000 });

        // Click Launch
        await launchButton.click();

        // Wait for redirection to job status page (e.g. /jobs/123)
        // Use a longer timeout for job creation
        await expect(page).toHaveURL(/.*\/jobs\/.*/, { timeout: 30000 });
        console.log('Successfully redirected to job status page');
    });
});
