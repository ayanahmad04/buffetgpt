"""
Analyze endpoint - image/video upload for buffet analysis.
"""

from typing import List, Optional

from fastapi import APIRouter, File, Form, UploadFile

from app.agents.pipeline import run_pipeline
from app.models.schemas import StrategyResponse

router = APIRouter()


@router.post("/analyze", response_model=dict)
async def analyze_buffet(
    image: UploadFile = File(...),
    goal: str = Form("enjoyment_first"),
    calorie_limit: Optional[int] = Form(None),
    allergies: Optional[str] = Form(None),
    dietary_filters: Optional[str] = Form(None),
):
    """
    Analyze buffet image and return eating strategy.

    - **image**: Buffet photo (JPEG/PNG)
    - **goal**: fat_loss | muscle_gain | blood_sugar | enjoyment_first
    - **calorie_limit**: Optional max calories
    - **allergies**: Comma-separated allergens to avoid
    - **dietary_filters**: Comma-separated (halal, vegan, vegetarian)
    """
    image_bytes = await image.read()
    allergy_list = [a.strip() for a in allergies.split(",")] if allergies else []
    filter_list = [f.strip() for f in dietary_filters.split(",")] if dietary_filters else []

    result = await run_pipeline(
        image_bytes=image_bytes,
        goal=goal,
        calorie_limit=calorie_limit,
        allergies=allergy_list,
        dietary_filters=filter_list,
    )
    return result
