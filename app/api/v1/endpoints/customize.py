from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
import httpx
import logging
import os

from app import schemas, crud, models
from app.api import deps
from local_s3 import upload_customization_image_data # Import the new upload function
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# --- AI Image Generation Endpoint ---

async def generate_with_openai(prompt: str) -> bytes:
    """Generates image using OpenAI DALL-E 3 and returns image bytes."""
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "response_format": "b64_json" # Request base64 encoded image data
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client: # Increased timeout
            response = await client.post("https://api.openai.com/v1/images/generations", json=payload, headers=headers)
            response.raise_for_status() # Raise exception for bad status codes
            
            data = response.json()
            b64_data = data["data"][0]["b64_json"]
            image_bytes = base64.b64decode(b64_data)
            return image_bytes
            
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenAI API request failed: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"OpenAI API Error: {e.response.text}")
    except Exception as e:
        logger.error(f"Error during OpenAI image generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate image with OpenAI.")

async def generate_with_stabilityai(prompt: str) -> bytes:
    # Placeholder: Implement StabilityAI call
    api_key = settings.STABILITYAI_API_KEY
    if not api_key or api_key == "YOUR_STABILITYAI_API_KEY_HERE":
         raise HTTPException(status_code=501, detail="StabilityAI API key not configured or placeholder used.")
    # ... Actual API call logic ...
    logger.warning("StabilityAI generation not implemented yet.")
    raise HTTPException(status_code=501, detail="StabilityAI generation not implemented.")
    # return image_bytes

async def generate_with_deepai(prompt: str) -> bytes:
    # Placeholder: Implement DeepAI call
    api_key = settings.DEEPAI_API_KEY
    if not api_key or api_key == "YOUR_DEEPAI_API_KEY_HERE":
         raise HTTPException(status_code=501, detail="DeepAI API key not configured or placeholder used.")
    # ... Actual API call logic ...
    logger.warning("DeepAI generation not implemented yet.")
    raise HTTPException(status_code=501, detail="DeepAI generation not implemented.")
    # return image_bytes

@router.post("/generate-image", response_model=schemas.AIGenerationResponse)
async def generate_ai_image(
    request: schemas.AIGenerationRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Generates an image based on a prompt using the selected AI model.
    Uploads the generated image to S3 and returns its URL.
    """
    logger.info(f"User {current_user.id} requested AI image generation (Model: {request.model}) with prompt: '{request.prompt}'")
    
    try:
        image_bytes: bytes
        if request.model == "openai":
            image_bytes = await generate_with_openai(request.prompt)
        elif request.model == "stabilityai":
            image_bytes = await generate_with_stabilityai(request.prompt) # Placeholder call
        elif request.model == "deepai":
            image_bytes = await generate_with_deepai(request.prompt) # Placeholder call
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported AI model: {request.model}")

        # Assume product_id is needed for storage path - how to get this?
        # For now, let's use a placeholder or omit it if not strictly needed for the path
        # A better approach might be to associate generation with a temporary ID or session
        # before a product is selected, or pass product_id if available.
        # Using 0 as placeholder product_id for now.
        placeholder_product_id = 0 

        # Upload the generated image bytes to local S3
        image_url = await upload_customization_image_data(
            image_data=image_bytes,
            user_id=current_user.id,
            product_id=placeholder_product_id, # Use placeholder
            image_type=f"ai_{request.model}" 
        )

        return schemas.AIGenerationResponse(success=True, image_url=image_url)

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions directly (e.g., from API calls or unimplemented models)
        raise http_exc
    except Exception as e:
        logger.error(f"AI image generation failed for user {current_user.id}: {e}", exc_info=True)
        return schemas.AIGenerationResponse(success=False, error=f"An internal error occurred during image generation: {str(e)}")

# --- Product Customization Save Endpoint ---

@router.post("/save-customization", response_model=schemas.CustomizationSaveResponse)
async def save_product_customization(
    request: schemas.CustomizationSaveRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Saves a product customization: uploads the rendered image and stores details in the DB.
    Returns the ID and URL of the saved customization.
    """
    logger.info(f"User {current_user.id} attempting to save customization for product {request.product_id}")

    # Validate product exists and is customizable (optional but recommended)
    product = crud.product.get(db, id=request.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not product.is_customizable:
        raise HTTPException(status_code=400, detail="Product is not customizable")

    try:
        # Upload the rendered image (base64 data URL) to local S3
        rendered_image_url = await upload_customization_image_data(
            image_data=request.final_image_data_url,
            user_id=current_user.id,
            product_id=request.product_id,
            image_type="rendered"
        )

        # Create the customization record in the database
        db_customization = crud.create_product_customization(
            db=db,
            user_id=current_user.id,
            product_id=request.product_id,
            rendered_image_url=rendered_image_url,
            canvas_state=request.canvas_state,
            selected_attributes=request.selected_attributes
        )

        logger.info(f"Successfully saved customization {db_customization.id} for user {current_user.id}")
        return schemas.CustomizationSaveResponse(
            success=True, 
            customization_id=db_customization.id,
            rendered_image_url=rendered_image_url
        )

    except ValueError as ve:
         logger.error(f"Value error during customization save for user {current_user.id}: {ve}")
         raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to save customization for user {current_user.id}: {e}", exc_info=True)
        # Consider deleting the uploaded S3 image if DB save fails (optional cleanup)
        # await delete_file(rendered_image_url) # Need delete_file from local_s3
        raise HTTPException(status_code=500, detail=f"Failed to save customization: {str(e)}")

# --- Add endpoint to get customization details? (Optional) ---
# @router.get("/{customization_id}", response_model=schemas.ProductCustomizationRead)
# def read_customization(...):
#     # Fetch and return customization details
#     pass 