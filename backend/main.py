from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
import qrcode
import io
import socket

from backend.models import AddVideoRequest, QueueResponse, HostCommand, VideoItem
from backend.queue_manager import QueueManager
from backend.youtube_api import (
    validate_video_url,
    extract_video_id,
    is_playlist_url,
    extract_playlist_id,
    fetch_playlist_videos,
    fetch_video_metadata
)

app = FastAPI(title="YouTube Party", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize queue manager
queue_manager = QueueManager()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.remove(conn)


manager = ConnectionManager()


# Helper function to get local IP
def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


# Helper to broadcast queue updates
async def broadcast_queue_update():
    """Send queue update to all connected clients"""
    queue_data = {
        "type": "queue_update",
        "queue": [v.model_dump(mode='json') for v in queue_manager.get_queue()],
        "current_video": queue_manager.get_current().model_dump(mode='json') if queue_manager.get_current() else None,
        "total_videos": len(queue_manager.get_queue())
    }
    await manager.broadcast(queue_data)


# REST API Endpoints

@app.get("/")
async def root():
    """Serve the guest interface"""
    return FileResponse("frontend/index.html")


@app.get("/host")
async def host():
    """Serve the host interface"""
    return FileResponse("frontend/host.html")


@app.get("/api/queue", response_model=QueueResponse)
async def get_queue():
    """Get the current queue state"""
    return QueueResponse(
        queue=queue_manager.get_queue(),
        current_video=queue_manager.get_current(),
        total_videos=len(queue_manager.get_queue())
    )


@app.post("/api/queue")
async def add_to_queue(request: AddVideoRequest):
    """Add a video or playlist to the queue"""

    # Check if this is a playlist URL
    if is_playlist_url(request.url):
        playlist_id = extract_playlist_id(request.url)

        if not playlist_id:
            raise HTTPException(status_code=400, detail="Invalid playlist URL")

        # Fetch all video IDs from the playlist
        video_ids = await fetch_playlist_videos(playlist_id, max_videos=50)

        if not video_ids:
            raise HTTPException(status_code=400, detail="Could not fetch videos from playlist or playlist is empty")

        # Add each video to the queue
        added_videos = []
        skipped_videos = []

        for video_id in video_ids:
            # Check for duplicates
            if queue_manager.check_duplicate(video_id):
                skipped_videos.append(video_id)
                continue

            # Fetch metadata for this video
            title, thumbnail, _ = await fetch_video_metadata(video_id)

            # Add to queue
            video_item = queue_manager.add_video(
                video_id=video_id,
                url=f"https://www.youtube.com/watch?v={video_id}",
                title=title,
                thumbnail=thumbnail,
                added_by=request.added_by
            )
            added_videos.append(video_item)

        # Broadcast update
        await broadcast_queue_update()

        return {
            "success": True,
            "playlist": True,
            "added_count": len(added_videos),
            "skipped_count": len(skipped_videos),
            "total_count": len(video_ids),
            "videos": [v.model_dump(mode='json') for v in added_videos]
        }

    else:
        # Original single video logic
        # Validate and extract video information
        is_valid, video_id, title, thumbnail = await validate_video_url(request.url)

        if not is_valid or not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL or video not found")

        # Check for duplicates
        if queue_manager.check_duplicate(video_id):
            raise HTTPException(status_code=409, detail="Video already in queue")

        # Add to queue
        video_item = queue_manager.add_video(
            video_id=video_id,
            url=request.url,
            title=title,
            thumbnail=thumbnail,
            added_by=request.added_by
        )

        # Broadcast update
        await broadcast_queue_update()

        return {"success": True, "video": video_item.model_dump(mode='json')}


@app.delete("/api/queue/{item_id}")
async def remove_from_queue(item_id: str):
    """Remove a video from the queue"""
    success = queue_manager.remove_video(item_id)

    if not success:
        raise HTTPException(status_code=404, detail="Video not found in queue")

    await broadcast_queue_update()
    return {"success": True}


@app.post("/api/queue/next")
async def get_next():
    """Get the next video (host only)"""
    next_video = queue_manager.get_next_video()

    await broadcast_queue_update()

    if next_video:
        return {"success": True, "video": next_video.model_dump(mode='json')}
    else:
        return {"success": True, "video": None, "message": "Queue is empty"}


@app.post("/api/queue/skip")
async def skip_current():
    """Skip the current video (host only)"""
    next_video = queue_manager.skip_current()

    await broadcast_queue_update()

    return {"success": True, "next_video": next_video.model_dump(mode='json') if next_video else None}


@app.post("/api/queue/reorder")
async def reorder_queue(item_id: str, new_position: int):
    """Reorder a video in the queue"""
    success = queue_manager.reorder_video(item_id, new_position)

    if not success:
        raise HTTPException(status_code=404, detail="Video not found in queue")

    await broadcast_queue_update()
    return {"success": True}


@app.get("/api/info")
async def get_info():
    """Get server information"""
    local_ip = get_local_ip()
    return {
        "ip": local_ip,
        "port": 8000,
        "url": f"http://{local_ip}:8000",
        "host_url": f"http://{local_ip}:8000/host"
    }


@app.get("/api/qrcode")
async def get_qrcode():
    """Generate a QR code for easy mobile access"""
    local_ip = get_local_ip()
    url = f"http://{local_ip}:8000"

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save to bytes
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return Response(content=buf.getvalue(), media_type="image/png")


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)

    try:
        # Send initial queue state
        await websocket.send_json({
            "type": "queue_update",
            "queue": [v.model_dump(mode='json') for v in queue_manager.get_queue()],
            "current_video": queue_manager.get_current().model_dump(mode='json') if queue_manager.get_current() else None,
            "total_videos": len(queue_manager.get_queue())
        })

        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            # Echo back (can be used for ping/pong)
            await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🎉 YouTube Party Server Starting...")
    print("=" * 60)
    local_ip = get_local_ip()
    print(f"\n📱 Guest Interface: http://{local_ip}:8000")
    print(f"🖥️  Host Interface:  http://{local_ip}:8000/host")
    print(f"\n📱 Scan QR code at: http://{local_ip}:8000/api/qrcode\n")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
