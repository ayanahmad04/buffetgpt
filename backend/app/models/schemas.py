"""
Pydantic schemas for API requests and responses.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# --- Request Schemas ---


class ManualDishInput(BaseModel):
    """Single dish for manual input."""

    name: str
    estimated_grams: Optional[float] = 100
    cooking_method: Optional[str] = None


class AnalyzeRequest(BaseModel):
    """Manual strategy request (no image)."""

    dishes: List[ManualDishInput]
    goal: str = "enjoyment_first"
    calorie_limit: Optional[int] = None
    allergies: Optional[List[str]] = None
    dietary_filters: Optional[List[str]] = None  # halal, vegan, vegetarian


# --- Internal Agent Schemas ---


class DetectedDish(BaseModel):
    """Output from Vision Agent."""

    name: str
    confidence: float
    estimated_portion_density: float = 1.0  # g/ml
    cooking_method: Optional[str] = None
    cuisine_type: Optional[str] = None
    estimated_grams: float = 100
    bounding_box: Optional[Dict[str, float]] = None


class NutritionalData(BaseModel):
    """Per 100g nutrition data."""

    calories: float
    protein: float
    fat: float
    carbs: float
    fiber: float
    glycemic_load: float = 0.0
    confidence: float = 1.0


class DishWithNutrition(DetectedDish):
    """Dish enriched with nutrition data."""

    nutrition_per_100g: NutritionalData


class StomachImpact(BaseModel):
    """Stomach physics output per dish."""

    volume_ml: float
    satiety_score: float
    digestion_speed: str  # fast | medium | slow
    fullness_contribution: float


class DishWithStomachImpact(DishWithNutrition):
    """Dish with stomach physics data."""

    stomach_impact: StomachImpact


class PhaseItem(BaseModel):
    """Single item in an eating phase."""

    dish_name: str
    portion_grams: float
    portion_ml: Optional[float] = None
    calories: float
    protein: float
    carbs: float
    fat: float
    reason: Optional[str] = None


class EatingPhase(BaseModel):
    """Phase of eating (e.g., starter, protein, carbs)."""

    phase_name: str
    phase_order: int
    items: List[PhaseItem]


class StrategyResponse(BaseModel):
    """Full API response."""

    detected_dishes: List[DetectedDish]
    nutrition_summary: Dict[str, Any]
    stomach_simulation: Dict[str, Any]
    strategy: Dict[str, Any]
    explanation: str
    confidence_overall: float = 0.0
