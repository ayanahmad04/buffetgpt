"""
Goal Optimization Agent - Constrained optimization for eating strategy.
"""

from typing import Dict, List, Optional, Tuple

from app.config import settings
from app.models.schemas import DishWithStomachImpact


class GoalOptimizationAgent:
    """
    Maximizes goal reward subject to stomach volume and calorie limits.
    Goals: fat_loss, muscle_gain, blood_sugar, enjoyment_first
    """

    def __init__(
        self,
        calorie_limit: Optional[int] = None,
        stomach_capacity_ml: float = 1350,
    ):
        self.calorie_limit = calorie_limit or settings.DEFAULT_CALORIE_LIMIT
        self.stomach_capacity_ml = stomach_capacity_ml

    def _goal_reward(self, dish: DishWithStomachImpact, goal: str) -> float:
        """Score per dish for given goal."""
        n = dish.nutrition_per_100g
        g = dish.estimated_grams / 100.0
        sat = dish.stomach_impact.satiety_score

        if goal == "fat_loss":
            # Prefer: high protein, high fiber, low calorie density
            return (n.protein * 2 + n.fiber * 2 - n.calories / 50) * g
        if goal == "muscle_gain":
            # Prefer: high protein, moderate carbs
            return (n.protein * 3 + n.carbs * 0.5) * g
        if goal == "blood_sugar":
            # Prefer: low glycemic load, high fiber
            return (10 - n.glycemic_load + n.fiber * 2) * g
        # enjoyment_first: maximize satiety + variety
        return (sat + n.protein * 0.5) * g

    def _filter_allergies(self, dishes: List[DishWithStomachImpact], allergies: List[str]) -> List[DishWithStomachImpact]:
        """Remove dishes that may contain allergens."""
        if not allergies:
            return dishes
        allergen_keywords = [a.lower() for a in allergies]
        return [
            d for d in dishes
            if not any(kw in d.name.lower() for kw in allergen_keywords)
        ]

    def _filter_dietary(self, dishes: List[DishWithStomachImpact], filters: List[str]) -> List[DishWithStomachImpact]:
        """Apply halal, vegan, vegetarian filters (simplified)."""
        if not filters:
            return dishes
        filter_lower = [f.lower() for f in filters]
        if "vegan" in filter_lower:
            non_vegan = {"chicken", "meat", "fish", "salmon", "steak", "eggs", "cheese"}
            return [d for d in dishes if not any(nv in d.name.lower() for nv in non_vegan)]
        if "vegetarian" in filter_lower:
            non_veg = {"chicken", "meat", "fish", "salmon", "steak", "hot dog"}
            return [d for d in dishes if not any(nv in d.name.lower() for nv in non_veg)]
        return dishes

    def process(
        self,
        dishes: List[DishWithStomachImpact],
        goal: str = "enjoyment_first",
        allergies: Optional[List[str]] = None,
        dietary_filters: Optional[List[str]] = None,
    ) -> Tuple[List[DishWithStomachImpact], List[DishWithStomachImpact]]:
        """
        Returns (selected_dishes, skip_dishes).
        Uses greedy heuristic: sort by goal_reward, fill stomach until limit.
        """
        allergies = allergies or []
        dietary_filters = dietary_filters or []

        dishes = self._filter_allergies(dishes, allergies)
        dishes = self._filter_dietary(dishes, dietary_filters)

        if not dishes:
            return [], []

        # Score each dish
        scored = [(self._goal_reward(d, goal), d) for d in dishes]
        scored.sort(key=lambda x: -x[0])

        selected = []
        total_cal = 0
        total_vol = 0

        for _, d in scored:
            cal = d.nutrition_per_100g.calories * (d.estimated_grams / 100)
            vol = d.stomach_impact.volume_ml
            if total_cal + cal <= self.calorie_limit and total_vol + vol <= self.stomach_capacity_ml * 1.1:
                selected.append(d)
                total_cal += cal
                total_vol += vol

        skip = [d for d in dishes if d not in selected]
        return selected, skip
