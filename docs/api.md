# API Documentation

## Overview

The Housing ML API provides REST endpoints for housing price prediction with enterprise-grade features including authentication, monitoring, and comprehensive error handling.

## Base URL
```
http://localhost:8000  (local development)
https://api.housing-ml.com  (production)
```

## Authentication

All API endpoints require API key authentication via the `X-API-Key` header.

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/predict
```

## Endpoints

### GET /

Health check endpoint to verify API availability.

**Response:**
```json
{
  "message": "Housing Price Prediction API is running 🚀"
}
```

### GET /health

Comprehensive health check including model status and system information.

**Response:**
```json
{
  "status": "healthy",
  "model_path": "/app/models/xgb_best_model.pkl",
  "service": "housing-api",
  "n_features_expected": 25
}
```

**Error Response:**
```json
{
  "status": "unhealthy",
  "error": "Model not found"
}
```

### POST /predict

Core prediction endpoint for housing price estimation.

**Request Body:**
```json
[
  {
    "date": "2023-01-01",
    "price": 500000,
    "bedrooms": 3,
    "bathrooms": 2,
    "sqft_living": 2000,
    "zipcode": "98101"
  }
]
```

**Parameters:**
- `data` (array): List of property objects
- Each property object should contain housing features

**Response:**
```json
{
  "predictions": [485000.0, 625000.0],
  "actuals": [500000.0, 620000.0]
}
```

**Error Responses:**

400 Bad Request - Empty data
```json
{
  "detail": "No data provided"
}
```

401 Unauthorized - Invalid API key
```json
{
  "detail": "Invalid API Key"
}
```

500 Internal Server Error - Prediction failure
```json
{
  "detail": "Prediction failed"
}
```

### POST /run_batch

Trigger batch prediction job for monthly data processing.

**Response:**
```json
{
  "status": "success",
  "rows_predicted": 1000,
  "output_dir": "data/predictions/"
}
```

### GET /latest_predictions

Retrieve preview of most recent batch predictions.

**Query Parameters:**
- `limit` (int, optional): Number of records to return (default: 5)

**Response:**
```json
{
  "file": "preds_2024-01-15.csv",
  "rows": 1000,
  "preview": [
    {
      "property_id": "12345",
      "predicted_price": 485000.0,
      "actual_price": 500000.0
    }
  ]
}
```

## Data Schema

### Input Property Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| date | string | Yes | Property listing date (YYYY-MM-DD) |
| bedrooms | number | Yes | Number of bedrooms |
| bathrooms | number | Yes | Number of bathrooms |
| sqft_living | number | Yes | Living area in square feet |
| zipcode | string | Yes | Property zipcode |
| price | number | No | Actual sale price (for evaluation) |

### Additional Features

The API automatically processes additional features:
- Date-based features (month, year, day of week)
- Categorical encodings (zipcode frequency, city target encoding)
- Outlier removal and data cleaning

## Rate Limiting

- Default: 100 requests per minute per API key
- Configurable via environment variables
- Returns 429 Too Many Requests when exceeded

## Error Handling

All errors follow REST API conventions with appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid input)
- `401`: Unauthorized (invalid API key)
- `429`: Too Many Requests (rate limited)
- `500`: Internal Server Error (system issues)

## Monitoring

### Health Checks
- `/health` endpoint for load balancer health checks
- Model availability validation
- System resource monitoring

### Logging
- Structured JSON logging for all requests
- Error tracking with full stack traces
- Performance metrics logging

## Examples

### Python Client

```python
import requests

API_URL = "http://localhost:8000/predict"
API_KEY = "your-api-key"
HEADERS = {"X-API-Key": API_KEY}

data = [{
    "date": "2023-06-15",
    "bedrooms": 3,
    "bathrooms": 2.5,
    "sqft_living": 2200,
    "zipcode": "98101"
}]

response = requests.post(API_URL, json=data, headers=HEADERS)
predictions = response.json()
print(f"Predicted price: ${predictions['predictions'][0]:,.0f}")
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '[
       {
         "date": "2023-06-15",
         "bedrooms": 3,
         "bathrooms": 2,
         "sqft_living": 2000,
         "zipcode": "98101"
       }
     ]'
```

## SDKs and Libraries

### Python SDK (Future)
```python
from housing_ml import HousingMLClient

client = HousingMLClient(api_key="your-api-key")
prediction = client.predict_property({
    "date": "2023-06-15",
    "bedrooms": 3,
    "bathrooms": 2,
    "sqft_living": 2000,
    "zipcode": "98101"
})
```

## Support

For API support and issues:
- Check `/health` endpoint for system status
- Review logs for detailed error information
- Contact the development team with request IDs from error responses