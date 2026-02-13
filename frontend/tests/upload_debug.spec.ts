import { test, expect } from '@playwright/test';

test('Capture Upload page state', async ({ page }) => {
    console.log('Navigating to upload page...');

    const logs: string[] = [];
    page.on('console', msg => {
        const text = `BROWSER [${msg.type()}]: ${msg.text()}`;
        console.log(text);
        logs.push(text);
    });

    page.on('pageerror', err => {
        const text = `BROWSER ERROR: ${err.message}\nStack: ${err.stack}`;
        console.log(text);
        logs.push(text);
    });

    try {
        await page.goto('/dashboard/upload', { waitUntil: 'load' });

        // Wait for hydration and potential async ops
        await page.waitForTimeout(5000);

        // Take screenshot
        const screenshotPath = `C:/Users/Sayem/.gemini/antigravity/brain/b372c6b5-036b-46dd-818d-89dbf96fa2eb/upload_debug.png`;
        await page.screenshot({ path: screenshotPath, fullPage: true });
        console.log(`Screenshot saved to ${screenshotPath}`);

        const bodyHTML = await page.evaluate(() => document.body.innerHTML);
        console.log('Body HTML length:', bodyHTML.length);
        if (bodyHTML.length < 100) {
            console.log('BODY CONTENT IS MINIMAL:', bodyHTML);
        }

        // Check if any error is visible in the console logs
        const hasError = logs.some(l => l.includes('ERROR'));
        console.log('Console had errors:', hasError);
    } catch (e) {
        console.log('Test execution failed:', e.message);
    }
});
