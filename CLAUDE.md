# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**For development with Vite (recommended for frontend debugging):**

1. Start the backend server:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

2. In a separate terminal, start the Vite dev server:
```bash
cd frontend
npm run dev
```

Then access:
- Guest interface: http://localhost:3000/
- Host interface: http://localhost:3000/host.html

**For production mode (single server):**
```bash
python backend/main.py
# or
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Install dependencies:**
```bash
# Backend
uv sync

# Frontend
cd frontend
npm install
```

## Architecture Overview

This is a YouTube Party web application that enables shared video queuing across local networks. The architecture follows a clean separation between backend API and frontend interfaces.

### Backend (FastAPI)
- **main.py**: Core FastAPI application with WebSocket support for real-time updates
- **queue_manager.py**: In-memory queue management with JSON persistence to `queue_state.json`
- **youtube_api.py**: Video validation and metadata extraction via YouTube oEmbed API
- **models.py**: Pydantic data models for API contracts

### Frontend (Vanilla JS)
- **host.html**: 10-foot TV interface with YouTube player and queue controls
- **index.html**: Mobile-friendly guest interface for adding videos
- **static/**: CSS and JavaScript assets

### Key Design Patterns
- **WebSocket Broadcasting**: Real-time queue synchronization across all connected clients
- **Dual Interface Design**: Separate UIs optimized for different viewing distances (10-foot vs mobile)
- **State Persistence**: Queue survives server restarts via JSON serialization
- **No External APIs**: Uses YouTube oEmbed for metadata without requiring API keys

### Data Flow
1. Guests add videos via REST API (`POST /api/queue`)
2. Queue manager validates and stores video metadata
3. WebSocket broadcasts queue updates to all connected clients
4. Host interface controls playback and queue management
5. State automatically persists to disk on all changes

### WebSocket Events
- `queue_update`: Sent when queue state changes, includes full queue and current video
- Connection management handles auto-reconnection on disconnects

### URL Patterns
- `/` - Guest interface
- `/host` - Host interface  
- `/api/*` - REST API endpoints
- `/ws` - WebSocket endpoint
- `/static/*` - Static assets

The codebase uses modern Python patterns with type hints, async/await, and Pydantic for data validation.