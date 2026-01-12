# Development Guide

## Overview

This guide covers the development workflow for the Housing ML system, including setup, coding standards, testing, and contribution guidelines.

## Prerequisites

### System Requirements
- **Python**: 3.13 or higher
- **Package Manager**: uv (recommended) or pip
- **Container Runtime**: Docker
- **Git**: For version control
- **AWS CLI**: For cloud development

### Development Tools
```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install development dependencies
make install
```

## Project Setup

### 1. Clone and Setup
```bash
git clone <repository-url>
cd housing-ml

# Install dependencies
make install

# Copy environment template
cp .env.example .env
```

### 2. Environment Configuration

Edit `.env` file with your local configuration:

```bash
# Application
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# AWS (use your credentials)
AWS_REGION=ap-south-1
S3_BUCKET=housing-data-artifacts

# API
API_HOST=0.0.0.0
API_PORT=8000

# Development
API_KEY=dev-api-key-123
```

### 3. Data Setup

Download required datasets and models:
```bash
# Download Kaggle dataset (if not already present)
kaggle datasets download -d your-dataset

# Ensure model files are in models/ directory
ls models/
# xgb_best_model.pkl
# freq_encoder.pkl
# target_encoder.pkl
```

## Development Workflow

### Local Development

#### Start All Services
```bash
make run-compose
```

This starts:
- **API Service**: http://localhost:8000
- **Dashboard**: http://localhost:8501
- **Documentation**: http://localhost:8000/docs

#### Individual Service Development

```bash
# API only
make run

# Dashboard only
make run-dashboard
```

### Code Quality

#### Formatting and Linting
```bash
# Format code
make format

# Lint code
make lint

# Run both
make format lint
```

#### Pre-commit Hooks (Recommended)
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

### Testing

#### Run Test Suite
```bash
# Run all tests
make test

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest test/test_api.py

# Run tests in watch mode
uv run pytest-watch
```

#### Test Structure
```
test/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── test_api.py             # API endpoint tests
├── test_inference.py       # ML inference tests
├── test_features.py        # Feature engineering tests
├── test_training.py        # Model training tests
├── integration/            # Integration tests
└── fixtures/               # Test data fixtures
```

## Code Organization

### Directory Structure
```
housing-ml/
├── src/                    # Source code
│   ├── api/               # FastAPI application
│   ├── config/            # Configuration management
│   ├── inference_pipeline/ # ML inference logic
│   ├── model_training/    # Training pipelines
│   ├── utils/             # Shared utilities
│   └── batch/             # Batch processing
├── test/                  # Test suite
├── docs/                  # Documentation
├── models/                # Trained models
├── notebooks/             # Jupyter notebooks
└── scripts/               # Utility scripts
```

### Coding Standards

#### Python Style Guide
- **PEP 8** compliance
- **Black** for code formatting (line length: 88)
- **isort** for import sorting
- **flake8** for linting

#### Naming Conventions
```python
# Classes
class HousingPricePredictor:
    pass

# Functions
def predict_housing_price(data: dict) -> float:
    pass

# Variables
housing_data = load_data()
predicted_prices = model.predict(features)

# Constants
MAX_RETRY_ATTEMPTS = 3
DEFAULT_MODEL_PATH = "models/xgb_model.pkl"
```

#### Type Hints
```python
from typing import List, Dict, Optional, Any
from pathlib import Path

def process_data(
    input_path: Path,
    output_format: str = "parquet"
) -> pd.DataFrame:
    pass
```

#### Docstrings
```python
def predict_price(
    features: Dict[str, Any],
    model_version: Optional[str] = None
) -> float:
    """
    Predict housing price using trained model.

    Args:
        features: Dictionary of property features
        model_version: Optional model version to use

    Returns:
        Predicted price as float

    Raises:
        ModelNotFoundError: If specified model version not found
        PredictionError: If prediction fails

    Example:
        >>> features = {"bedrooms": 3, "bathrooms": 2, "sqft": 2000}
        >>> price = predict_price(features)
        >>> print(f"${price:,.0f}")
        $485,000
    """
    pass
```

## API Development

### Adding New Endpoints

1. **Define endpoint in `src/api/main.py`**:
```python
@app.post("/batch_predict")
def batch_predict(data: List[Dict[str, Any]], api_key: str = Depends(get_api_key)):
    """Batch prediction endpoint."""
    # Implementation
    pass
```

2. **Add comprehensive logging**:
```python
logger.info("Batch prediction request", batch_size=len(data))
```

3. **Handle errors properly**:
```python
try:
    # Prediction logic
    pass
except Exception as e:
    logger.error("Batch prediction failed", error=str(e))
    raise HTTPException(status_code=500, detail="Batch prediction failed")
```

4. **Add tests in `test/test_api.py`**:
```python
def test_batch_predict(client, auth_headers):
    response = client.post("/batch_predict", json=test_data, headers=auth_headers)
    assert response.status_code == 200
```

### Request/Response Models

Use Pydantic models for type safety:

```python
from pydantic import BaseModel
from typing import List

class PropertyFeatures(BaseModel):
    date: str
    bedrooms: int
    bathrooms: float
    sqft_living: int
    zipcode: str

class PredictionRequest(BaseModel):
    properties: List[PropertyFeatures]

class PredictionResponse(BaseModel):
    predictions: List[float]
    model_version: str
```

## ML Pipeline Development

### Adding New Features

