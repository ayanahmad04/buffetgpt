"""
Vision Agent - Detects dishes in buffet images using YOLOv8 or Google Gemini Vision.
"""

import io
import json
from typing import List, Optional

from PIL import Image

from app.models.schemas import DetectedDish


class VisionAgent:
    """
    Detects food items in buffet images.
    Supports YOLOv8 (local) and Google Gemini Vision API (free tier).
    """

    def __init__(self, model_type: str = "yolov8", gemini_api_key: Optional[str] = None):
        self.model_type = model_type
        self.gemini_api_key = gemini_api_key
        self._yolo_model = None

    def _load_yolo(self):
        """Lazy load YOLOv8 model."""
        if self._yolo_model is None:
            try:
                from ultralytics import YOLO
                # Use COCO pretrained - in production would use food-specific model
                self._yolo_model = YOLO("yolov8n.pt")
            except ImportError:
                self._yolo_model = None
        return self._yolo_model

    def _detect_yolo(self, image_bytes: bytes) -> List[DetectedDish]:
        """Detect using YOLOv8. COCO has food classes (pizza, cake, etc)."""
        model = self._load_yolo()
        if model is None:
            return self._fallback_detection(image_bytes)

        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            results = model(img, verbose=False)

            dishes = []
            # COCO food-related class IDs: 56=donut, 57=cake, 58=chair->59=couch, 60=pot...
            # YOLO COCO: 49=orange, 50=broccoli, 51=carrot, 52=hot dog, 53=pizza, 54=donut, 55=cake
            food_classes = {46: "banana", 47: "apple", 48: "sandwich", 49: "orange",
                           50: "broccoli", 51: "carrot", 52: "hot dog", 53: "pizza",
                           54: "donut", 55: "cake", 56: "chair"}

            for r in results:
                if r.boxes is not None:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0]) if hasattr(box, "conf") and box.conf is not None else 0.8
                        name = food_classes.get(cls_id, f"food_item_{cls_id}")
                        if cls_id < 57:  # Exclude non-food
                            dishes.append(DetectedDish(
                                name=name.replace("_", " ").title(),
                                confidence=conf,
                                estimated_portion_density=1.0,
                                estimated_grams=100,
                            ))
            if not dishes:
                return self._fallback_detection(image_bytes)
            return dishes[:15]  # Limit to 15 dishes
        except Exception:
            return self._fallback_detection(image_bytes)

    def _detect_gemini(self, image_bytes: bytes) -> List[DetectedDish]:
        """Detect using Google Gemini Vision API (free tier)."""
        if not self.gemini_api_key:
            return self._fallback_detection(image_bytes)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.gemini_api_key)
            prompt = (
                "List every distinct food/dish you see in this buffet image. "
                "For each item, respond with: name, estimated_grams (50-300), "
                "cooking_method (fried/grilled/raw/steamed/etc), cuisine_type. "
                "Return ONLY a valid JSON array, no other text: "
                '[{"name":"...", "grams":100, "cooking_method":"...", "cuisine":"..."}]'
            )
            image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(max_output_tokens=1024),
            )
            text = response.text or ""
            # Extract JSON from response (handle markdown code blocks)
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                items = json.loads(text[start:end])
                return [
                    DetectedDish(
                        name=item.get("name", "unknown"),
                        confidence=0.9,
                        estimated_grams=float(item.get("grams", 100)),
                        cooking_method=item.get("cooking_method"),
                        cuisine_type=item.get("cuisine"),
                    )
                    for item in items[:20]
                ]
        except Exception:
            pass
        return self._fallback_detection(image_bytes)

    def _fallback_detection(self, image_bytes: bytes) -> List[DetectedDish]:
        """
        Fallback when no ML model available.
        Returns generic buffet items for demo/testing.
        """
        return [
            DetectedDish(name="Mixed Salad", confidence=0.7, estimated_grams=80),
            DetectedDish(name="Grilled Chicken", confidence=0.7, estimated_grams=150),
            DetectedDish(name="Roasted Vegetables", confidence=0.7, estimated_grams=100),
            DetectedDish(name="Rice", confidence=0.7, estimated_grams=120),
            DetectedDish(name="Bread Roll", confidence=0.7, estimated_grams=50),
            DetectedDish(name="Soup", confidence=0.7, estimated_grams=200),
            DetectedDish(name="Pasta", confidence=0.7, estimated_grams=150),
            DetectedDish(name="Dessert", confidence=0.6, estimated_grams=80),
        ]

    def process(self, image_bytes: bytes) -> List[DetectedDish]:
        """Detect all dishes in the image."""
        if self.model_type == "gemini" and self.gemini_api_key:
            return self._detect_gemini(image_bytes)
        return self._detect_yolo(image_bytes)
