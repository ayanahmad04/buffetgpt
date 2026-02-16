"""
BuffetGPT Agent Pipeline - Orchestrates Vision → Nutrition → Stomach → Optimization → Strategy.
"""

from typing import Any, Dict, List, Optional

from app.agents.nutrition import NutritionAgent
from app.agents.optimization import GoalOptimizationAgent
from app.agents.stomach import StomachPhysicsAgent
from app.agents.strategy import StrategyPlanningAgent
from app.agents.vision import VisionAgent
from app.config import settings
from app.models.schemas import DetectedDish


def _detected_dish_from_manual(d: Dict) -> DetectedDish:
    """Convert manual dish dict to DetectedDish."""
    return DetectedDish(
        name=d["name"],
        confidence=0.9,
        estimated_grams=d.get("estimated_grams", 100),
        cooking_method=d.get("cooking_method"),
    )


async def run_pipeline(
    image_bytes: bytes,
    goal: str = "enjoyment_first",
    calorie_limit: Optional[int] = None,
    allergies: Optional[List[str]] = None,
    dietary_filters: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Full pipeline: image → vision → nutrition → stomach → optimization → strategy.
    """
    # 1. Vision Agent
    vision = VisionAgent(
        model_type=settings.VISION_MODEL,
        gemini_api_key=settings.GEMINI_API_KEY,
    )
    detected = vision.process(image_bytes)

    return _run_rest_of_pipeline(
        detected_dishes=detected,
        goal=goal,
        calorie_limit=calorie_limit,
        allergies=allergies or [],
        dietary_filters=dietary_filters or [],
    )


async def run_pipeline_manual(
    dishes: List[Dict],
    goal: str = "enjoyment_first",
    calorie_limit: Optional[int] = None,
    allergies: Optional[List[str]] = None,
    dietary_filters: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Pipeline from manual dish list (skip vision).
    """
    detected = [_detected_dish_from_manual(d) for d in dishes]

    return _run_rest_of_pipeline(
        detected_dishes=detected,
        goal=goal,
        calorie_limit=calorie_limit,
        allergies=allergies or [],
        dietary_filters=dietary_filters or [],
    )


def _run_rest_of_pipeline(
    detected_dishes: List[DetectedDish],
    goal: str,
    calorie_limit: Optional[int],
    allergies: List[str],
    dietary_filters: List[str],
) -> Dict[str, Any]:
    """Shared pipeline logic after detection."""
    if not detected_dishes:
        return _empty_response("No dishes detected.")

    # 2. Nutrition Agent
    nutrition = NutritionAgent()
    with_nutrition = nutrition.process(detected_dishes)

    # 3. Stomach Physics Agent
    stomach = StomachPhysicsAgent()
    with_stomach = stomach.process(with_nutrition)

    # 4. Goal Optimization Agent
    opt = GoalOptimizationAgent(
        calorie_limit=calorie_limit or settings.DEFAULT_CALORIE_LIMIT,
        stomach_capacity_ml=settings.STOMACH_CAPACITY_ML,
    )
    selected, skip = opt.process(
        with_stomach,
        goal=goal,
        allergies=allergies,
        dietary_filters=dietary_filters,
    )

    # 5. Strategy Planning Agent
    strategy_agent = StrategyPlanningAgent()
    strategy, explanation = strategy_agent.process(
        selected_dishes=selected,
        skip_dishes=skip,
        goal=goal,
        calorie_limit=calorie_limit or settings.DEFAULT_CALORIE_LIMIT,
    )

    # Build response
    nutrition_summary = _build_nutrition_summary(with_nutrition)
    stomach_simulation = _build_stomach_simulation(with_stomach, selected)

    confidence = (
        sum(d.confidence for d in detected_dishes) / len(detected_dishes)
        if detected_dishes
        else 0.0
    )

    return {
        "detected_dishes": [d.model_dump() for d in detected_dishes],
        "nutrition_summary": nutrition_summary,
        "stomach_simulation": stomach_simulation,
        "strategy": strategy,
        "explanation": explanation,
        "confidence_overall": round(confidence, 2),
    }


def _build_nutrition_summary(dishes) -> Dict[str, Any]:
    """Aggregate nutrition across all detected dishes."""
    total_cal = 0.0
    total_protein = 0.0
    total_fat = 0.0
    total_carbs = 0.0
    total_fiber = 0.0
    total_gl = 0.0

    for d in dishes:
        factor = d.estimated_grams / 100.0
        n = d.nutrition_per_100g
        total_cal += n.calories * factor
        total_protein += n.protein * factor
        total_fat += n.fat * factor
        total_carbs += n.carbs * factor
        total_fiber += n.fiber * factor
        total_gl += n.glycemic_load * factor

    return {
        "total_available_calories": round(total_cal, 1),
        "total_protein_g": round(total_protein, 1),
        "total_fat_g": round(total_fat, 1),
        "total_carbs_g": round(total_carbs, 1),
        "total_fiber_g": round(total_fiber, 1),
        "total_glycemic_load": round(total_gl, 1),
        "dish_count": len(dishes),
    }


def _build_stomach_simulation(dishes, selected) -> Dict[str, Any]:
    """Stomach physics summary."""
    total_vol = sum(d.stomach_impact.volume_ml for d in dishes)
    selected_vol = sum(d.stomach_impact.volume_ml for d in selected)
    avg_satiety = (
        sum(d.stomach_impact.satiety_score for d in selected) / len(selected)
        if selected
        else 0.0
    )

    return {
        "total_volume_ml": round(total_vol, 1),
        "selected_volume_ml": round(selected_vol, 1),
        "capacity_ml": 1350,
        "avg_satiety_score": round(avg_satiety, 2),
        "digestion_profiles": {
            "fast": sum(1 for d in selected if d.stomach_impact.digestion_speed == "fast"),
            "medium": sum(1 for d in selected if d.stomach_impact.digestion_speed == "medium"),
            "slow": sum(1 for d in selected if d.stomach_impact.digestion_speed == "slow"),
        },
    }


def _empty_response(msg: str) -> Dict[str, Any]:
    """Return empty structured response."""
    return {
        "detected_dishes": [],
        "nutrition_summary": {},
        "stomach_simulation": {},
        "strategy": {
            "phases": [],
            "skip": [],
            "total_calories": 0,
            "fullness_score": 0,
        },
        "explanation": msg,
        "confidence_overall": 0.0,
    }