1. **Update preprocessing in `src/feature_pipeline/preprocess.py`**
2. **Add feature engineering in `src/feature_pipeline/feature_engineering.py`**
3. **Update inference pipeline in `src/inference_pipeline/inference.py`**
4. **Retrain models with new features**
5. **Update tests and validation**

### Model Versioning

```python
# Use MLflow for model versioning (future enhancement)
import mlflow

with mlflow.start_run():
    # Train model
    model = train_model(X_train, y_train)

    # Log model
    mlflow.sklearn.log_model(model, "model")

    # Register model
    mlflow.register_model(
        f"runs:/{mlflow.active_run().info.run_id}/model",
        "housing-price-model"
    )
```

## Testing Strategy

### Unit Tests
```python
import pytest
from src.inference_pipeline.inference import predict

def test_predict_valid_input():
    """Test prediction with valid input."""
    test_data = pd.DataFrame({
        "bedrooms": [3],
        "bathrooms": [2],
        "sqft_living": [2000],
        "zipcode": ["98101"]
    })

    result = predict(test_data)
    assert "predicted_price" in result.columns
    assert len(result) == 1
```

### Integration Tests
```python
def test_api_predict_endpoint(client, auth_headers):
    """Test full API prediction flow."""
    test_payload = [{
        "date": "2023-01-01",
        "bedrooms": 3,
        "bathrooms": 2,
        "sqft_living": 2000,
        "zipcode": "98101"
    }]

    response = client.post("/predict", json=test_payload, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert "predictions" in data
    assert len(data["predictions"]) == 1
```

### Performance Tests
```python
import time

def test_prediction_performance():
    """Test prediction latency."""
    test_data = generate_large_dataset(1000)

    start_time = time.time()
    result = predict(test_data)
    end_time = time.time()

    latency = end_time - start_time
    assert latency < 5.0  # Should complete within 5 seconds
```

## Debugging

### Local Debugging

#### API Debugging
```bash
# Run with reload
uv run uvicorn src.api.main:app --reload --log-level debug

# Check health
curl http://localhost:8000/health

# Test prediction
curl -X POST "http://localhost:8000/predict" \
     -H "X-API-Key: dev-api-key-123" \
     -H "Content-Type: application/json" \
     -d '[{"bedrooms": 3, "bathrooms": 2, "sqft_living": 2000, "zipcode": "98101"}]'
```

#### Dashboard Debugging
```bash
# Run with debug logging
streamlit run app.py --logger.level=debug

# Check API connectivity
curl http://localhost:8000/predict
```

### Logging

#### View Application Logs
```bash
# API logs
docker-compose logs api

# Dashboard logs
docker-compose logs dashboard

# All logs
docker-compose logs
```

#### Structured Logging
```python
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# Info logging
logger.info("Processing prediction", user_id="123", property_count=5)

# Error logging with context
try:
    result = risky_operation()
except Exception as e:
    logger.error("Operation failed", error=str(e), user_id="123", exc_info=True)
```

## Performance Optimization

### Profiling
```python
import cProfile
import pstats

def profile_prediction():
    """Profile prediction performance."""
    profiler = cProfile.Profile()
    profiler.enable()

    # Run prediction
    predict(test_data)

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats(20)  # Top 20 functions
```

### Memory Optimization
```python
# Use chunked processing for large datasets
def predict_batch_chunked(data: pd.DataFrame, chunk_size: int = 1000):
    """Process predictions in chunks to manage memory."""
    results = []

    for i in range(0, len(data), chunk_size):
        chunk = data.iloc[i:i + chunk_size]
        chunk_result = predict(chunk)
        results.append(chunk_result)

    return pd.concat(results, ignore_index=True)
```

## Contributing

### Pull Request Process

1. **Create Feature Branch**
```bash
git checkout -b feature/new-prediction-endpoint
```

2. **Make Changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

3. **Run Quality Checks**
```bash
make format lint test
```

4. **Commit Changes**
```bash
git add .
git commit -m "feat: add batch prediction endpoint

- Add /batch_predict endpoint
- Support up to 1000 properties per request
- Add comprehensive error handling
- Update API documentation"
```

5. **Create Pull Request**
   - Provide clear description
   - Reference related issues
   - Request review from team members

### Code Review Checklist

- [ ] **Functionality**: Code works as expected
- [ ] **Tests**: Adequate test coverage
- [ ] **Documentation**: Updated docs and docstrings
- [ ] **Style**: Follows coding standards
- [ ] **Performance**: No performance regressions
- [ ] **Security**: No security vulnerabilities

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Reinstall dependencies
make clean
make install
```

#### Docker Issues
```bash
# Clean Docker
docker system prune -a

# Rebuild images
make build
```

#### Model Loading Issues
```bash
# Check model files
ls -la models/

# Verify model integrity
python -c "import joblib; joblib.load('models/xgb_best_model.pkl')"
```

#### Port Conflicts
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

## Resources

### Documentation
- [API Documentation](api.md)
- [Architecture Guide](architecture.md)
- [Deployment Guide](deployment.md)

### Tools
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Settings](https://pydantic-settings.readthedocs.io/)
- [Structlog Documentation](https://www.structlog.org/)

### Related Projects
- [MLflow](https://mlflow.org/) - Model management
- [Great Expectations](https://greatexpectations.io/) - Data validation
- [Evidently](https://evidentlyai.com/) - ML monitoring