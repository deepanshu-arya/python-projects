# -------------------------------------------------------------
# Project: HealthRisk Analyzer (Predictive API Model)
# Description: Predict health risk (demo model) via a FastAPI ML endpoint
# Author: Deepanshu
# -------------------------------------------------------------

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import Dict, Any
import numpy as np
import pickle
import os
from sklearn.linear_model import LogisticRegression

# =============================================================
# App initialization & metadata
# =============================================================
app = FastAPI(
    title="HealthRisk Analyzer API",
    version="1.1.0",
    description="A demonstration API that predicts simple health risk (e.g., diabetes-like risk) "
                "using a logistic regression model. Uses a tiny synthetic dataset for demo purposes."
)

MODEL_FILE = "health_model.pkl"
MODEL_VERSION = "v1"

# =============================================================
# Data model (input validation)
# =============================================================
class HealthData(BaseModel):
    """Input schema for health prediction."""
    age: int = Field(..., ge=0, le=120, description="Age of the patient in years")
    bmi: float = Field(..., gt=0, le=80, description="Body Mass Index")
    glucose: float = Field(..., gt=0, le=500, description="Blood glucose level (mg/dL)")
    blood_pressure: float = Field(..., gt=0, le=300, description="Systolic blood pressure (mmHg)")
    insulin: float = Field(..., ge=0, le=1000, description="Insulin level (µIU/mL)")

    @validator("age")
    def age_reasonable(cls, v):
        if v < 1:
            raise ValueError("Age must be at least 1 year.")
        return v

# =============================================================
# Utility functions (logging, training, load/save)
# =============================================================
def log(msg: str) -> None:
    """Simple timestamped console logger."""
    from datetime import datetime
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def train_model() -> LogisticRegression:
    """
    Train a tiny LogisticRegression model on synthetic demo data.
    Returns the trained model and saves it to disk.
    """
    log("Training new demo model (synthetic data).")
    # Synthetic/dummy dataset for demonstration only
    X = np.array([
        [25, 22.0, 85, 70, 90],
        [45, 30.5, 130, 85, 120],
        [35, 26.0, 110, 80, 100],
        [55, 32.0, 150, 90, 130],
        [60, 34.0, 160, 95, 140],
        [50, 29.0, 140, 88, 125],
        [30, 24.0, 95, 72, 95],
        [40, 28.5, 120, 82, 110]
    ])
    y = np.array([0, 1, 0, 1, 1, 1, 0, 1])  # 0 = Low risk, 1 = High risk

    model = LogisticRegression(random_state=42, solver="lbfgs", max_iter=200)
    model.fit(X, y)

    try:
        with open(MODEL_FILE, "wb") as f:
            pickle.dump({"model": model, "version": MODEL_VERSION}, f)
        log(f"Model saved to {MODEL_FILE}")
    except Exception as e:
        log(f"Warning: failed to save model file: {e}")

    return model

def load_model() -> LogisticRegression:
    """Load model from disk or train a new one if missing or corrupted."""
    if os.path.exists(MODEL_FILE):
        try:
            with open(MODEL_FILE, "rb") as f:
                payload = pickle.load(f)
                model = payload.get("model")
                ver = payload.get("version", "unknown")
                log(f"Loaded model from {MODEL_FILE} (version {ver})")
                return model
        except Exception as e:
            log(f"Failed to load model file ({MODEL_FILE}): {e}. Retraining a new model.")
            # fall through to training
    # Train and return a fresh model
    return train_model()

# Load or train model at startup
model = load_model()

# =============================================================
# Helper: prediction routine
# =============================================================
def predict_risk(data: HealthData) -> Dict[str, Any]:
    """
    Predict risk using the loaded model.
    Returns prediction label and probability for transparency.
    """
    try:
        features = np.array([[data.age, data.bmi, data.glucose, data.blood_pressure, data.insulin]])
        pred = model.predict(features)[0]
        prob = None
        # predict_proba may not be available for all models, but works for LogisticRegression
        if hasattr(model, "predict_proba"):
            prob_arr = model.predict_proba(features)[0]
            prob = float(round(prob_arr[pred], 4))
        label = "High Risk" if int(pred) == 1 else "Low Risk"
        return {"label": label, "probability": prob}
    except Exception as e:
        log(f"Prediction error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Prediction failed: {e}")

# =============================================================
# Routes / Endpoints
# =============================================================
@app.get("/", tags=["Root"])
def root():
    """Basic root endpoint."""
    return {
        "message": "Welcome to HealthRisk Analyzer API 🚀",
        "model_version": MODEL_VERSION,
        "note": "This demo uses a synthetic dataset and is for learning purposes only."
    }

@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint to verify service status."""
    return {"status": "ok", "model_loaded": model is not None}

@app.post("/predict", tags=["Prediction"], status_code=status.HTTP_200_OK)
def predict(data: HealthData):
    """
    Predict health risk based on submitted features.

    Returns:
      - input_data: echo of input
      - predicted_risk: 'High Risk' or 'Low Risk'
      - probability: confidence score (if available)
      - model_version: version of the model used
    """
    result = predict_risk(data)
    return {
        "input_data": data.dict(),
        "predicted_risk": result["label"],
        "probability": result["probability"],
        "model_version": MODEL_VERSION
    }

@app.post("/retrain", tags=["Admin"], status_code=status.HTTP_200_OK)
def retrain_model():
    """
    (Admin) Retrain the demo model. This endpoint retrains on the synthetic dataset
    and overwrites the saved model file.
    """
    global model
    try:
        model = train_model()
        return {"message": "Model retrained successfully", "model_version": MODEL_VERSION}
    except Exception as e:
        log(f"Retrain failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Retrain failed: {e}")

# =============================================================
# Developer Notes:
# - This API is a demo. Do NOT use for real clinical decision-making.
# - For production: use a real dataset, proper preprocessing, model validation,
#   secure model storage, and authentication on admin endpoints.
# =============================================================
