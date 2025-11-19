# 🎉 YouTube Party

A locally hosted web application for sharing YouTube videos with friends on the same network. Perfect for parties, gatherings, or just hanging out!

## Features

- 🎵 **Shared Queue**: Everyone on the network can add videos to a shared queue
- 📺 **10-Foot Interface**: Host view optimized for TVs and projectors
- 📱 **Mobile Friendly**: Guest interface works great on phones and tablets
- 🔄 **Real-Time Updates**: WebSocket-powered live queue synchronization
- 🎮 **Host Controls**: Skip videos, remove from queue, and manage playback
- 🛰️ **Embed-Restriction Bypass**: Host playback calls YouTube's internal `youtubei` API and uses an HLS player so even "Playback on other websites disabled" videos keep working
- 📊 **QR Code Access**: Easy mobile connection via QR code
- 🚀 **Zero Configuration**: No API keys or external services required
- 💾 **Queue Persistence**: Queue survives server restarts

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ (for Vite dev server)
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- [just](https://github.com/casey/just) (optional, for convenient commands)
- Modern web browser with JavaScript enabled

**Installing just (optional but recommended):**
```bash
# macOS
brew install just

# Linux
cargo install just

# Or download from https://github.com/casey/just/releases
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-party.git
cd youtube-party
```

2. Install backend dependencies:
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

### Running the Application

**Option 1: Using just (recommended)**
```bash
# Start both backend and frontend dev servers
just dev

# Or start individually
just backend    # Start backend only
just frontend   # Start frontend only
```

**Option 2: Manual start**
```bash
# Terminal 1 - Start backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Start frontend (for development with HMR)
cd frontend && npm run dev
```

**Option 3: Production mode (single server)**
```bash
python backend/main.py
```

### Access the Application

**Development mode (with Vite):**
- **Guest Interface**: `http://localhost:3000`
- **Host Interface**: `http://localhost:3000/host.html`

**Production mode:**
- **Guest Interface**: `http://YOUR_IP:8000`
- **Host Interface**: `http://YOUR_IP:8000/host`

The server will display your local IP address and access URLs when it starts.

## Usage

### For Hosts (TV/Projector Display)

1. Open the host interface at `http://YOUR_IP:8000/host`
2. The YouTube player will appear with the queue sidebar
3. Share your IP address or QR code with guests
4. Control playback with the "Skip Video" button
5. Remove videos from the queue using the "Remove" button

**Host Interface Features:**
- Large, readable text optimized for 10-foot viewing
- Embedded YouTube player with auto-progression
- Real-time queue updates
- QR code for easy guest access
- Current video information display

### For Guests (Phone/Tablet/Computer)

1. Connect to the same WiFi network as the host
2. Open `http://HOST_IP:8000` in your browser (or scan QR code)
3. Paste a YouTube URL in the input field
4. Optionally enter your name
5. Click "Add to Queue"

**Guest Interface Features:**
- Simple, clean interface for adding videos
- View current playing video
- See upcoming queue
- Works on any device with a browser

## Architecture

### Backend (Python/FastAPI)

- **FastAPI**: High-performance async web framework
- **WebSockets**: Real-time bidirectional communication
- **Queue Manager**: In-memory queue with JSON persistence
- **YouTube API**: Metadata fetching via oEmbed (no API key needed)

### Frontend (Vanilla JavaScript)

- **YouTube IFrame API**: Embedded player on host interface
- **WebSocket Client**: Real-time queue updates
- **Responsive Design**: Adapts to different screen sizes
- **10-Foot UI**: Optimized for TV viewing distance

### File Structure

```
youtube-party/
├── backend/
│   ├── main.py              # FastAPI app and WebSocket server
│   ├── models.py            # Pydantic data models
│   ├── queue_manager.py     # Queue state management
│   └── youtube_api.py       # Video validation and metadata
├── frontend/
│   ├── index.html           # Guest interface
│   ├── host.html            # Host interface (10-foot)
│   ├── package.json         # Frontend dependencies
│   ├── vite.config.js       # Vite configuration
│   └── static/
│       ├── css/
│       │   └── styles.css   # Styling for both interfaces
│       └── js/
│           └── app.js       # Client-side logic
├── pyproject.toml           # Python dependencies (uv)
├── uv.lock                  # Lockfile for reproducible builds
├── justfile                 # Task runner commands
├── CLAUDE.md                # Developer guidance for Claude Code
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## API Endpoints

### REST API

- `GET /` - Guest interface
- `GET /host` - Host interface
- `GET /api/queue` - Get current queue state
- `POST /api/queue` - Add video to queue
- `DELETE /api/queue/{item_id}` - Remove video from queue
- `POST /api/queue/next` - Get next video (auto-removes from queue)
- `POST /api/queue/skip` - Skip current video
- `GET /api/info` - Get server information (IP, port, URLs)
- `GET /api/qrcode` - Generate QR code for guest access

### WebSocket

- `WS /ws` - WebSocket connection for real-time updates
  - Sends `queue_update` messages when queue changes
  - Includes current video and full queue state

## Configuration

### Port Change

To run on a different port, modify `backend/main.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=YOUR_PORT)
```

### Queue Persistence

The queue is automatically saved to `queue_state.json` and restored on server restart. To disable persistence, modify `queue_manager.py`.

## Supported YouTube URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://m.youtube.com/watch?v=VIDEO_ID`

## Troubleshooting

### Videos Won't Play

- Ensure you're not running in a restricted environment
- YouTube IFrame API requires a production-like setup
- Some videos may be restricted from embedding

### Can't Connect from Other Devices

- Ensure all devices are on the same network
- Check firewall settings (port 8000 must be open)
- Try using the explicit IP address instead of localhost

### WebSocket Disconnects

- The app automatically reconnects every 3 seconds
- Check network stability
- Ensure no proxy or firewall is blocking WebSocket connections

## Development

### Running in Development Mode

The project uses Vite for frontend development with Hot Module Replacement (HMR) for faster iteration:

```bash
# Using just (recommended)
just dev

# Or manually
# Terminal 1: Backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

Access the app at `http://localhost:3000` (Vite proxies API requests to backend).

### Available Just Commands

```bash
just --list              # Show all available commands
just install            # Install all dependencies
just dev                # Start both backend and frontend
just backend            # Start backend only
just frontend           # Start frontend only
just clean              # Clean build artifacts and caches
just format             # Format code
just test               # Run tests
```

### Project Dependencies

**Backend (Python):**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `websockets` - WebSocket support
- `httpx` - HTTP client for YouTube API
- `pydantic` - Data validation
- `qrcode` - QR code generation

**Frontend (Node.js):**
- `vite` - Dev server with HMR

## Inspiration

This project combines ideas from:
- [crowd-q](https://github.com/tsdiokno/crowd-q) - Local hosting and shared queue concept
- [songup](https://github.com/motz0815/songup) - Clean UI and QR code access

## License

MIT License - feel free to use and modify!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Future Enhancements

- [ ] Search YouTube directly from the interface
- [ ] Voting system for queue ordering
- [ ] Playlist import/export
- [ ] User authentication for host controls
- [ ] Video preview before adding
- [ ] Dark/light theme toggle
- [ ] Queue history and statistics
- [ ] Support for other video platforms

---

Made with ❤️ for bringing people together through music and videos!
