import streamlit as st
import requests

# Nutritionix API credentials
APP_ID = "4137b2bd"
APP_KEY = "0d54df8b5b390485a6b9ee2f7ec8cdbd"

# Health condition thresholds (FSSAI/ICMR-aligned)
AI_THRESHOLDS = {
    "Obesity": {
        "nf_calories": (500, "max"),
        "nf_total_fat": (15, "max"),
        "nf_saturated_fat": (5, "max"),
        "nf_trans_fatty_acid": (0.5, "max"),
    },
    "Diabetes": {
        "nf_sugars": (8, "max"),
        "nf_total_carbohydrate": (45, "max"),
    },
    "High Blood Pressure": {
        "nf_sodium": (500, "max"),
    },
    "Anemia": {
        "full_nutrients": {
            "303": (6, "min"),     # Iron
            "401": (12, "min"),    # Vitamin C
            "417": (150, "min"),   # Folate
        }
    },
    "None": {}
}

# Fetch nutrition from API
def fetch_nutrition(food_name):
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": APP_ID,
        "x-app-key": APP_KEY,
        "Content-Type": "application/json"
    }
    body = {"query": food_name}
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        return None
    data = response.json().get("foods", [])
    return data[0] if data else None

# AI health analysis
def analyze_nutrition(data, condition):
    warnings = []
    if not data or condition == "None":
        return warnings

    rules = AI_THRESHOLDS.get(condition, {})

    # Handle direct nutrient fields
    for field, value in rules.items():
        if field == "full_nutrients":
            continue
        limit, rule = value
        val = data.get(field)
        if val is not None:
            if rule == "max" and val > limit:
                warnings.append(f"⚠️ {field} is high ({val:.1f}) — limit {limit}")
            elif rule == "min" and val < limit:
                warnings.append(f"⚠️ {field} is low ({val:.1f}) — needs at least {limit}")

    # Handle full_nutrients (used for anemia)
    if "full_nutrients" in rules:
        nutrients = {str(n["attr_id"]): n["value"] for n in data.get("full_nutrients", [])}
        for attr_id, (limit, rule) in rules["full_nutrients"].items():
            val = nutrients.get(str(attr_id))
            if val is not None:
                if rule == "max" and val > limit:
                    warnings.append(f"⚠️ Nutrient {attr_id} is high ({val:.1f})")
                elif rule == "min" and val < limit:
                    warnings.append(f"⚠️ Nutrient {attr_id} is low ({val:.1f})")

    return warnings


# Streamlit UI
st.set_page_config("Smart AI Nutrition Advisor", page_icon="🧠")
st.title("🧠 AI-Based Smart Nutrition Risk Checker")
st.write("Get live nutrition data & AI health risk analysis (FSSAI + ICMR aligned)")

food = st.text_input("🍽️ Enter your food name (e.g. Chole Bhature)")
condition = st.selectbox("🩺 Health Condition", list(AI_THRESHOLDS.keys()))

if food:
    with st.spinner("🔍 Fetching data from Nutritionix..."):
        data = fetch_nutrition(food)
    if not data:
        st.error("❌ API error or food not found.")
    else:
        st.success(f"✅ Found: {data['food_name'].title()}")
        st.subheader("🔬 Nutritional Facts")
        st.write({
            "Calories": data.get("nf_calories"),
            "Total Fat": data.get("nf_total_fat"),
            "Saturated Fat": data.get("nf_saturated_fat"),
            "Trans Fat": data.get("nf_trans_fatty_acid"),
            "Carbs": data.get("nf_total_carbohydrate"),
            "Sugars": data.get("nf_sugars"),
            "Protein": data.get("nf_protein"),
            "Sodium": data.get("nf_sodium")
        })

        st.subheader("🧪 AI Health Risk Analysis")
        warnings = analyze_nutrition(data, condition)
        if warnings:
            for w in warnings:
                st.warning(w)
        else:
            st.success("✅ This food is okay for your selected health condition.")










