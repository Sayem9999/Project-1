import { test, expect } from '@playwright/test';

test.describe('Maintenance & System Map', () => {

    test('should show System Map tab in Admin Dashboard', async ({ page }) => {
        // Navigate to admin (assuming dev server handles auth or bypasses for test)
        await page.goto('/admin');

        // Check if System Map tab button exists
        const systemTab = page.locator('button:has-text("System Map")');
        await expect(systemTab).toBeVisible();
    });

    test('should switch to System Map and show graph nodes', async ({ page }) => {
        await page.goto('/admin');

        // Click System Map tab
        await page.click('button:has-text("System Map")');

        // Verify header text
        await expect(page.locator('h3:has-text("Codebase Architecture")')).toBeVisible();

        // Verify stats cards are present
        await expect(page.locator('div:has-text("Nodes")')).toBeVisible();
        await expect(page.locator('div:has-text("Endpoints")')).toBeVisible();

        // Verify maintenance buttons exist
        await expect(page.locator('button:has-text("Run Audit")')).toBeVisible();
        await expect(page.locator('button:has-text("Auto-Heal")')).toBeVisible();
    });

    test('should show node details when a node is clicked', async ({ page }) => {
        await page.goto('/admin');
        await page.click('button:has-text("System Map")');

        // Wait for nodes to load (at least one node should be visible)
        const firstNode = page.locator('button.group').first();
        await expect(firstNode).toBeVisible({ timeout: 10000 });

        // Click the node
        await firstNode.click();

        // Check if node details card appeared
        await expect(page.locator('h4.text-white')).toBeVisible();
        await expect(page.locator('span:has-text("ID")')).toBeVisible();
    });
});
