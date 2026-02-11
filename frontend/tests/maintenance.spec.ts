import { test, expect } from '@playwright/test';

test.describe('Maintenance & System Map', () => {
    test.beforeEach(async ({ page }) => {
        await page.addInitScript(() => {
            localStorage.setItem('token', 'test-token');
            localStorage.setItem(
                'user',
                JSON.stringify({ id: 1, email: 'admin@example.com', is_admin: true })
            );
        });

        await page.route('**/admin/stats*', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    users: { total: 1, active_24h: 1 },
                    jobs: { total: 1, recent_24h: 1 },
                    storage: { used_gb: 1, limit_gb: 10, percent: 10, files: 1 },
                }),
            });
        });

        await page.route('**/admin/users*', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify([
                    {
                        id: 1,
                        email: 'admin@example.com',
                        full_name: 'Admin',
                        credits: 10,
                        is_admin: true,
                        created_at: new Date().toISOString(),
                    },
                ]),
            });
        });

        await page.route('**/admin/jobs*', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify([]),
            });
        });

        await page.route('**/admin/health*', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    db: { reachable: true },
                    redis: { configured: true, reachable: true, latency_ms: 2 },
                    storage: { used_gb: 1, limit_gb: 10, percent: 10, files: 1 },
                    llm: {},
                }),
            });
        });

        await page.route('**/maintenance/graph*', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    nodes: [
                        { id: 'endpoint:/health', type: 'endpoint', label: 'GET /health', file: '/app/main.py' },
                        { id: 'service:workflow', type: 'service', label: 'workflow_engine', file: '/app/services/workflow_engine.py' },
                    ],
                    edges: [{ source: 'service:workflow', target: 'endpoint:/health', type: 'uses' }],
                    stats: { source_files: 2, total_nodes: 2, total_edges: 1, lines_of_code: 120 },
                }),
            });
        });

        await page.route('**/maintenance/audit*', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ status: 'ok' }),
            });
        });

        await page.route('**/maintenance/heal*', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ status: 'ok' }),
            });
        });
    });

    test('should show System Map tab in Admin Dashboard', async ({ page }) => {
        await page.goto('/admin');

        const systemTab = page.locator('button:has-text("System Map")');
        await expect(systemTab).toBeVisible();
    });

    test('should switch to System Map and show graph nodes', async ({ page }) => {
        await page.goto('/admin');

        await page.click('button:has-text("System Map")');

        await expect(page.locator('div.text-xs.text-gray-500', { hasText: /^Nodes$/ }).first()).toBeVisible();
        await expect(page.locator('div.text-xs.text-gray-500', { hasText: /^Endpoints$/ }).first()).toBeVisible();

        await expect(page.locator('button:has-text("Run Audit")')).toBeVisible();
        await expect(page.locator('button:has-text("Auto-Heal")')).toBeVisible();
    });

    test('should show node details when a node is clicked', async ({ page }) => {
        await page.goto('/admin');
        await page.click('button:has-text("System Map")');

        const firstNode = page.locator('button.group').first();
        await expect(firstNode).toBeVisible({ timeout: 10000 });

        await firstNode.click();

        await expect(page.locator('h4.text-white')).toBeVisible();
        await expect(page.locator('span:has-text("ID")')).toBeVisible();
    });
});
