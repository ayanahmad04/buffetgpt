"""
Strategy Planning Agent - Produces eating phases, order, portions, skip list, and explanation.
"""

from typing import Any, Dict, List, Tuple

from app.config import settings
from app.models.schemas import (
    DishWithStomachImpact,
    EatingPhase,
    PhaseItem,
)


class StrategyPlanningAgent:
    """
    Produces:
    - Eating phases (starter → protein → carbs → treats)
    - Portion sizes (grams)
    - Order of eating
    - Skip list
    - Estimated fullness curve
    - Natural language explanation
    """

    def _classify_phase(self, dish: DishWithStomachImpact) -> str:
        """Classify dish into eating phase based on nutrition and type."""
        n = dish.nutrition_per_100g
        name_lower = dish.name.lower()

        # Soups, salads, broths = starter (volume-filling, low-cal)
        if any(kw in name_lower for kw in ["soup", "salad", "broth", "consomme"]):
            return "starter"

        # High protein = protein phase
        if n.protein > 15 or any(kw in name_lower for kw in ["chicken", "fish", "steak", "salmon", "meat", "eggs"]):
            return "protein"

        # Desserts, cake, donut = treats
        if any(kw in name_lower for kw in ["dessert", "cake", "donut", "cookie", "pastry"]):
            return "treats"

        # Carbs: rice, pasta, bread, potato
        if any(kw in name_lower for kw in ["rice", "pasta", "bread", "potato", "quinoa", "beans"]):
            return "carbs"

        # Vegetables (non-salad)
        if any(kw in name_lower for kw in ["vegetable", "broccoli", "carrot"]):
            return "vegetables"

        # Default by nutrition
        if n.protein > 10:
            return "protein"
        if n.carbs > 20:
            return "carbs"
        return "vegetables"

    def _phase_order(self, phase_name: str) -> int:
        """Order of phases: starter first, treats last."""
        order_map = {
            "starter": 1,
            "protein": 2,
            "vegetables": 3,
            "carbs": 4,
            "treats": 5,
        }
        return order_map.get(phase_name, 3)

    def _compute_portion(
        self,
        dish: DishWithStomachImpact,
        selected_dishes: List[DishWithStomachImpact],
        calorie_budget_remaining: float,
        stomach_remaining_ml: float,
    ) -> Tuple[float, str]:
        """
        Compute optimal portion size for dish.
        Returns (portion_grams, reason).
        """
        n = dish.nutrition_per_100g
        cal_per_100 = n.calories
        vol_per_100 = dish.stomach_impact.volume_ml / (dish.estimated_grams / 100) if dish.estimated_grams else 100

        # Cap by stomach space and calorie budget
        max_by_cal = (calorie_budget_remaining / cal_per_100) * 100 if cal_per_100 > 0 else 500
        max_by_vol = (stomach_remaining_ml / vol_per_100) * 100 if vol_per_100 > 0 else 500

        portion = min(dish.estimated_grams, max_by_cal, max_by_vol, 250)  # Max 250g per item
        portion = max(20, round(portion, 0))  # Min 20g

        # Reason based on dish type
        if "soup" in dish.name.lower() or "salad" in dish.name.lower():
            reason = f"Volume-fill to increase satiety with low calories"
        elif n.protein > 15:
            reason = f"High protein ({n.protein}g/100g) for satiety"
        elif n.glycemic_load < 5:
            reason = f"Low glycemic load ({n.glycemic_load}) for blood sugar"
        else:
            reason = f"Balanced portion for variety"

        return portion, reason

    def process(
        self,
        selected_dishes: List[DishWithStomachImpact],
        skip_dishes: List[DishWithStomachImpact],
        goal: str,
        calorie_limit: int,
    ) -> Tuple[Dict[str, Any], str]:
        """
        Produce strategy dict and natural language explanation.
        """
        phase_groups: Dict[str, List[DishWithStomachImpact]] = {}
        for d in selected_dishes:
            phase = self._classify_phase(d)
            phase_groups.setdefault(phase, []).append(d)

        phases: List[Dict[str, Any]] = []
        total_calories = 0.0
        stomach_used_ml = 0.0
        stomach_capacity = settings.STOMACH_CAPACITY_ML

        for phase_name in sorted(phase_groups.keys(), key=self._phase_order):
            dishes = phase_groups[phase_name]
            items = []

            for dish in dishes:
                cal_remaining = calorie_limit - total_calories
                vol_remaining = stomach_capacity - stomach_used_ml
                portion, reason = self._compute_portion(dish, selected_dishes, cal_remaining, vol_remaining)

                n = dish.nutrition_per_100g
                factor = portion / 100.0
                item = PhaseItem(
                    dish_name=dish.name,
                    portion_grams=portion,
                    portion_ml=round(dish.stomach_impact.volume_ml * (portion / dish.estimated_grams), 1) if dish.estimated_grams else None,
                    calories=round(n.calories * factor, 1),
                    protein=round(n.protein * factor, 1),
                    carbs=round(n.carbs * factor, 1),
                    fat=round(n.fat * factor, 1),
                    reason=reason,
                )
                items.append(item)
                total_calories += item.calories
                stomach_used_ml += item.portion_ml or (portion * 1.0)  # Assume 1 g/ml

            phases.append({
                "phase_name": phase_name.replace("_", " ").title(),
                "phase_order": self._phase_order(phase_name),
                "items": [i.model_dump() for i in items],
            })

        # Sort phases by order
        phases.sort(key=lambda p: p["phase_order"])

        skip_list = [
            {"name": d.name, "reason": "Lower priority for goal or exceeded volume/calorie limit"}
            for d in skip_dishes
        ]

        fullness_score = min(1.0, stomach_used_ml / stomach_capacity)

        strategy = {
            "phase_1": phases[0] if phases else None,
            "phase_2": phases[1] if len(phases) > 1 else None,
            "phase_3": phases[2] if len(phases) > 2 else None,
            "phase_4": phases[3] if len(phases) > 3 else None,
            "phase_5": phases[4] if len(phases) > 4 else None,
            "phases": phases,
            "skip": skip_list,
            "total_calories": round(total_calories, 1),
            "fullness_score": round(fullness_score, 2),
            "stomach_used_ml": round(stomach_used_ml, 1),
        }

        explanation = self._generate_explanation(
            strategy=strategy,
            goal=goal,
            selected=selected_dishes,
            skip=skip_dishes,
        )

        return strategy, explanation

    def _generate_explanation(
        self,
        strategy: Dict[str, Any],
        goal: str,
        selected: List[DishWithStomachImpact],
        skip: List[DishWithStomachImpact],
    ) -> str:
        """Generate natural language strategy explanation."""
        parts = []

        # Start with soup/salad if present
        starter_items = [p for p in strategy.get("phases", []) if "starter" in p["phase_name"].lower()]
        if starter_items and starter_items[0].get("items"):
            parts.append(
                "Start with soup or salad to fill volume cheaply (low calories, high satiety). "
            )

        # Protein
        protein_items = [p for p in strategy.get("phases", []) if "protein" in p["phase_name"].lower()]
        if protein_items and protein_items[0].get("items"):
            names = [i["dish_name"] for i in protein_items[0]["items"]]
            parts.append(f"Then prioritize protein ({', '.join(names)}) for satiety and muscle support. ")

        # Carbs
        carb_items = [p for p in strategy.get("phases", []) if "carbs" in p["phase_name"].lower() or "vegetable" in p["phase_name"].lower()]
        if carb_items:
            for p in carb_items:
                if p.get("items"):
                    names = [i["dish_name"] for i in p["items"]]
                    parts.append(f"Add {', '.join(names)} for energy and fiber. ")

        # Treats
        treat_items = [p for p in strategy.get("phases", []) if "treat" in p["phase_name"].lower()]
        if treat_items and treat_items[0].get("items"):
            parts.append("Save dessert for last—your stomach will be fuller, so you'll eat less. ")

        if skip:
            parts.append(f"Skip or minimize: {', '.join(d.name for d in skip[:5])}. ")

        goal_hint = {
            "fat_loss": "Strategy favors high-protein, high-fiber, low-calorie-density items.",
            "muscle_gain": "Strategy prioritizes protein and moderate carbs for recovery.",
            "blood_sugar": "Strategy selects low-glycemic items and pairs carbs with fiber.",
            "enjoyment_first": "Strategy balances satiety with variety for maximum enjoyment.",
        }.get(goal, "")

        if goal_hint:
            parts.append(goal_hint)

        return "".join(parts).strip() or "Follow the phases in order for optimal satiety and nutrition."
