from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.models import User
from app.api import deps

router = APIRouter()

@router.get("/")
async def health_check(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Health check endpoint.
    """
    return {"status": "healthy", "user": current_user.email} 