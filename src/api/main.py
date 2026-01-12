"""
Housing ML API Service

A FastAPI-based REST API for housing price prediction with enterprise-grade features:
- Centralized configuration management
- Structured logging
- API key authentication
- Comprehensive error handling
- Health monitoring
"""

import os
from pathlib import Path
from typing import Any, Dict, List

import boto3
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader

# Import configuration, logging, and exceptions
from src.batch.run_batch import run_monthly_predictions
from src.config.settings import settings
from src.inference_pipeline.inference import predict
from src.utils.logging_config import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key(api_key: str = Depends(api_key_header)) -> str:
    """
    Validate API key for authentication.

    Args:
        api_key: API key from request header

    Returns:
        Validated API key

    Raises:
        HTTPException: If API key is invalid
    """
    if not api_key or api_key != settings.api_key:
        logger.warning("Invalid API key attempt")
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key


# ----------------------------
# Config
# ----------------------------
s3 = boto3.client("s3", region_name=settings.aws_region)


# Ensures your app always has the latest model/data locally,
# but avoids re-downloading every time it starts.
def load_from_s3(key, local_path):
    """Download from S3 if not already cached locally."""
    local_path = Path(local_path)
    if not local_path.exists():
        os.makedirs(local_path.parent, exist_ok=True)
        logger.info("Downloading from S3", key=key, local_path=str(local_path))
        s3.download_file(settings.s3_bucket, key, str(local_path))
    return str(local_path)


# ----------------------------
# Paths
# ----------------------------
# Downloads model + training features from S3 if not cached.
MODEL_PATH = Path(
    load_from_s3(f"models/{settings.model_name}", str(settings.model_path))
)
TRAIN_FE_PATH = Path(
    load_from_s3(
        f"processed/{settings.train_features_file}", str(settings.train_features_path)
    )
)

# Load expected training features for alignment
if TRAIN_FE_PATH.exists():
    _train_cols = pd.read_csv(TRAIN_FE_PATH, nrows=1)
    TRAIN_FEATURE_COLUMNS = [c for c in _train_cols.columns if c != "price"]
else:
    TRAIN_FEATURE_COLUMNS = None


# Initialize FastAPI app
app = FastAPI(
    title="Housing Price Prediction API",
    description="Enterprise-grade ML API for housing price prediction",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/")
def root() -> Dict[str, str]:
    """
    Root endpoint to confirm API is running.

    Returns:
        Dict with status message
    """
    return {"message": "Housing Price Prediction API is running 🚀"}


@app.get("/health")
def health() -> Dict[str, Any]:
    """
    Health check endpoint that validates model availability and system status.

    Returns:
        Dict containing health status and system information
    """
    status: Dict[str, Any] = {
        "status": "healthy",
        "model_path": str(MODEL_PATH),
        "service": "housing-api",
    }

    if not MODEL_PATH.exists():
        status["status"] = "unhealthy"
        status["error"] = "Model not found"
        logger.error("Health check failed: model not found")
    else:
        logger.info("Health check passed")
        if TRAIN_FEATURE_COLUMNS:
            status["n_features_expected"] = len(TRAIN_FEATURE_COLUMNS)

    return status


@app.post("/predict")
def predict_batch(
    data: List[Dict[str, Any]], api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Core ML prediction endpoint for housing price estimation.

    Args:
        data: List of property data dictionaries
        api_key: Validated API key (dependency injection)

    Returns:
        Dict containing predictions and optional actual prices

    Raises:
        HTTPException: For invalid input or prediction failures
    """
    logger.info("Prediction request received", num_records=len(data))

    if not MODEL_PATH.exists():
        logger.error("Model not found", model_path=str(MODEL_PATH))
        raise HTTPException(
            status_code=500, detail=f"Model not found at {str(MODEL_PATH)}"
        )

    df = pd.DataFrame(data)
    if df.empty:
        logger.warning("Empty data provided")
        raise HTTPException(status_code=400, detail="No data provided")

    try:
        preds_df = predict(
            df,
            model_path=settings.model_path,
            freq_encoder_path=settings.freq_encoder_path,
            target_encoder_path=settings.target_encoder_path,
        )

        resp = {"predictions": preds_df["predicted_price"].astype(float).tolist()}
        if "actual_price" in preds_df.columns:
            resp["actuals"] = preds_df["actual_price"].astype(float).tolist()

        logger.info("Prediction completed", num_predictions=len(resp["predictions"]))
        return resp

    except Exception as e:
        logger.error("Prediction failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction failed")


# Trigger a monthly batch job via API.
@app.post("/run_batch")
def run_batch():
    preds = run_monthly_predictions()
    return {
        "status": "success",
        "rows_predicted": int(len(preds)),
        "output_dir": "data/predictions/",
    }


# Returns a preview of the most recent batch predictions.
@app.get("/latest_predictions")
def latest_predictions(limit: int = 5):
    pred_dir = settings.predictions_path
    files = sorted(pred_dir.glob("preds_*.csv"))
    if not files:
        return {"error": "No predictions found"}

    latest_file = files[-1]
    df = pd.read_csv(latest_file)
    return {
        "file": latest_file.name,
        "rows": int(len(df)),
        "preview": df.head(limit).to_dict(orient="records"),
    }


"""
🔹 Execution Order / Module Flow

1. Imports (FastAPI, pandas, boto3, your inference function).
2. Config setup (env vars → bucket/region).
3. S3 utility (load_from_s3).
4. Download + load model/artifacts (MODEL_PATH, TRAIN_FE_PATH).
5. Infer schema (TRAIN_FEATURE_COLUMNS).
6. Create FastAPI app (app = FastAPI).
7. Declare endpoints (/, /health, /predict, /run_batch, /latest_predictions).
"""
