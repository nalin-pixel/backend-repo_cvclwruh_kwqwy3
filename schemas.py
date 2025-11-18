"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal
from datetime import datetime

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Video AI Clipper app schemas

class DetectedMoment(BaseModel):
    start_sec: float = Field(..., ge=0, description="Start time in seconds")
    end_sec: float = Field(..., ge=0, description="End time in seconds")
    label: str = Field(..., description="Short label for the moment")
    confidence: float = Field(0.8, ge=0, le=1, description="Confidence score")

class VideoJob(BaseModel):
    youtube_url: HttpUrl = Field(..., description="YouTube video URL")
    title: Optional[str] = Field(None, description="Video title")
    author: Optional[str] = Field(None, description="Channel/author")
    thumbnail_url: Optional[HttpUrl] = Field(None, description="Thumbnail image")
    status: Literal["pending", "analyzed", "rendered", "error"] = "pending"
    detected_moments: List[DetectedMoment] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class OverlayText(BaseModel):
    content: str
    position: Literal["top", "center", "bottom"] = "bottom"
    style: Literal["caption", "title", "subtitle", "emoji"] = "caption"

class ClipRequest(BaseModel):
    job_id: str = Field(..., description="ID of the analyzed video job")
    start_sec: float = Field(..., ge=0)
    end_sec: float = Field(..., ge=0)
    overlays: List[OverlayText] = Field(default_factory=list)
    animation: Literal["bounce", "fade", "slide", "pop"] = "bounce"
    emoji: Optional[str] = None

class ClipResult(BaseModel):
    job_id: str
    preview_url: Optional[str] = None
    start_sec: float
    end_sec: float
    overlays: List[OverlayText] = Field(default_factory=list)
    animation: str
    emoji: Optional[str] = None
    created_at: Optional[datetime] = None

