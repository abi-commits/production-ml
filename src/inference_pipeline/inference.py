"""
Inference Pipeline for Housing Price Prediction

This module handles the complete ML inference workflow:
- Raw input preprocessing and cleaning
- Feature engineering with saved encoders
- Feature alignment with training schema
- Model prediction and result formatting

The pipeline ensures consistent preprocessing between training and inference.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from joblib import load

# Import configuration, logging, and exceptions
from src.config.settings import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

from src.feature_pipeline.feature_engineering import (add_date_features,
                                                      drop_unused_columns)
# Import preprocessing + feature engineering helpers
from src.feature_pipeline.preprocess import (clean_and_merge, drop_duplicates,
                                             remove_outliers)

# ----------------------------
# Default paths
# ----------------------------
DEFAULT_MODEL = settings.model_path
DEFAULT_FREQ_ENCODER = settings.freq_encoder_path
DEFAULT_TARGET_ENCODER = settings.target_encoder_path
TRAIN_FE_PATH = settings.train_features_path
DEFAULT_OUTPUT = settings.predictions_path / "predictions.csv"


# Load training feature columns (strict schema from training dataset)
if TRAIN_FE_PATH.exists():
    _train_cols = pd.read_csv(TRAIN_FE_PATH, nrows=1)
    TRAIN_FEATURE_COLUMNS = [
        c for c in _train_cols.columns if c != "price"
    ]  # excluding price column
else:
    TRAIN_FEATURE_COLUMNS = None


# ----------------------------
# Core inference function
# ----------------------------
def predict(
    input_df: pd.DataFrame,
    model_path: Path | str = DEFAULT_MODEL,
    freq_encoder_path: Path | str = DEFAULT_FREQ_ENCODER,
    target_encoder_path: Path | str = DEFAULT_TARGET_ENCODER,
) -> pd.DataFrame:
    """
    Execute the complete inference pipeline for housing price prediction.

    Args:
        input_df: Raw input data as pandas DataFrame
        model_path: Path to trained model file
        freq_encoder_path: Path to frequency encoder pickle
        target_encoder_path: Path to target encoder pickle

    Returns:
        DataFrame with predictions and optional actual prices

    Raises:
        ModelNotFoundError: If model file cannot be loaded
        PredictionError: If prediction fails
    """
    logger.info("Starting inference", input_shape=input_df.shape)

    # Step 1: Preprocess raw input
    df = clean_and_merge(input_df)
    df = drop_duplicates(df)
    df = remove_outliers(df)
    logger.info("Preprocessing completed", processed_shape=df.shape)

    # Step 2: Feature engineering
    if "date" in df.columns:
        df = add_date_features(df)
        logger.info("Date features added")

    # Step 3: Encodings ----------------
    # Frequency encoding (zipcode)
    if Path(freq_encoder_path).exists() and "zipcode" in df.columns:
        freq_map = load(freq_encoder_path)
        df["zipcode_freq"] = df["zipcode"].map(freq_map).fillna(0)
        df = df.drop(columns=["zipcode"], errors="ignore")
        logger.info("Frequency encoding applied")

    # Target encoding (city_full → city_full_encoded)
    if Path(target_encoder_path).exists() and "city_full" in df.columns:
        target_encoder = load(target_encoder_path)
        df["city_full_encoded"] = target_encoder.transform(df["city_full"])
        df = df.drop(columns=["city_full"], errors="ignore")
        logger.info("Target encoding applied")

    # Drop leakage columns
    df, _ = drop_unused_columns(df.copy(), df.copy())

    # Step 4: Separate actuals if present
    y_true = None
    if "price" in df.columns:
        y_true = df["price"].tolist()
        df = df.drop(columns=["price"])

    # Step 5: Align columns with training schema
    if TRAIN_FEATURE_COLUMNS is not None:
        df = df.reindex(columns=TRAIN_FEATURE_COLUMNS, fill_value=0)
        logger.info(
            "Features aligned with training schema",
            num_features=len(TRAIN_FEATURE_COLUMNS),
        )

    # Step 6: Load model & predict
    try:
        model = load(model_path)
        preds = model.predict(df)
        logger.info("Predictions generated", num_predictions=len(preds))
    except FileNotFoundError:
        logger.error("Model file not found", model_path=str(model_path))
        raise ModelNotFoundError(f"Model not found at {model_path}")
    except Exception as e:
        logger.error("Prediction failed", error=str(e))
        raise PredictionError(f"Prediction failed: {str(e)}")

    # Step 7: Build output
    out = df.copy()
    out["predicted_price"] = preds
    if y_true is not None:
        out["actual_price"] = y_true

    logger.info("Inference completed")
    return out


# ----------------------------
# CLI entrypoint
# ----------------------------
# Allows running inference directly from terminal.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run inference on new housing data (raw)."
    )
    parser.add_argument(
        "--input", type=str, required=True, help="Path to input RAW CSV file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(DEFAULT_OUTPUT),
        help="Path to save predictions CSV",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=str(DEFAULT_MODEL),
        help="Path to trained model file",
    )
    parser.add_argument(
        "--freq_encoder",
        type=str,
        default=str(DEFAULT_FREQ_ENCODER),
        help="Path to frequency encoder pickle",
    )
    parser.add_argument(
        "--target_encoder",
        type=str,
        default=str(DEFAULT_TARGET_ENCODER),
        help="Path to target encoder pickle",
    )

    args = parser.parse_args()

    raw_df = pd.read_csv(args.input)
    preds_df = predict(
        raw_df,
        model_path=args.model,
        freq_encoder_path=args.freq_encoder,
        target_encoder_path=args.target_encoder,
    )

    preds_df.to_csv(args.output, index=False)
    print(f"✅ Predictions saved to {args.output}")
