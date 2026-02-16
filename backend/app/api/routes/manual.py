"""
Manual strategy endpoint - dish list input without image.
"""

from typing import List, Optional

from fastapi import APIRouter

from app.agents.pipeline import run_pipeline_manual
from app.models.schemas import AnalyzeRequest, ManualDishInput

router = APIRouter()


@router.post("/strategy/manual", response_model=dict)
async def manual_strategy(request: AnalyzeRequest):
    """
    Generate eating strategy from manual dish list (no image).

    - **dishes**: List of dish names with optional estimated grams
    - **goal**: fat_loss | muscle_gain | blood_sugar | enjoyment_first
    - **calorie_limit**: Optional max calories
    - **allergies**: Allergens to avoid
    - **dietary_filters**: halal, vegan, vegetarian
    """
    dishes = [
        {
            "name": d.name,
            "estimated_grams": d.estimated_grams,
            "cooking_method": d.cooking_method,
        }
        for d in request.dishes
    ]
    result = await run_pipeline_manual(
        dishes=dishes,
        goal=request.goal,
        calorie_limit=request.calorie_limit,
        allergies=request.allergies or [],
        dietary_filters=request.dietary_filters or [],
    )
    return result
