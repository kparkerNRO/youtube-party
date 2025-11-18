// ===== WEBSOCKET CONNECTION =====
let ws = null;
let reconnectInterval = null;

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('WebSocket connected');
        if (reconnectInterval) {
            clearInterval(reconnectInterval);
            reconnectInterval = null;
        }
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected');
        // Attempt to reconnect every 3 seconds
        if (!reconnectInterval) {
            reconnectInterval = setInterval(connectWebSocket, 3000);
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

function handleWebSocketMessage(data) {
    if (data.type === 'queue_update') {
        console.log('Queue update received:', data);
        updateQueueDisplay(data.queue, data.current_video);

        // If this is the host page, handle video playback
        if (playerReady && hostVideoElement) {
            if (data.current_video) {
                const newVideoId = data.current_video.video_id;
                if (newVideoId !== currentVideoId) {
                    console.log('Loading playable stream for', newVideoId);
                    loadVideo(newVideoId);
                }
            } else if (currentVideoId) {
                console.log('Queue empty, stopping host player');
                stopPlayback();
            }
        }
    }
}

// ===== API CALLS =====
async function fetchQueue() {
    try {
        const response = await fetch('/api/queue');
        const data = await response.json();
        updateQueueDisplay(data.queue, data.current_video);
    } catch (error) {
        console.error('Error fetching queue:', error);
    }
}

async function addVideo(url, addedBy = 'Guest') {
    try {
        const response = await fetch('/api/queue', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url, added_by: addedBy }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add video');
        }

        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function removeVideo(itemId) {
    try {
        const response = await fetch(`/api/queue/${itemId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            throw new Error('Failed to remove video');
        }

        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function skipCurrent() {
    try {
        const response = await fetch('/api/queue/skip', {
            method: 'POST',
        });

        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function getNextVideo() {
    try {
        const response = await fetch('/api/queue/next', {
            method: 'POST',
        });

        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function getServerInfo() {
    try {
        const response = await fetch('/api/info');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching server info:', error);
        return null;
    }
}

// ===== QUEUE DISPLAY =====
function updateQueueDisplay(queue, currentVideo) {
    // Update current video (if element exists - for guest view)
    const nowPlayingEl = document.getElementById('now-playing');
    if (nowPlayingEl) {
        if (currentVideo) {
            nowPlayingEl.innerHTML = `
                <h3>Now Playing</h3>
                <div class="video-info">
                    <img src="${currentVideo.thumbnail || 'https://via.placeholder.com/120x90?text=No+Thumbnail'}" alt="${currentVideo.title}">
                    <div class="details">
                        <h4>${currentVideo.title || 'Unknown Title'}</h4>
                        <p>Added by ${currentVideo.added_by}</p>
                    </div>
                </div>
            `;
        } else {
            nowPlayingEl.innerHTML = `
                <h3>Now Playing</h3>
                <p class="empty-queue">No video currently playing</p>
            `;
        }
    }

    // Update current info (for host view)
    const currentInfoEl = document.getElementById('current-info');
    if (currentInfoEl) {
        if (currentVideo) {
            currentInfoEl.innerHTML = `
                <h2>Now Playing</h2>
                <div class="video-title">${currentVideo.title || 'Unknown Title'}</div>
                <div class="added-by">Added by ${currentVideo.added_by}</div>
            `;
        } else {
            currentInfoEl.innerHTML = `
                <h2>Now Playing</h2>
                <div class="video-title">Queue is empty</div>
                <div class="added-by">Add videos to get started!</div>
            `;
        }
    }

    const hostVideoEl = document.getElementById('host-video');
    if (hostVideoEl) {
        if (currentVideo && currentVideo.thumbnail) {
            hostVideoEl.poster = currentVideo.thumbnail;
        } else {
            hostVideoEl.removeAttribute('poster');
        }
    }

    // Update queue list
    const queueListEl = document.getElementById('queue-list');
    if (queueListEl) {
        const isHost = queueListEl.classList.contains('host-queue-list');

        if (queue.length === 0) {
            queueListEl.innerHTML = `
                <div class="empty-queue">
                    <p>The queue is empty. Add some videos!</p>
                </div>
            `;
        } else {
            queueListEl.innerHTML = queue.map((video, index) => {
                if (isHost) {
                    return `
                        <div class="host-queue-item">
                            <div class="position">${index + 1}</div>
                            <img src="${video.thumbnail || 'https://via.placeholder.com/120x90?text=No+Thumbnail'}" alt="${video.title}">
                            <div class="info">
                                <h4>${video.title || 'Unknown Title'}</h4>
                                <p>Added by ${video.added_by}</p>
                            </div>
                            <button class="btn btn-danger btn-small btn-remove" onclick="handleRemove('${video.id}')">Remove</button>
                        </div>
                    `;
                } else {
                    return `
                        <div class="queue-item">
                            <div class="position">${index + 1}</div>
                            <img src="${video.thumbnail || 'https://via.placeholder.com/120x90?text=No+Thumbnail'}" alt="${video.title}">
                            <div class="info">
                                <h4>${video.title || 'Unknown Title'}</h4>
                                <p>Added by ${video.added_by}</p>
                            </div>
                        </div>
                    `;
                }
            }).join('');
        }
    }

    // Update queue count
    const queueCountEl = document.getElementById('queue-count');
    if (queueCountEl) {
        queueCountEl.textContent = queue.length;
    }
}

// ===== EVENT HANDLERS =====
async function handleAddVideo(event) {
    event.preventDefault();

    const urlInput = document.getElementById('video-url');
    const nameInput = document.getElementById('user-name');
    const addButton = document.getElementById('add-button');
    const statusEl = document.getElementById('status-message');

    const url = urlInput.value.trim();
    const name = nameInput.value.trim() || 'Guest';

    if (!url) {
        showStatus('Please enter a YouTube URL', 'error');
        return;
    }

    // Disable button and show loading
    addButton.disabled = true;
    addButton.textContent = 'Adding...';

    const result = await addVideo(url, name);

    // Re-enable button
    addButton.disabled = false;
    addButton.textContent = 'Add to Queue';

    if (result.success) {
        // Check if it's a playlist
        if (result.data.playlist) {
            const { added_count, skipped_count, total_count } = result.data;
            let message = `Playlist added! ${added_count} video(s) added to queue`;
            if (skipped_count > 0) {
                message += ` (${skipped_count} already in queue)`;
            }
            showStatus(message, 'success');
        } else {
            showStatus('Video added to queue!', 'success');
        }
        urlInput.value = '';
        urlInput.focus();
    } else {
        showStatus(`Error: ${result.error}`, 'error');
    }
}

async function handleRemove(itemId) {
    const result = await removeVideo(itemId);

    if (!result.success) {
        alert(`Error removing video: ${result.error}`);
    }
}

async function handleSkip() {
    const skipButton = document.getElementById('skip-button');
    if (skipButton) {
        skipButton.disabled = true;
        skipButton.textContent = 'Skipping...';
    }

    console.log('Skipping current video');
    const result = await skipCurrent();
    console.log('Skip result:', result);

    if (skipButton) {
        skipButton.disabled = false;
        skipButton.textContent = 'Skip Video';
    }

    // WebSocket will handle loading the next video automatically
    // No need to manually load it here
}

function showStatus(message, type) {
    const statusEl = document.getElementById('status-message');
    if (statusEl) {
        statusEl.textContent = message;
        statusEl.className = `status-message status-${type}`;
        statusEl.style.display = 'block';

        setTimeout(() => {
            statusEl.style.display = 'none';
        }, 5000);
    }
}

function showHostError(message) {
    const currentInfoEl = document.getElementById('current-info');
    if (currentInfoEl) {
        currentInfoEl.innerHTML = `
            <h2>Playback Error</h2>
            <div class="video-title">${message}</div>
            <div class="added-by">Try skipping to the next video.</div>
        `;
    }
}

// ===== HOST HLS PLAYER (HOST ONLY) =====
let hostVideoElement = null;
let hlsInstance = null;
let playerReady = false;
let currentVideoId = null;

function initHostPlayer() {
    hostVideoElement = document.getElementById('host-video');
    if (!hostVideoElement) {
        return;
    }

    playerReady = true;

    hostVideoElement.addEventListener('ended', () => {
        playNext();
    });

    hostVideoElement.addEventListener('error', (event) => {
        console.error('Playback error', event);
        showHostError('Playback error. Trying the next video...');
        playNext();
    });

    // Load whatever is currently playing
    fetch('/api/queue')
        .then((res) => res.json())
        .then((data) => {
            if (data.current_video) {
                currentVideoId = data.current_video.video_id;
                loadVideo(currentVideoId);
            }
        })
        .catch((error) => console.error('Failed to hydrate host player', error));
}

async function loadVideo(videoId) {
    if (!hostVideoElement || !playerReady) {
        return;
    }

    currentVideoId = videoId;

    try {
        const response = await fetch(`/api/player/${videoId}`);
        const payload = await response.json();

        if (!response.ok) {
            throw new Error(payload.detail || 'Failed to fetch stream info');
        }

        if (!payload.stream_url) {
            throw new Error('Playable stream missing from response');
        }

        attachStream(payload.stream_url);
        console.log('Loaded stream using client', payload.client_name, payload.client_version);
    } catch (error) {
        console.error('Unable to start playback', error);
        showHostError(error.message || 'Unable to load video');
    }
}

function attachStream(streamUrl) {
    if (!hostVideoElement) {
        return;
    }

    if (hlsInstance) {
        hlsInstance.destroy();
        hlsInstance = null;
    }

    if (window.Hls && window.Hls.isSupported()) {
        hlsInstance = new Hls({ enableWorker: true });
        hlsInstance.loadSource(streamUrl);
        hlsInstance.attachMedia(hostVideoElement);
        hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
            hostVideoElement.play().catch((error) => console.error('Autoplay blocked', error));
        });
        hlsInstance.on(Hls.Events.ERROR, (_, data) => {
            if (!data.fatal) {
                return;
            }

            if (data.type === Hls.ErrorTypes.NETWORK_ERROR) {
                console.warn('HLS network error, retrying load');
                hlsInstance.startLoad();
            } else {
                console.error('Fatal HLS error, destroying instance', data);
                hlsInstance.destroy();
                hlsInstance = null;
                showHostError('Stream error. Skipping to next video.');
                playNext();
            }
        });
    } else if (hostVideoElement.canPlayType('application/vnd.apple.mpegurl')) {
        hostVideoElement.src = streamUrl;
        hostVideoElement.addEventListener(
            'loadedmetadata',
            () => {
                hostVideoElement.play().catch((error) => console.error('Autoplay blocked', error));
            },
            { once: true },
        );
    } else {
        showHostError('HLS playback is not supported in this browser.');
    }
}

function stopPlayback() {
    if (hlsInstance) {
        hlsInstance.destroy();
        hlsInstance = null;
    }

    if (hostVideoElement) {
        hostVideoElement.pause();
        hostVideoElement.removeAttribute('src');
        hostVideoElement.load();
    }

    currentVideoId = null;
}

async function playNext() {
    const result = await getNextVideo();

    if (result.success && result.data.video) {
        loadVideo(result.data.video.video_id);
    } else {
        console.log('Queue is empty');
        stopPlayback();
    }
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', async () => {
    // Connect WebSocket
    connectWebSocket();

    // Fetch initial queue
    await fetchQueue();

    // Set up form handlers
    const addForm = document.getElementById('add-video-form');
    if (addForm) {
        addForm.addEventListener('submit', handleAddVideo);
    }

    const skipButton = document.getElementById('skip-button');
    if (skipButton) {
        skipButton.addEventListener('click', handleSkip);
    }

    // Load server info for connection display
    const serverInfo = await getServerInfo();
    if (serverInfo) {
        const urlEl = document.getElementById('server-url');
        if (urlEl) {
            urlEl.textContent = serverInfo.url;
        }

        const qrEl = document.getElementById('qr-code');
        if (qrEl) {
            qrEl.src = '/api/qrcode';
        }
    }

    if (document.getElementById('host-video')) {
        initHostPlayer();
    }
});

// Make functions globally available
window.handleRemove = handleRemove;
window.handleSkip = handleSkip;
