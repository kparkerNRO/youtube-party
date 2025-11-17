import uuid
import json
from typing import Optional, List
from datetime import datetime
from pathlib import Path
from backend.models import VideoItem


class QueueManager:
    """Manages the video queue state"""

    def __init__(self, persist_file: str = "queue_state.json"):
        self.queue: List[VideoItem] = []
        self.current_video: Optional[VideoItem] = None
        self.persist_file = Path(persist_file)
        self.load_state()

    def add_video(
        self,
        video_id: str,
        url: str,
        title: Optional[str] = None,
        thumbnail: Optional[str] = None,
        duration: Optional[int] = None,
        added_by: str = "Guest"
    ) -> VideoItem:
        """Add a video to the queue"""
        video_item = VideoItem(
            id=str(uuid.uuid4()),
            video_id=video_id,
            url=url,
            title=title or f"Video {video_id}",
            thumbnail=thumbnail,
            duration=duration,
            added_by=added_by,
            added_at=datetime.now()
        )

        self.queue.append(video_item)
        self.save_state()
        return video_item

    def remove_video(self, item_id: str) -> bool:
        """Remove a video from the queue by its ID"""
        original_length = len(self.queue)
        self.queue = [v for v in self.queue if v.id != item_id]

        if len(self.queue) < original_length:
            self.save_state()
            return True
        return False

    def get_next_video(self) -> Optional[VideoItem]:
        """Get and remove the next video from the queue"""
        if not self.queue:
            self.current_video = None
            self.save_state()
            return None

        next_video = self.queue.pop(0)
        self.current_video = next_video
        self.save_state()
        return next_video

    def skip_current(self) -> Optional[VideoItem]:
        """Skip the current video and get the next one"""
        return self.get_next_video()

    def get_queue(self) -> List[VideoItem]:
        """Get the current queue"""
        return self.queue.copy()

    def get_current(self) -> Optional[VideoItem]:
        """Get the currently playing video"""
        return self.current_video

    def reorder_video(self, item_id: str, new_position: int) -> bool:
        """Move a video to a new position in the queue"""
        video = None
        old_index = None

        # Find the video
        for i, v in enumerate(self.queue):
            if v.id == item_id:
                video = v
                old_index = i
                break

        if video is None or old_index is None:
            return False

        # Remove from old position
        self.queue.pop(old_index)

        # Insert at new position (clamp to valid range)
        new_position = max(0, min(new_position, len(self.queue)))
        self.queue.insert(new_position, video)

        self.save_state()
        return True

    def clear_queue(self):
        """Clear all videos from the queue"""
        self.queue = []
        self.current_video = None
        self.save_state()

    def check_duplicate(self, video_id: str) -> bool:
        """Check if a video is already in the queue"""
        return any(v.video_id == video_id for v in self.queue)

    def save_state(self):
        """Save queue state to disk"""
        try:
            state = {
                "queue": [v.model_dump(mode='json') for v in self.queue],
                "current_video": self.current_video.model_dump(mode='json') if self.current_video else None
            }
            self.persist_file.write_text(json.dumps(state, indent=2, default=str))
        except Exception as e:
            print(f"Error saving queue state: {e}")

    def load_state(self):
        """Load queue state from disk"""
        try:
            if self.persist_file.exists():
                state = json.loads(self.persist_file.read_text())
                self.queue = [VideoItem(**v) for v in state.get("queue", [])]
                current = state.get("current_video")
                self.current_video = VideoItem(**current) if current else None
                print(f"Loaded queue state: {len(self.queue)} videos in queue")
        except Exception as e:
            print(f"Error loading queue state: {e}")
            self.queue = []
            self.current_video = None
