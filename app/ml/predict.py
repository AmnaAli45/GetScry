import pickle
import json
import pandas as pd
import shap
import os

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "xgb_final_model.pkl")
CONFIG_PATH = os.path.join(BASE_DIR, "model_config.json")
FEATURES_PATH = os.path.join(BASE_DIR, "feature_columns.json")
PCA_PATH = os.path.join(BASE_DIR, "pca_transformer.pkl")

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)
    THRESHOLD = config["threshold"]

with open(FEATURES_PATH, "r") as f:
    FEATURE_COLUMNS = json.load(f)

with open(PCA_PATH, "rb") as f:
    pca = pickle.load(f)

# SHAP explainer - model se seedha banaya ja sakta hai, alag se save karne ki zaroorat nahi
explainer = shap.TreeExplainer(model)

# Feature names ko readable labels mein map karein (dashboard pe dikhane ke liye)
FRIENDLY_NAMES = {
    "PageValues": "High-value page views",
    "ExitRates": "Exit rate",
    "BounceRates": "Bounce rate",
    "ProductEngagementPCA": "Product browsing engagement",
    "Administrative": "Admin pages viewed",
    "Administrative_Duration": "Time on admin pages",
    "Informational": "Informational pages viewed",
    "Informational_Duration": "Time on informational pages",
    "SpecialDay": "Proximity to special day",
    "Weekend": "Weekend visit",
}


def _friendly(feature_name: str) -> str:
    if feature_name in FRIENDLY_NAMES:
        return FRIENDLY_NAMES[feature_name]
    if feature_name.startswith("Month_"):
        return f"Visited in {feature_name.replace('Month_', '')}"
    if feature_name.startswith("VisitorType_"):
        return feature_name.replace("VisitorType_", "").replace("_", " ")
    return feature_name


def _build_input_df(
    administrative, administrative_duration, informational, informational_duration,
    product_pages, product_duration, bounce_rates, exit_rates, page_values,
    special_day, operating_systems, browser, region, traffic_type,
    weekend, month, visitor_type,
) -> pd.DataFrame:

    product_df = pd.DataFrame(
        [[product_pages, product_duration]],
        columns=["ProductRelated", "ProductRelated_Duration"]
    )
    product_engagement_pca = pca.transform(product_df)[0][0]

    raw = {
        "Administrative": administrative,
        "Administrative_Duration": administrative_duration,
        "Informational": informational,
        "Informational_Duration": informational_duration,
        "BounceRates": bounce_rates,
        "ExitRates": exit_rates,
        "PageValues": page_values,
        "SpecialDay": special_day,
        "OperatingSystems": operating_systems,
        "Browser": browser,
        "Region": region,
        "TrafficType": traffic_type,
        "Weekend": int(weekend),
        "ProductEngagementPCA": product_engagement_pca,
        "Month": month,
        "VisitorType": visitor_type,
    }

    input_df = pd.DataFrame([raw])
    input_df = pd.get_dummies(input_df, columns=["Month", "VisitorType"], drop_first=True)
    input_df = input_df.reindex(columns=FEATURE_COLUMNS, fill_value=0)
    return input_df


def calculate_intent_score(**kwargs) -> float:
    input_df = _build_input_df(**kwargs)
    probability = model.predict_proba(input_df)[:, 1][0]
    return round(float(probability) * 100, 2)


def get_top_reasons(top_n: int = 3, **kwargs) -> list:
    """SHAP se top N reasons nikalta hai jo score ko sabse zyada badha rahe hain."""
    input_df = _build_input_df(**kwargs)
    shap_values = explainer.shap_values(input_df)[0]

    feature_impact = list(zip(FEATURE_COLUMNS, shap_values))
    # Sirf POSITIVE impact wale features lein (jo score ko badha rahe hain), sabse bara impact pehle
    positive_impact = [f for f in feature_impact if f[1] > 0]
    positive_impact.sort(key=lambda x: x[1], reverse=True)

    reasons = [_friendly(name) for name, _ in positive_impact[:top_n]]
    return reasons


def predict_purchase(**kwargs) -> dict:
    score_kwargs = {k: v for k, v in kwargs.items()}
    score = calculate_intent_score(**score_kwargs)
    reasons = get_top_reasons(**score_kwargs)
    is_likely_buyer = (score / 100) >= THRESHOLD
    return {
        "intent_score": score,
        "reasons": reasons,
        "will_purchase": bool(is_likely_buyer),
        "threshold_used": THRESHOLD
    }