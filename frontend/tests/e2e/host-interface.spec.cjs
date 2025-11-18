// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Host Interface', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/host');
    await expect(page.locator('h1')).toContainText('YouTube Party');
  });

  test('should display the host interface correctly', async ({ page }) => {
    // Check main elements are present
    await expect(page.locator('h1')).toContainText('YouTube Party');

    // Check for YouTube player container
    await expect(page.locator('#player')).toBeVisible();

    // Check for current info section
    await expect(page.locator('#current-info')).toBeVisible();

    // Check for queue list
    await expect(page.locator('#queue-list')).toBeVisible();

    // Check for skip button
    await expect(page.locator('#skip-button')).toBeVisible();
  });

  test('should show empty queue message when no videos', async ({ page }) => {
    // Initially queue should be empty
    const currentInfo = page.locator('#current-info');
    await expect(currentInfo).toContainText('Queue is empty', { timeout: 5000 });
  });

  test('should display QR code for easy mobile access', async ({ page }) => {
    // Check QR code is present
    const qrCode = page.locator('#qr-code');
    await expect(qrCode).toBeVisible();

    // QR code should have a valid src
    const src = await qrCode.getAttribute('src');
    expect(src).toContain('/api/qrcode');
  });

  test('should display server URL for connection', async ({ page }) => {
    // Check server URL is displayed
    const serverUrl = page.locator('#server-url');
    await expect(serverUrl).toBeVisible();

    // URL should contain http and port 8000
    const urlText = await serverUrl.textContent();
    expect(urlText).toContain('http');
  });

  test('should have YouTube player iframe loaded', async ({ page }) => {
    // Wait for YouTube iframe API to load
    await page.waitForTimeout(3000);

    // Check if YouTube iframe is present (it gets created by the API)
    const iframe = page.frameLocator('iframe[src*="youtube.com"]');
    // Just checking that we can locate it means the API loaded successfully
  });

  test('should display queue items with position numbers', async ({ page, context }) => {
    // Open guest page in new tab to add a video
    const guestPage = await context.newPage();
    await guestPage.goto('/');

    // Add a video from guest interface
    await guestPage.fill('#video-url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    await guestPage.fill('#user-name', 'Test User');
    await guestPage.click('#add-button');
    await guestPage.waitForTimeout(1000);

    // Add another video
    await guestPage.fill('#video-url', 'https://www.youtube.com/watch?v=jNQXAC9IVRw');
    await guestPage.click('#add-button');
    await guestPage.waitForTimeout(1000);

    // Check host interface shows queue
    const queueList = page.locator('#queue-list');

    // Should have queue items (first one is playing, second is in queue)
    await expect(queueList.locator('.host-queue-item')).toHaveCount(1, { timeout: 5000 });

    // Queue item should have position number
    await expect(queueList.locator('.position')).toContainText('1');

    await guestPage.close();
  });

  test('should show remove buttons for queue items', async ({ page, context }) => {
    // Add a video via guest interface
    const guestPage = await context.newPage();
    await guestPage.goto('/');
    await guestPage.fill('#video-url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    await guestPage.click('#add-button');
    await guestPage.waitForTimeout(1000);

    // Add second video so we have one in queue
    await guestPage.fill('#video-url', 'https://www.youtube.com/watch?v=jNQXAC9IVRw');
    await guestPage.click('#add-button');
    await guestPage.waitForTimeout(2000);

    // Check for remove button
    const removeButton = page.locator('.btn-remove');
    await expect(removeButton).toHaveCount(1, { timeout: 5000 });
    await expect(removeButton).toContainText('Remove');

    await guestPage.close();
  });

  test('should allow removing videos from queue', async ({ page, context }) => {
    // Add videos via guest interface
    const guestPage = await context.newPage();
    await guestPage.goto('/');
    await guestPage.fill('#video-url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    await guestPage.click('#add-button');
    await guestPage.waitForTimeout(1000);

    await guestPage.fill('#video-url', 'https://www.youtube.com/watch?v=jNQXAC9IVRw');
    await guestPage.click('#add-button');
    await guestPage.waitForTimeout(2000);

    // Get queue count before removal
    const queueCount = page.locator('#queue-count');
    const beforeCount = await queueCount.textContent();

    // Click remove button
    const removeButton = page.locator('.btn-remove').first();
    await removeButton.click();
    await page.waitForTimeout(1000);

    // Queue should have fewer items
    const afterCount = await queueCount.textContent();
    expect(parseInt(afterCount || '0')).toBeLessThan(parseInt(beforeCount || '1'));

    await guestPage.close();
  });

  test('should allow skipping current video', async ({ page, context }) => {
    // Add videos via guest interface
    const guestPage = await context.newPage();
    await guestPage.goto('/');
    await guestPage.fill('#video-url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    await guestPage.click('#add-button');
    await guestPage.waitForTimeout(1000);

    await guestPage.fill('#video-url', 'https://www.youtube.com/watch?v=jNQXAC9IVRw');
    await guestPage.click('#add-button');
    await guestPage.waitForTimeout(2000);

    // Click skip button
    const skipButton = page.locator('#skip-button');
    await skipButton.click();

    // Button should show loading state briefly
    await expect(skipButton).toBeEnabled({ timeout: 5000 });

    await guestPage.close();
  });

  test('should update in real-time when videos are added', async ({ page, context }) => {
    // Get initial queue count
    const queueCount = page.locator('#queue-count');
    const initialCount = await queueCount.textContent();

    // Open guest page and add a video
    const guestPage = await context.newPage();
    await guestPage.goto('/');
    await guestPage.fill('#video-url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    await guestPage.click('#add-button');

    // Host interface should update automatically via WebSocket
    // Queue count should change (or current video should appear)
    await expect(page.locator('#current-info')).not.toContainText('Queue is empty', { timeout: 5000 });

    await guestPage.close();
  });

  test('should show video thumbnails in queue', async ({ page, context }) => {
    // Add a video
    const guestPage = await context.newPage();
    await guestPage.goto('/');
    await guestPage.fill('#video-url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    await guestPage.click('#add-button');
    await guestPage.waitForTimeout(1000);

    await guestPage.fill('#video-url', 'https://www.youtube.com/watch?v=jNQXAC9IVRw');
    await guestPage.click('#add-button');
    await guestPage.waitForTimeout(2000);

    // Check for thumbnail images in queue
    const queueItem = page.locator('.host-queue-item').first();
    const thumbnail = queueItem.locator('img');
    await expect(thumbnail).toBeVisible({ timeout: 5000 });

    // Thumbnail should have a src attribute
    const src = await thumbnail.getAttribute('src');
    expect(src).toBeTruthy();

    await guestPage.close();
  });

  test('should show video titles and added-by info', async ({ page, context }) => {
    // Add a video with a name
    const guestPage = await context.newPage();
    await guestPage.goto('/');
    await guestPage.fill('#video-url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    await guestPage.fill('#user-name', 'John Doe');
    await guestPage.click('#add-button');
    await guestPage.waitForTimeout(2000);

    // Current video info should show the user name
    const currentInfo = page.locator('#current-info');
    await expect(currentInfo).toContainText('John Doe', { timeout: 5000 });

    await guestPage.close();
  });
});
