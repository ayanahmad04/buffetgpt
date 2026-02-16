"""
Stomach Physics Agent - Models gastric volume, emptying rates, and satiety.
"""

from typing import List

from app.config import settings
from app.models.schemas import DishWithNutrition, DishWithStomachImpact, StomachImpact


class StomachPhysicsAgent:
    """
    Models stomach as ~1.35L capacity.
    Liquids empty fastest, fats slowest.
    Satiety = protein + fiber + volume - calorie_density
    """

    STOMACH_CAPACITY_ML = settings.STOMACH_CAPACITY_ML

    def _satiety_score(self, dish: DishWithNutrition) -> float:
        """
        Satiety per 100g: higher = more filling per gram.
        Formula: protein*2 + fiber*3 + (100/calorie_density) - fat*0.5
        """
        n = dish.nutrition_per_100g
        cal = max(n.calories, 10)
        protein_score = n.protein * 2.0
        fiber_score = n.fiber * 3.0
        volume_score = 100.0 / (cal / 100.0) if cal > 0 else 0  # inverse calorie density
        fat_penalty = n.fat * 0.5  # Fats are slow to digest but less satiating per calorie
        return max(0, protein_score + fiber_score + volume_score - fat_penalty)

    def _digestion_speed(self, dish: DishWithNutrition) -> str:
        """Liquids fast, fats slow."""
        n = dish.nutrition_per_100g
        if n.calories < 60 and n.fat < 2:  # Broth-like
            return "fast"
        if n.fat > 15:
            return "slow"
        if n.fiber > 5:
            return "medium"
        return "medium"

    def _volume_ml(self, dish: DishWithNutrition) -> float:
        """Estimate volume from grams. Assume density ~1 g/ml for mixed foods."""
        density = dish.estimated_portion_density or 1.0
        return dish.estimated_grams / density

    def process(self, dishes: List[DishWithNutrition]) -> List[DishWithStomachImpact]:
        """Add stomach physics to each dish."""
        result = []
        for d in dishes:
            vol = self._volume_ml(d)
            satiety = self._satiety_score(d)
            speed = self._digestion_speed(d)
            # Fullness contribution: volume * satiety factor
            fullness = min(1.0, (vol / self.STOMACH_CAPACITY_ML) * (1 + satiety * 0.1))
            impact = StomachImpact(
                volume_ml=vol,
                satiety_score=round(satiety, 2),
                digestion_speed=speed,
                fullness_contribution=round(fullness, 3),
            )
            result.append(
                DishWithStomachImpact(
                    **d.model_dump(),
                    stomach_impact=impact,
                )
            )
        return result
