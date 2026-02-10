const { chromium } = require('@playwright/test');

(async () => {
    console.log('Starting browser launch...');
    try {
        const browser = await chromium.launch({ headless: true });
        console.log('Browser launched successfully!');
        const page = await browser.newPage();
        console.log('Opening page...');
        await page.goto('http://127.0.0.1:3000', { timeout: 10000 });
        console.log('Page title:', await page.title());
        await browser.close();
        console.log('Browser closed.');
    } catch (error) {
        console.error('FAILED to launch or interact with browser:', error);
        process.exit(1);
    }
})();
