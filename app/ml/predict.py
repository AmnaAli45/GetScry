import pickle
import json
import pandas as pd
import os

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "xgb_final_model.pkl")
CONFIG_PATH = os.path.join(BASE_DIR, "model_config.json")
FEATURES_PATH = os.path.join(BASE_DIR, "feature_columns.json")
PCA_PATH = os.path.join(BASE_DIR, "pca_transformer.pkl")

# Sab kuch ek baar load karein (app start hone par)
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)
    THRESHOLD = config["threshold"]

with open(FEATURES_PATH, "r") as f:
    FEATURE_COLUMNS = json.load(f)

with open(PCA_PATH, "rb") as f:
    pca = pickle.load(f)


def calculate_intent_score(
    administrative: int,
    administrative_duration: float,
    informational: int,
    informational_duration: float,
    product_pages: int,          # ProductRelated
    product_duration: float,     # ProductRelated_Duration
    bounce_rates: float,
    exit_rates: float,
    page_values: float,
    special_day: float,
    operating_systems: int,
    browser: int,
    region: int,
    traffic_type: int,
    weekend: bool,
    month: str,          # "Feb", "Mar", "May", "June", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    visitor_type: str,   # "Returning_Visitor", "New_Visitor", "Other"
) -> float:

    # Step 1: PCA transform (exact wahi fitted PCA use karein, naya fit NAHI karna)
    product_engagement_pca = pca.transform(
        [[product_pages, product_duration]]
    )[0][0]

    # Step 2: Raw row banayein (baaki features ke sath)
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

    # Step 3: Exactly wahi one-hot encoding jo training mein hui thi
    input_df = pd.get_dummies(input_df, columns=["Month", "VisitorType"], drop_first=True)

    # Step 4: Training ke exact columns/order ke sath align karein
    input_df = input_df.reindex(columns=FEATURE_COLUMNS, fill_value=0)

    probability = model.predict_proba(input_df)[:, 1][0]
    return round(float(probability) * 100, 2)


def predict_purchase(**kwargs) -> dict:
    score = calculate_intent_score(**kwargs)
    is_likely_buyer = (score / 100) >= THRESHOLD
    return {
        "intent_score": score,
        "will_purchase": bool(is_likely_buyer),
        "threshold_used": THRESHOLD
    }