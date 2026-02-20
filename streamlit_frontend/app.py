import os
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
import streamlit as st


GOALS: Dict[str, Dict[str, str]] = {
    "enjoyment_first": {
        "label": "Enjoyment First",
        "icon": "🎯",
        "desc": "Balance satiety & variety",
    },
    "fat_loss": {
        "label": "Fat Loss",
        "icon": "🔥",
        "desc": "High protein, low calorie density",
    },
    "muscle_gain": {
        "label": "Muscle Gain",
        "icon": "💪",
        "desc": "Prioritize protein & carbs",
    },
    "blood_sugar": {
        "label": "Blood Sugar Control",
        "icon": "📊",
        "desc": "Low glycemic, high fiber",
    },
}


def _api_base() -> str:
    base = os.environ.get("BUFFETGPT_API_URL") or os.environ.get("API_URL") or "http://localhost:8000/api/v1"
    return base.rstrip("/")


def _raise_for_api_error(res: requests.Response, fallback: str) -> None:
    if res.ok:
        return
    detail = None
    try:
        payload = res.json()
        if isinstance(payload, dict):
            detail = payload.get("detail")
    except Exception:
        detail = None
    raise RuntimeError(detail or fallback)


@st.cache_data(ttl=5, show_spinner=False)
def health_check(api_base: str) -> Optional[Dict[str, Any]]:
    try:
        res = requests.get(f"{api_base}/health", timeout=3)
        return res.json() if res.ok else None
    except Exception:
        return None


def analyze_image(
    file_bytes: bytes,
    filename: str,
    mime_type: str,
    *,
    goal: str,
    calorie_limit: int,
    allergies: List[str],
    dietary_filters: List[str],
) -> Dict[str, Any]:
    api_base = _api_base()
    files = {"image": (filename, file_bytes, mime_type)}
    data: Dict[str, Any] = {"goal": goal, "calorie_limit": str(calorie_limit)}
    if allergies:
        data["allergies"] = ", ".join(allergies)
    if dietary_filters:
        data["dietary_filters"] = ", ".join(dietary_filters)

    res = requests.post(f"{api_base}/analyze", files=files, data=data, timeout=120)
    _raise_for_api_error(res, "Analysis failed")
    payload = res.json()
    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected response shape from API")
    return payload


def analyze_manual(
    dishes: List[Dict[str, Any]],
    *,
    goal: str,
    calorie_limit: int,
    allergies: List[str],
    dietary_filters: List[str],
) -> Dict[str, Any]:
    api_base = _api_base()
    body: Dict[str, Any] = {
        "dishes": dishes,
        "goal": goal,
        "calorie_limit": calorie_limit,
        "allergies": allergies,
        "dietary_filters": dietary_filters,
    }
    res = requests.post(f"{api_base}/strategy/manual", json=body, timeout=120)
    _raise_for_api_error(res, "Strategy generation failed")
    payload = res.json()
    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected response shape from API")
    return payload


def _split_csv(text: str) -> List[str]:
    return [s.strip() for s in (text or "").split(",") if s.strip()]


def _css() -> str:
    return """
<style>
  /* Background */
  [data-testid="stAppViewContainer"]{
    background: radial-gradient(1200px circle at 15% 15%, rgba(235,116,26,.12), transparent 55%),
                radial-gradient(1200px circle at 80% 10%, rgba(245,158,11,.10), transparent 60%),
                linear-gradient(135deg, #fffbeb 0%, #fafaf9 45%, #fff7ed 100%);
  }

  /* Make the top block feel like a header */
  .buffet-header{
    padding: 0.25rem 0 0.75rem 0;
  }
  .buffet-title{
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #3f1508;
    margin: 0;
    line-height: 1.05;
  }
  .buffet-subtitle{
    margin: .25rem 0 0 0;
    color: rgba(87,83,78,.85);
    font-size: .95rem;
  }

  /* Card */
  .card{
    background: rgba(255,255,255,.78);
    border: 1px solid rgba(231,229,228,.85);
    border-radius: 18px;
    padding: 18px 18px;
    box-shadow: 0 1px 0 rgba(0,0,0,.02);
    backdrop-filter: blur(6px);
  }
  .card h2, .card h3{
    margin-top: 0;
  }

  /* Chips */
  .chip{
    display:inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    background: rgba(231,229,228,.9);
    color: rgba(87,83,78,.95);
    font-size: .85rem;
    margin-right: 6px;
    margin-bottom: 6px;
  }

  /* Phase cards */
  .phase-card{
    background: white;
    border: 1px solid rgba(231,229,228,.95);
    border-radius: 14px;
    padding: 14px 14px;
  }
  .phase-title{
    font-weight: 700;
    color: rgba(41,37,36,.95);
    margin: 0 0 10px 0;
    display:flex;
    align-items:center;
    gap:8px;
  }
  .phase-dot{
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: rgba(235,116,26,.85);
    display:inline-block;
  }
  .item-row{
    display:flex;
    justify-content: space-between;
    align-items:flex-start;
    gap: 10px;
    padding: 6px 0;
    border-bottom: 1px dashed rgba(231,229,228,.85);
  }
  .item-row:last-child{ border-bottom: 0; }
  .item-name{ font-weight: 600; color: rgba(68,64,60,.95); }
  .item-meta{ color: rgba(120,113,108,.95); font-size: .85rem; }
  .item-reason{ color: rgba(168,162,158,.95); font-size: .8rem; margin-top:2px; }
  .item-macros{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
                font-size: .8rem; color: rgba(120,113,108,.95); white-space: nowrap; margin-top: 2px; }

  /* Reduce extra whitespace above the first container */
  .block-container{ padding-top: 1.5rem; }
</style>
"""


