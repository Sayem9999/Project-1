import { test, expect } from '@playwright/test';

test.describe('E2E Flow', () => {
    test('should sign up and upload a video', async ({ page }) => {
        page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));
        page.on('pageerror', exception => console.log(`BROWSER EXCEPTION: "${exception}"`));
        page.on('response', response => {
            if (response.status() >= 400) {
                console.log(`<< API ERROR: ${response.status()} ${response.url()}`);
            }
        });

        await page.route('**/auth/signup*', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ access_token: 'test-token' }),
            });
        });
        await page.route('**/auth/me*', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ id: 1, email: 'test@example.com', is_admin: false, credits: 10 }),
            });
        });
        await page.route('**/jobs/upload*', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ id: 123 }),
            });
        });
        await page.route('**/jobs/123/start*', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ status: 'ok', job_id: 123 }),
            });
        });

        const timestamp = Date.now();
        const email = `testuser${timestamp}@example.com`;
        const password = 'Password123!';

        console.log(`Testing signup with email: ${email}`);

        await page.goto('/signup');

        await page.fill('input[type="email"]', email);
        await page.fill('input[type="password"]', password);

        await page.click('button[type="submit"]');

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

        console.log('Starting upload flow...');

        await page.setInputFiles('input[type="file"]', {
            name: 'dummy_video.mp4',
            mimeType: 'video/mp4',
            buffer: Buffer.from('dummy-video-content'),
        });

        const uploadButton = page.getByRole('button', { name: 'Start Upload' }).first();
        await expect(uploadButton).toBeVisible({ timeout: 10000 });
        await uploadButton.click();

        const startEditButton = page.getByRole('button', { name: 'Start Edit' });
        await expect(startEditButton).toBeVisible({ timeout: 10000 });
        await startEditButton.click();

        await expect(page).toHaveURL(/.*\/jobs\/123/, { timeout: 30000 });
        console.log('Successfully redirected to job status page');
    });
});
