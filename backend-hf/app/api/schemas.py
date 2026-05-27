# app/api/schemas.py
from pydantic import BaseModel, Field

class GenerationResponse(BaseModel):
    status: str = Field(..., description="Current status of the compilation pipeline (completed/failed)")
    video_url: str = Field(..., description="Direct access HTTP URL path to download or stream the .mp4 file")
    message: str = Field(..., description="Summary message of the compilation results")