def render_results(data: Dict[str, Any]) -> None:
    detected = data.get("detected_dishes") or []
    strategy = data.get("strategy") or {}
    phases = strategy.get("phases") or []
    skip = strategy.get("skip") or []
    explanation = data.get("explanation") or ""
    confidence = data.get("confidence_overall")

    total_cal = strategy.get("total_calories") or 0
    fullness_score = float(strategy.get("fullness_score") or 0.0)
    fullness_pct = max(0.0, min(1.0, fullness_score))

    st.markdown("### Results")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Calories", f"{int(total_cal)}")
    with c2:
        st.metric("Detected", f"{len(detected)} dishes")
    with c3:
        if confidence is None:
            st.metric("Confidence", "—")
        else:
            st.metric("Confidence", f"{float(confidence) * 100:.0f}%")
    with c4:
        st.metric("Fullness", f"{fullness_pct * 100:.0f}%")
        st.progress(fullness_pct)

    st.markdown(f'<div class="card"><h3>Strategy</h3><div style="color:rgba(41,37,36,.92);line-height:1.55;">{explanation}</div></div>', unsafe_allow_html=True)

    st.markdown("### Eating Order")
    if not phases:
        st.info("No phases returned by the API.")
    else:
        cols = st.columns(2)
        for i, ph in enumerate(phases):
            with cols[i % 2]:
                items = ph.get("items") or []
                inner = []
                for it in items:
                    dish = it.get("dish_name", "Unknown")
                    grams = it.get("portion_grams", 0)
                    cal = it.get("calories", 0)
                    protein = it.get("protein", 0)
                    carbs = it.get("carbs", 0)
                    fat = it.get("fat", 0)
                    reason = it.get("reason")
                    inner.append(
                        f"""
                        <div class="item-row">
                          <div>
                            <div><span class="item-name">{dish}</span>
                              <span class="item-meta"> {grams}g · {cal} cal</span>
                            </div>
                            {f'<div class="item-reason">{reason}</div>' if reason else ''}
                          </div>
                          <div class="item-macros">P{protein} C{carbs} F{fat}</div>
                        </div>
                        """
                    )

                html = f"""
                <div class="phase-card">
                  <div class="phase-title"><span class="phase-dot"></span>{ph.get('phase_name','Phase')}</div>
                  {''.join(inner) if inner else '<div class="item-meta">No items</div>'}
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)

    if skip:
        st.markdown("### Skip or minimize")
        chips = []
        for s in skip:
            name = s.get("name") if isinstance(s, dict) else str(s)
            chips.append(f'<span class="chip">{name}</span>')
        st.markdown(f'<div class="card">{"".join(chips)}</div>', unsafe_allow_html=True)

    if detected:
        with st.expander(f"Detected dishes ({len(detected)})"):
            for d in detected:
                name = d.get("name", "Unknown")
                grams = d.get("estimated_grams")
                conf = d.get("confidence")
                meta = []
                if grams is not None:
                    meta.append(f"{grams}g")
                if conf is not None:
                    meta.append(f"{float(conf) * 100:.0f}%")
                st.write(f"- **{name}**" + (f" — {' · '.join(meta)}" if meta else ""))

    nutrition_summary = data.get("nutrition_summary") or {}
    if isinstance(nutrition_summary, dict) and nutrition_summary:
        with st.expander("Nutrition summary"):
            pairs = sorted(nutrition_summary.items(), key=lambda kv: str(kv[0]))
            rows = [{"metric": str(k).replace("_", " "), "value": v} for k, v in pairs]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    stomach = data.get("stomach_simulation") or {}
    if isinstance(stomach, dict) and stomach:
        with st.expander("Stomach simulation"):
            st.json(stomach)


def main() -> None:
    st.set_page_config(page_title="BuffetGPT", layout="wide")
    st.markdown(_css(), unsafe_allow_html=True)

    api_base = _api_base()
    health = health_check(api_base)

    st.markdown(
        """
        <div class="buffet-header">
          <div class="buffet-title">BuffetGPT</div>
          <div class="buffet-subtitle">AI-powered buffet eating strategy</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_left, top_right = st.columns([3, 2], vertical_alignment="center")
    with top_left:
        st.caption(f"API: `{api_base}`" + (" (healthy)" if health else " (unreachable)"))
    with top_right:
        mode_label = st.radio(
            "Mode",
            options=["📷 Upload Image", "✏️ Manual List"],
            horizontal=True,
            label_visibility="collapsed",
            key="mode_label",
        )
    mode = "image" if mode_label.startswith("📷") else "manual"

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Your Goal")
    goal = st.radio(
        "Goal",
        options=list(GOALS.keys()),
        horizontal=True,
        label_visibility="collapsed",
        format_func=lambda k: f"{GOALS[k]['icon']} {GOALS[k]['label']}",
        key="goal",
    )

    c1, c2, c3 = st.columns([1.2, 1.4, 1.6], vertical_alignment="center")
    with c1:
        calorie_limit = st.number_input(
            "Calorie limit",
            min_value=800,
            max_value=4000,
            step=100,
            value=int(st.session_state.get("calorie_limit", 2000)),
            key="calorie_limit",
        )
    with c2:
        allergies_text = st.text_input(
            "Allergies (comma-separated)",
            value=st.session_state.get("allergies_text", ""),
            placeholder="e.g. nuts, shellfish",
            key="allergies_text",
        )
    with c3:
        dietary = st.selectbox(
            "Dietary",
            options=["None", "Vegan", "Vegetarian", "Halal"],
            index=0,
            key="dietary",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    allergies = _split_csv(allergies_text)
    dietary_filters = []
    if dietary != "None":
        dietary_filters = [dietary.lower()]

    st.markdown("### Input")

    if "result" not in st.session_state:
        st.session_state["result"] = None
    if "error" not in st.session_state:
        st.session_state["error"] = None

    if mode == "image":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("Upload a buffet photo. We’ll detect dishes and build your strategy.")
        uploaded = st.file_uploader("Buffet image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

        if uploaded is not None:
            st.image(uploaded, caption=uploaded.name, use_container_width=True)

        col_a, col_b = st.columns([1, 1], vertical_alignment="center")
        with col_a:
            run = st.button(
                "Analyze Buffet",
                type="primary",
                disabled=(uploaded is None),
                use_container_width=True,
            )
        with col_b:
            clear = st.button("Clear", disabled=(uploaded is None), use_container_width=True)

        if clear:
            st.session_state["result"] = None
            st.session_state["error"] = None
            st.rerun()

        if run and uploaded is not None:
            st.session_state["error"] = None
            st.session_state["result"] = None
            with st.spinner("Analyzing…"):
                try:
                    st.session_state["result"] = analyze_image(
                        uploaded.getvalue(),
                        uploaded.name or "buffet.jpg",
                        uploaded.type or "image/jpeg",
                        goal=goal,
                        calorie_limit=int(calorie_limit),
                        allergies=allergies,
                        dietary_filters=dietary_filters,
                    )
                except Exception as e:
                    st.session_state["error"] = str(e) or "Something went wrong"
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("Enter the dishes you see at the buffet. We’ll build your strategy.")

        default_rows = [
            {"name": "Mixed Salad", "estimated_grams": 80},
            {"name": "Grilled Chicken", "estimated_grams": 150},
            {"name": "Rice", "estimated_grams": 120},
            {"name": "Soup", "estimated_grams": 200},
            {"name": "Dessert", "estimated_grams": 80},
        ]
        if "manual_df" not in st.session_state:
            st.session_state["manual_df"] = pd.DataFrame(default_rows)

        edited = st.data_editor(
            st.session_state["manual_df"],
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "name": st.column_config.TextColumn("Dish name", required=False),
                "estimated_grams": st.column_config.NumberColumn(
                    "g", min_value=20, max_value=500, step=10, required=False
                ),
            },
        )
        st.session_state["manual_df"] = edited

        has_any_dish = False
        if isinstance(edited, pd.DataFrame) and "name" in edited.columns:
            has_any_dish = (
                edited["name"]
                .fillna("")
                .astype(str)
                .str.strip()
                .ne("")
                .any()
            )

        run = st.button(
            "Get Strategy",
            type="primary",
            use_container_width=True,
            disabled=not has_any_dish,
        )

        if run:
            st.session_state["error"] = None
            st.session_state["result"] = None
            rows = edited.to_dict(orient="records") if isinstance(edited, pd.DataFrame) else []
            dishes = []
            for r in rows:
                name = str(r.get("name") or "").strip()
                if not name:
                    continue
                grams = r.get("estimated_grams") or 100
                dishes.append({"name": name, "estimated_grams": int(grams)})

            if not dishes:
                st.session_state["error"] = "Please add at least one dish name."
            else:
                with st.spinner("Generating…"):
                    try:
                        st.session_state["result"] = analyze_manual(
                            dishes,
                            goal=goal,
                            calorie_limit=int(calorie_limit),
                            allergies=allergies,
                            dietary_filters=dietary_filters,
                        )
                    except Exception as e:
                        st.session_state["error"] = str(e) or "Something went wrong"
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.get("error"):
        st.error(st.session_state["error"])

    if st.session_state.get("result"):
        render_results(st.session_state["result"])

    st.caption("BuffetGPT — Computer vision, nutrition science & stomach physics")


if __name__ == "__main__":
    main()

