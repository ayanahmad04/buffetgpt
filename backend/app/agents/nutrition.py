"""
Nutrition Intelligence Agent - Maps dishes to USDA nutrition data.
"""

from typing import Dict, List, Optional

from app.models.schemas import DetectedDish, DishWithNutrition, NutritionalData


class NutritionAgent:
    """
    Maps detected dishes to nutrition data.
    Uses embedded USDA-derived dataset + fuzzy matching.
    """

    def __init__(self):
        self._db = self._load_nutrition_db()

    def _load_nutrition_db(self) -> Dict[str, Dict]:
        """Load nutrition database (USDA-derived values per 100g)."""
        # Core dataset: common buffet foods with realistic nutrition
        return {
            "mixed salad": {"cal": 18, "protein": 1.5, "fat": 0.3, "carbs": 3.5, "fiber": 1.2, "gl": 2},
            "salad": {"cal": 18, "protein": 1.5, "fat": 0.3, "carbs": 3.5, "fiber": 1.2, "gl": 2},
            "grilled chicken": {"cal": 165, "protein": 31, "fat": 3.6, "carbs": 0, "fiber": 0, "gl": 0},
            "chicken": {"cal": 165, "protein": 31, "fat": 3.6, "carbs": 0, "fiber": 0, "gl": 0},
            "roasted vegetables": {"cal": 65, "protein": 2, "fat": 3, "carbs": 8, "fiber": 2.5, "gl": 4},
            "vegetables": {"cal": 65, "protein": 2, "fat": 3, "carbs": 8, "fiber": 2.5, "gl": 4},
            "rice": {"cal": 130, "protein": 2.7, "fat": 0.3, "carbs": 28, "fiber": 0.4, "gl": 23},
            "bread roll": {"cal": 265, "protein": 8.5, "fat": 3.2, "carbs": 50, "fiber": 2.7, "gl": 25},
            "bread": {"cal": 265, "protein": 8.5, "fat": 3.2, "carbs": 50, "fiber": 2.7, "gl": 25},
            "soup": {"cal": 45, "protein": 2.5, "fat": 1.5, "carbs": 6, "fiber": 1, "gl": 5},
            "pasta": {"cal": 131, "protein": 5, "fat": 1.1, "carbs": 25, "fiber": 1.8, "gl": 18},
            "dessert": {"cal": 350, "protein": 4, "fat": 15, "carbs": 50, "fiber": 1, "gl": 35},
            "cake": {"cal": 350, "protein": 4, "fat": 15, "carbs": 50, "fiber": 1, "gl": 35},
            "donut": {"cal": 421, "protein": 5, "fat": 22, "carbs": 52, "fiber": 1.5, "gl": 40},
            "pizza": {"cal": 266, "protein": 11, "fat": 10, "carbs": 33, "fiber": 2.3, "gl": 22},
            "hot dog": {"cal": 290, "protein": 10, "fat": 26, "carbs": 4, "fiber": 0, "gl": 3},
            "sandwich": {"cal": 250, "protein": 12, "fat": 10, "carbs": 28, "fiber": 1.5, "gl": 20},
            "broccoli": {"cal": 34, "protein": 2.8, "fat": 0.4, "carbs": 7, "fiber": 2.6, "gl": 2},
            "carrot": {"cal": 41, "protein": 0.9, "fat": 0.2, "carbs": 10, "fiber": 2.8, "gl": 5},
            "apple": {"cal": 52, "protein": 0.3, "fat": 0.2, "carbs": 14, "fiber": 2.4, "gl": 6},
            "orange": {"cal": 47, "protein": 0.9, "fat": 0.1, "carbs": 12, "fiber": 2.4, "gl": 5},
            "banana": {"cal": 89, "protein": 1.1, "fat": 0.3, "carbs": 23, "fiber": 2.6, "gl": 12},
            "steak": {"cal": 271, "protein": 26, "fat": 18, "carbs": 0, "fiber": 0, "gl": 0},
            "fish": {"cal": 206, "protein": 22, "fat": 12, "carbs": 0, "fiber": 0, "gl": 0},
            "salmon": {"cal": 208, "protein": 20, "fat": 13, "carbs": 0, "fiber": 0, "gl": 0},
            "fried chicken": {"cal": 287, "protein": 23, "fat": 18, "carbs": 12, "fiber": 0.5, "gl": 8},
            "potato": {"cal": 77, "protein": 2, "fat": 0.1, "carbs": 17, "fiber": 2.2, "gl": 14},
            "fries": {"cal": 312, "protein": 3.4, "fat": 15, "carbs": 42, "fiber": 3.8, "gl": 25},
            "cheese": {"cal": 402, "protein": 25, "fat": 33, "carbs": 1.3, "fiber": 0, "gl": 0},
            "eggs": {"cal": 155, "protein": 13, "fat": 11, "carbs": 1.1, "fiber": 0, "gl": 0},
            "beans": {"cal": 127, "protein": 8.7, "fat": 0.5, "carbs": 23, "fiber": 6.4, "gl": 6},
            "lentils": {"cal": 116, "protein": 9, "fat": 0.4, "carbs": 20, "fiber": 7.9, "gl": 5},
            "quinoa": {"cal": 120, "protein": 4.4, "fat": 1.9, "carbs": 21, "fiber": 2.8, "gl": 13},
            "hummus": {"cal": 166, "protein": 7.9, "fat": 9.6, "carbs": 14, "fiber": 6, "gl": 4},
        }

    def _lookup(self, dish_name: str) -> Optional[Dict]:
        """Fuzzy lookup in nutrition database."""
        name_lower = dish_name.lower().strip()
        # Direct match
        if name_lower in self._db:
            return self._db[name_lower]
        # Partial match
        for key, val in self._db.items():
            if key in name_lower or name_lower in key:
                return val
        # Default: generic mixed dish
        return {"cal": 150, "protein": 8, "fat": 8, "carbs": 12, "fiber": 1.5, "gl": 10}

    def process(self, dishes: List[DetectedDish]) -> List[DishWithNutrition]:
        """Enrich each dish with nutrition data per 100g."""
        result = []
        for d in dishes:
            nd = self._lookup(d.name)
            nutrition = NutritionalData(
                calories=nd["cal"],
                protein=nd["protein"],
                fat=nd["fat"],
                carbs=nd["carbs"],
                fiber=nd["fiber"],
                glycemic_load=nd["gl"],
                confidence=0.9 if d.name.lower() in str(self._db) else 0.7,
            )
            result.append(
                DishWithNutrition(
                    name=d.name,
                    confidence=d.confidence,
                    estimated_portion_density=d.estimated_portion_density,
                    cooking_method=d.cooking_method,
                    cuisine_type=d.cuisine_type,
                    estimated_grams=d.estimated_grams,
                    bounding_box=d.bounding_box,
                    nutrition_per_100g=nutrition,
                )
            )
        return result
