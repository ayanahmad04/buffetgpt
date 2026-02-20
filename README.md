# BuffetGPT

**AI-powered buffet strategist** — Upload an image, get an optimal eating strategy based on computer vision, nutrition science, and stomach volume physics.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What is BuffetGPT?

BuffetGPT is a multi-agent AI system that analyzes buffet images and generates personalized eating strategies. It detects dishes, maps nutrition, models stomach physics, and produces a structured plan: **what to eat, what to skip, how much, and in what order**.

Think of it as a real-time buffet strategist — not just a food recommender.

### Features

| Feature | Description |
|--------|-------------|
| **Vision Agent** | Detects dishes in images via Google Gemini Vision (free) or YOLOv8 |
| **Nutrition Intelligence** | Maps dishes to USDA-derived nutrition data (calories, protein, fats, carbs, fiber, glycemic load) |
| **Stomach Physics** | Models gastric capacity (~1.35L), satiety scores, and digestion speed |
| **Goal Optimization** | Supports fat loss, muscle gain, blood sugar control, or enjoyment-first |
| **Strategy Planning** | Eating phases, portion sizes, order, skip list, and natural language explanation |
| **Allergy & Dietary Filters** | Vegan, vegetarian, halal, and allergen exclusion |

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **Docker** (optional)

### 1. Clone & Install

```bash
# Backend
cd backend
pip install -r requirements.txt
```

### 2. Configure (Optional)

For real dish detection from images, add a [free Gemini API key](https://aistudio.google.com/apikey):

```bash
# backend/.env
GEMINI_API_KEY=your_key_here
VISION_MODEL=gemini
```

Without a key, the system uses fallback demo dishes — it still works for testing.

### 3. Run (Streamlit UI)

Start the backend and the Streamlit UI:

```bash
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2: Streamlit UI
cd streamlit_frontend
pip install -r requirements.txt
export BUFFETGPT_API_URL=http://localhost:8000/api/v1
streamlit run app.py
```

- **Streamlit UI:** http://localhost:8501
- **API docs:** http://localhost:8000/docs

---

## Docker

```bash
docker-compose up --build
```

- **Backend:** http://localhost:8000  
- **API docs:** http://localhost:8000/docs

With Gemini key: `GEMINI_API_KEY=your_key docker-compose up --build`

---

## Usage

### Web UI

1. Choose **Upload Image** or **Manual List**
2. Set your goal (fat loss, muscle gain, blood sugar, enjoyment)
3. Optionally set calorie limit, allergies, or dietary filters
4. Upload a buffet image or enter dish names
5. Get your eating strategy with phases, portions, and explanation

### API

**Analyze image**

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "image=@buffet.jpg" \
  -F "goal=fat_loss" \
  -F "calorie_limit=1500"
```

**Manual dish list**

```bash
curl -X POST "http://localhost:8000/api/v1/strategy/manual" \
  -H "Content-Type: application/json" \
  -d '{
    "dishes": [
      {"name": "Mixed Salad", "estimated_grams": 80},
      {"name": "Grilled Chicken", "estimated_grams": 150},
      {"name": "Rice", "estimated_grams": 120}
    ],
    "goal": "enjoyment_first",
    "calorie_limit": 2000
  }'
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/analyze` | Analyze buffet image (multipart: image, goal, calorie_limit, allergies, dietary_filters) |
| `POST` | `/api/v1/strategy/manual` | Generate strategy from manual dish list |
| `GET` | `/api/v1/health` | Health check |

### Goals

| Goal | Description |
|------|-------------|
| `enjoyment_first` | Balance satiety and variety |
| `fat_loss` | High protein, high fiber, low calorie density |
| `muscle_gain` | Prioritize protein and moderate carbs |
| `blood_sugar` | Low glycemic load, high fiber |

### Example Response

```json
{
  "detected_dishes": [
    {"name": "Mixed Salad", "confidence": 0.9, "estimated_grams": 80}
  ],
  "nutrition_summary": {
    "total_available_calories": 850,
    "total_protein_g": 52,
    "dish_count": 8
  },
  "stomach_simulation": {
    "capacity_ml": 1350,
    "avg_satiety_score": 12.5
  },
  "strategy": {
    "phases": [
      {"phase_name": "Starter", "items": [...]},
      {"phase_name": "Protein", "items": [...]}
    ],
    "skip": [{"name": "Dessert", "reason": "..."}],
    "total_calories": 820,
    "fullness_score": 0.92
  },
  "explanation": "Start with soup or salad to fill volume cheaply...",
  "confidence_overall": 0.85
}
```

More examples: [`docs/API_EXAMPLES.md`](docs/API_EXAMPLES.md)

---

## Project Structure

```
buffetgpt/
├── backend/
│   ├── app/
│   │   ├── agents/           # Multi-agent pipeline
│   │   │   ├── vision.py     # Dish detection (Gemini / YOLOv8)
│   │   │   ├── nutrition.py  # USDA nutrition mapping
│   │   │   ├── stomach.py    # Stomach physics engine
│   │   │   ├── optimization.py  # Goal-based optimization
│   │   │   ├── strategy.py   # Eating phase planner
│   │   │   └── pipeline.py   # Orchestrator
│   │   ├── api/routes/       # FastAPI endpoints
│   │   ├── config.py
│   │   ├── main.py
│   │   └── models/schemas.py
│   ├── requirements.txt
│   └── Dockerfile
├── streamlit_frontend/
│   ├── app.py              # Streamlit UI
│   └── requirements.txt
├── docs/
│   └── API_EXAMPLES.md
├── ARCHITECTURE.md
├── docker-compose.yml
└── README.md
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | Free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `VISION_MODEL` | `gemini` | `gemini` \| `yolov8` |
| `DEFAULT_CALORIE_LIMIT` | `2000` | Default calorie cap |
| `DEBUG` | `false` | Debug mode |

---

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** FastAPI, Python 3.10+
- **Vision:** Google Gemini (free) / YOLOv8 (optional)
- **Nutrition:** Embedded USDA-derived dataset
- **Deployment:** Docker Compose

---

## License

MIT
