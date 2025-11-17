from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VideoItem(BaseModel):
    """Represents a video in the queue"""
    id: str = Field(..., description="Unique ID for this queue entry")
    video_id: str = Field(..., description="YouTube video ID")
    url: str = Field(..., description="Full YouTube URL")
    title: Optional[str] = Field(None, description="Video title")
    thumbnail: Optional[str] = Field(None, description="Video thumbnail URL")
    duration: Optional[int] = Field(None, description="Video duration in seconds")
    added_by: str = Field(default="Guest", description="User who added the video")
    added_at: datetime = Field(default_factory=datetime.now, description="Timestamp when added")


class AddVideoRequest(BaseModel):
    """Request to add a video to the queue"""
    url: str = Field(..., description="YouTube video URL")
    added_by: str = Field(default="Guest", description="User who added the video")


class QueueResponse(BaseModel):
    """Response containing the current queue state"""
    queue: list[VideoItem]
    current_video: Optional[VideoItem] = None
    total_videos: int


class HostCommand(BaseModel):
    """Commands from the host to control playback"""
    action: str = Field(..., description="Action to perform: skip, remove, reorder")
    video_id: Optional[str] = Field(None, description="ID of video to act on")
    new_position: Optional[int] = Field(None, description="New position for reorder")
