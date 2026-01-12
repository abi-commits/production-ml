"""
Centralized Configuration Management

This module provides application-wide configuration using Pydantic settings.
All configuration is loaded from environment variables with sensible defaults.

Features:
- Environment variable binding
- Type validation
- Computed properties for paths
- Support for .env files
"""

from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # AWS Configuration
    aws_region: str = Field(default="ap-south-1", alias="AWS_REGION")
    s3_bucket: str = Field(default="housing-data-artifacts", alias="S3_BUCKET")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_workers: int = Field(default=1, alias="API_WORKERS")

    # Model Configuration
    model_name: str = Field(default="xgb_best_model.pkl", alias="MODEL_NAME")
    freq_encoder_name: str = Field(
        default="freq_encoder.pkl", alias="FREQ_ENCODER_NAME"
    )
    target_encoder_name: str = Field(
        default="target_encoder.pkl", alias="TARGET_ENCODER_NAME"
    )
    train_features_file: str = Field(
        default="feature_engineered_train.csv", alias="TRAIN_FEATURES_FILE"
    )

    # Paths
    project_root: Path = Field(default=Path(__file__).resolve().parents[2])
    models_dir: str = Field(default="models")
    data_dir: str = Field(default="data")
    predictions_dir: str = Field(default="data/predictions")

    # MLflow Configuration
    mlflow_tracking_uri: str = Field(
        default="http://localhost:5000", alias="MLFLOW_TRACKING_URI"
    )
    mlflow_experiment_name: str = Field(
        default="housing_regression", alias="MLFLOW_EXPERIMENT_NAME"
    )

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Security
    secret_key: str = Field(default="your-secret-key-here", alias="SECRET_KEY")
    api_key: str = Field(default="", alias="API_KEY")  # For simple auth

    # Monitoring
    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")

    @computed_field
    @property
    def model_path(self) -> Path:
        """Full path to the model file."""
        return self.project_root / self.models_dir / self.model_name

    @computed_field
    @property
    def freq_encoder_path(self) -> Path:
        """Full path to the frequency encoder."""
        return self.project_root / self.models_dir / self.freq_encoder_name

    @computed_field
    @property
    def target_encoder_path(self) -> Path:
        """Full path to the target encoder."""
        return self.project_root / self.models_dir / self.target_encoder_name

    @computed_field
    @property
    def train_features_path(self) -> Path:
        """Full path to the training features file."""
        return (
            self.project_root / self.data_dir / "processed" / self.train_features_file
        )

    @computed_field
    @property
    def predictions_path(self) -> Path:
        """Directory for predictions."""
        return self.project_root / self.predictions_dir

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
