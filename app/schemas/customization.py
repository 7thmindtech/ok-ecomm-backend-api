from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, Literal
from datetime import datetime

# --- AI Image Generation Schemas ---

class AIGenerationRequest(BaseModel):
    prompt: str
    model: Literal["openai", "stabilityai", "deepai"] # Enforce allowed models
    # Add other potential parameters like negative_prompt, style_preset etc. if needed

class AIGenerationResponse(BaseModel):
    success: bool
    image_url: Optional[HttpUrl] = None # URL of the generated image in S3
    error: Optional[str] = None

# --- Product Customization Schemas ---

class CustomizationSaveRequest(BaseModel):
    product_id: int
    canvas_state: Optional[Dict[str, Any]] = None # e.g., Fabric.js JSON state
    final_image_data_url: str # Base64 encoded image data URL from canvas
    selected_attributes: Optional[Dict[str, Any]] = None # e.g., {"size": "M", "color": "#FF0000"}

class CustomizationSaveResponse(BaseModel):
    success: bool
    customization_id: Optional[int] = None
    rendered_image_url: Optional[HttpUrl] = None
    error: Optional[str] = None

# --- Schema for Reading Customization Data ---

class ProductCustomizationRead(BaseModel):
    id: int
    user_id: int
    product_id: int
    canvas_state: Optional[Dict[str, Any]] = None
    rendered_image_url: HttpUrl
    selected_attributes: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # Renamed from orm_mode
        # If using Pydantic v2+, use: from_attributes = True 