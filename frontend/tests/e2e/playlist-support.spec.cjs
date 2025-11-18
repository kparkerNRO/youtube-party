// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Playlist Support', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('YouTube Party');
  });

  test('should add a playlist to the queue', async ({ page }) => {
    // Use a small test playlist
    const playlistUrl = 'https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf';

    // Fill in the form
    await page.fill('#video-url', playlistUrl);
    await page.fill('#user-name', 'Playlist Tester');

    // Submit the form
    await page.click('#add-button');

    // Wait for success message indicating playlist was added
    // The message should mention how many videos were added
    await expect(page.locator('#status-message')).toContainText('Playlist added!', { timeout: 10000 });
    await expect(page.locator('#status-message')).toContainText('added to queue', { timeout: 10000 });
  });

  test('should show count of videos added from playlist', async ({ page }) => {
    const playlistUrl = 'https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf';

    await page.fill('#video-url', playlistUrl);
    await page.click('#add-button');

    // Wait for the success message
    const statusMessage = page.locator('#status-message');
    await expect(statusMessage).toContainText('Playlist added!', { timeout: 10000 });

    // Should show number of videos added (this playlist has 2 videos)
    await expect(statusMessage).toContainText('video(s) added to queue');
  });

  test('should handle playlist URL with video parameter', async ({ page }) => {
    // URL that has both a video and a playlist
    const playlistUrl = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf';

    await page.fill('#video-url', playlistUrl);
    await page.click('#add-button');

    // Should add the entire playlist, not just the single video
    await expect(page.locator('#status-message')).toContainText('Playlist added!', { timeout: 10000 });
  });

  test('should update queue count after adding playlist', async ({ page }) => {
    const playlistUrl = 'https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf';

    // Get initial queue count
    const queueCount = page.locator('#queue-count');
    const initialCount = parseInt(await queueCount.textContent() || '0');

    // Add playlist
    await page.fill('#video-url', playlistUrl);
    await page.click('#add-button');

    // Wait for success
    await expect(page.locator('#status-message')).toContainText('Playlist added!', { timeout: 10000 });

    // Queue count should increase (this test playlist has 2 videos, but one becomes current)
    await expect(queueCount).not.toContainText(initialCount.toString(), { timeout: 5000 });
  });

  test('should show skipped count if playlist contains duplicates', async ({ page }) => {
    const playlistUrl = 'https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf';

    // Add playlist first time
    await page.fill('#video-url', playlistUrl);
    await page.click('#add-button');
    await expect(page.locator('#status-message')).toContainText('Playlist added!', { timeout: 10000 });

    // Wait a bit for the queue to update
    await page.waitForTimeout(2000);

    // Try to add the same playlist again
    await page.fill('#video-url', playlistUrl);
    await page.click('#add-button');

    // Should indicate that videos were skipped because they're already in queue
    await expect(page.locator('#status-message')).toContainText('already in queue', { timeout: 10000 });
  });

  test('should clear input after playlist is added successfully', async ({ page }) => {
    const playlistUrl = 'https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf';

    await page.fill('#video-url', playlistUrl);
    await page.click('#add-button');

    // Wait for success
    await expect(page.locator('#status-message')).toContainText('Playlist added!', { timeout: 10000 });

    // Input should be cleared
    await expect(page.locator('#video-url')).toHaveValue('');
  });

  test('should handle invalid playlist URL', async ({ page }) => {
    // Use an invalid or non-existent playlist ID
    const invalidPlaylistUrl = 'https://www.youtube.com/playlist?list=INVALID123456';

    await page.fill('#video-url', invalidPlaylistUrl);
    await page.click('#add-button');

    // Should show error message
    await expect(page.locator('#status-message')).toContainText('Error:', { timeout: 10000 });
  });

  test('placeholder text should mention playlist support', async ({ page }) => {
    const urlInput = page.locator('#video-url');
    const placeholder = await urlInput.getAttribute('placeholder');

    // Check that placeholder mentions playlists
    expect(placeholder?.toLowerCase()).toContain('playlist');
  });

  test('header should mention playlist support', async ({ page }) => {
    // Check that the interface mentions playlist support
    const heading = page.locator('h2').first();
    await expect(heading).toContainText('Playlist');
  });
});
