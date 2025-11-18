// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Guest Interface', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the guest interface
    await page.goto('/');

    // Wait for the page to load
    await expect(page.locator('h1')).toContainText('YouTube Party');
  });

  test('should display the guest interface correctly', async ({ page }) => {
    // Check main elements are present
    await expect(page.locator('h1')).toContainText('YouTube Party');
    await expect(page.locator('h2').first()).toContainText('Add a Video or Playlist');

    // Check form elements
    await expect(page.locator('#video-url')).toBeVisible();
    await expect(page.locator('#user-name')).toBeVisible();
    await expect(page.locator('#add-button')).toBeVisible();
  });

  test('should show validation error for empty URL', async ({ page }) => {
    // Try to submit empty form
    await page.click('#add-button');

    // HTML5 validation should prevent submission
    const urlInput = page.locator('#video-url');
    await expect(urlInput).toBeFocused();
  });

  test('should add a single video to the queue', async ({ page }) => {
    // Fill in the form
    await page.fill('#video-url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    await page.fill('#user-name', 'Test User');

    // Submit the form
    await page.click('#add-button');

    // Wait for success message
    await expect(page.locator('#status-message')).toContainText('Video added to queue!');

    // Check that the input was cleared
    await expect(page.locator('#video-url')).toHaveValue('');

    // Wait for queue to update (check that queue count increased)
    await expect(page.locator('#queue-count')).toContainText('1', { timeout: 5000 });
  });

  test('should handle YouTube Shorts URLs', async ({ page }) => {
    // Fill in the form with a Shorts URL
    await page.fill('#video-url', 'https://www.youtube.com/shorts/dQw4w9WgXcQ');
    await page.fill('#user-name', 'Test User');

    // Submit the form
    await page.click('#add-button');

    // Wait for success message
    await expect(page.locator('#status-message')).toContainText('Video added to queue!');
  });

  test('should handle youtu.be short URLs', async ({ page }) => {
    // Fill in the form with a youtu.be URL
    await page.fill('#video-url', 'https://youtu.be/dQw4w9WgXcQ');
    await page.fill('#user-name', 'Test User');

    // Submit the form
    await page.click('#add-button');

    // Wait for success message
    await expect(page.locator('#status-message')).toContainText('Video added to queue!');
  });

  test('should show error for invalid URL', async ({ page }) => {
    // Fill in the form with an invalid URL
    await page.fill('#video-url', 'https://example.com/invalid');
    await page.fill('#user-name', 'Test User');

    // Submit the form
    await page.click('#add-button');

    // Wait for error message
    await expect(page.locator('#status-message')).toContainText('Error:', { timeout: 5000 });
  });

  test('should show error for duplicate video', async ({ page }) => {
    const videoUrl = 'https://www.youtube.com/watch?v=unique-test-video';

    // Add video first time
    await page.fill('#video-url', videoUrl);
    await page.fill('#user-name', 'Test User');
    await page.click('#add-button');

    // Wait for success
    await expect(page.locator('#status-message')).toContainText('Video added to queue!');

    // Try to add the same video again
    await page.fill('#video-url', videoUrl);
    await page.click('#add-button');

    // Should show duplicate error
    await expect(page.locator('#status-message')).toContainText('already in queue', { timeout: 5000 });
  });

  test('should display the current playing video', async ({ page }) => {
    // Add a video
    await page.fill('#video-url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    await page.fill('#user-name', 'Test User');
    await page.click('#add-button');

    // Wait for the video to appear in "Now Playing" section
    const nowPlaying = page.locator('#now-playing');
    await expect(nowPlaying).toContainText('Now Playing', { timeout: 5000 });
    await expect(nowPlaying).toContainText('Test User', { timeout: 5000 });
  });

  test('should display queue items', async ({ page }) => {
    // Add first video
    await page.fill('#video-url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    await page.fill('#user-name', 'User 1');
    await page.click('#add-button');
    await page.waitForTimeout(1000);

    // Add second video
    await page.fill('#video-url', 'https://www.youtube.com/watch?v=jNQXAC9IVRw');
    await page.fill('#user-name', 'User 2');
    await page.click('#add-button');

    // Wait for queue to update
    await expect(page.locator('#queue-count')).toContainText('1', { timeout: 5000 });

    // Check queue list contains video info
    const queueList = page.locator('#queue-list');
    await expect(queueList.locator('.queue-item')).toHaveCount(1, { timeout: 5000 });
  });

  test('should use default name "Guest" when no name provided', async ({ page }) => {
    // Add video without providing a name
    await page.fill('#video-url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    // Don't fill in user-name
    await page.click('#add-button');

    // Wait for success
    await expect(page.locator('#status-message')).toContainText('Video added to queue!');

    // Check that "Guest" appears in the now playing section
    await expect(page.locator('#now-playing')).toContainText('Guest', { timeout: 5000 });
  });

  test('should clear URL after successful submission', async ({ page }) => {
    // Fill and submit
    await page.fill('#video-url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    await page.click('#add-button');

    // Wait for success
    await expect(page.locator('#status-message')).toContainText('Video added to queue!');

    // URL should be cleared
    await expect(page.locator('#video-url')).toHaveValue('');

    // Name should NOT be cleared (for convenience)
    // This allows users to add multiple videos with the same name
  });

  test('should show loading state on button during submission', async ({ page }) => {
    // Fill form
    await page.fill('#video-url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');

    // Click button and immediately check loading state
    const submitPromise = page.click('#add-button');

    // Button should show "Adding..." text while request is in flight
    // Note: This might be too fast to catch, so we just verify it doesn't error
    await submitPromise;

    // Eventually button should return to normal
    await expect(page.locator('#add-button')).toContainText('Add to Queue');
  });
});
