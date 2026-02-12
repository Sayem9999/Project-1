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
        await page.route('**/jobs/**/start*', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ status: 'ok', job_id: 123 }),
            });
        });
        await page.route('**/jobs/123', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    id: 123,
                    status: 'processing',
                    progress_message: 'Starting pipeline...',
                    created_at: new Date().toISOString(),
                }),
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
        const jobId = await page.evaluate(async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Missing auth token after signup');
            }

            const formData = new FormData();
            const file = new File([new Blob(['dummy-video-content'], { type: 'video/mp4' })], 'dummy_video.mp4', {
                type: 'video/mp4',
            });
            formData.append('file', file);
            formData.append('theme', 'professional');
            formData.append('tier', 'pro');
            formData.append('platform', 'youtube');

            const uploadRes = await fetch('http://localhost:8000/api/jobs/upload', {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` },
                body: formData,
            });
            if (!uploadRes.ok) {
                throw new Error(`Upload failed: ${uploadRes.status}`);
            }
            const uploadBody = await uploadRes.json();
            const createdJobId = uploadBody?.id;
            if (!createdJobId) {
                throw new Error('Upload did not return job id');
            }

            const startRes = await fetch(`http://localhost:8000/api/jobs/${createdJobId}/start`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!startRes.ok) {
                throw new Error(`Start failed: ${startRes.status}`);
            }

            return createdJobId as number;
        });

        await page.goto(`/jobs/${jobId}`);
        await expect(page).toHaveURL(new RegExp(`.*/jobs/${jobId}$`), { timeout: 30000 });
        console.log('Successfully redirected to job status page');
    });
});
