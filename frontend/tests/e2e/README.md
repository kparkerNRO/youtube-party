# End-to-End Tests

This directory contains automated end-to-end tests for the YouTube Party application using Playwright.

## Test Files

- **guest-interface.spec.js** - Tests for the guest interface (adding videos, viewing queue)
- **playlist-support.spec.js** - Tests for playlist functionality
- **host-interface.spec.js** - Tests for the host interface (playback control, queue management)

## Running Tests

### Prerequisites

Ensure you have the dependencies installed:

```bash
cd frontend
npm install
```

### Run All Tests

```bash
npm test
```

### Run Tests in UI Mode (Interactive)

```bash
npm run test:ui
```

### Run Tests in Headed Mode (See Browser)

```bash
npm run test:headed
```

### View Test Report

After running tests, view the HTML report:

```bash
npm run test:report
```

## What Gets Tested

### Guest Interface
- Page layout and UI elements
- Adding single videos (various URL formats)
- YouTube Shorts URL support
- youtu.be short URL support
- Error handling for invalid URLs
- Duplicate video detection
- Queue display and updates
- Default "Guest" name handling
- Form validation

### Playlist Support
- Adding playlists to queue
- Playlist URL detection
- Mixed video + playlist URLs
- Showing count of added videos
- Duplicate handling in playlists
- Queue updates after playlist addition
- Error handling for invalid playlists

### Host Interface
- Page layout and control elements
- YouTube player embedding
- QR code generation
- Real-time queue updates via WebSocket
- Removing videos from queue
- Skipping current video
- Displaying video thumbnails and metadata
- Position numbering in queue

## Test Configuration

Tests are configured to:
- Run against `http://localhost:3000` (Vite dev server)
- Automatically start backend (`uvicorn`) and frontend (`npm run dev`) servers
- Reuse existing servers if already running
- Take screenshots on failure
- Generate HTML reports
- Run in Chromium browser

Configuration can be modified in `playwright.config.js`.

## Continuous Integration

Tests are designed to run in CI environments:
- `CI=true npm test` will run in headless mode with retries
- Screenshots and traces are captured for debugging failures
