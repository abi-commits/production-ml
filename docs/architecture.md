# System Architecture

## Overview

The Housing ML system is a production-ready machine learning platform for housing price prediction, built with enterprise-grade architecture and best practices.

## Architecture Components

### Core Services

#### 1. API Service (`src/api/main.py`)
- **Framework**: FastAPI
- **Purpose**: REST API for real-time predictions
- **Features**:
  - API key authentication
  - Health monitoring endpoints
  - Structured logging
  - Error handling with proper HTTP status codes

#### 2. Dashboard Service (`app.py`)
- **Framework**: Streamlit
- **Purpose**: Web interface for model interaction
- **Features**:
  - Property data input forms
  - Real-time prediction display
  - API integration with authentication

#### 3. ML Pipeline (`src/inference_pipeline/`)
- **Components**:
  - Data preprocessing (`preprocess.py`)
  - Feature engineering (`feature_engineering.py`)
  - Model inference (`inference.py`)
- **Features**:
  - Consistent preprocessing between training/inference
  - Encoder management
  - Feature alignment

### Supporting Infrastructure

#### Configuration Management (`src/config/settings.py`)
- **Technology**: Pydantic Settings
- **Features**:
  - Environment variable binding
  - Type validation
  - Computed properties for paths
  - Environment-specific configurations

#### Logging System (`src/utils/logging_config.py`)
- **Technology**: Structlog + Python logging
- **Features**:
  - Structured JSON logging for production
  - Human-readable logging for development
  - Configurable log levels
  - Context-aware logging

#### Error Handling (`src/utils/exceptions.py`)
- **Custom Exceptions**:
  - `HousingMLError`: Base exception
  - `ModelNotFoundError`: Model loading failures
  - `InvalidInputError`: Input validation failures
  - `PredictionError`: ML prediction failures

## Data Flow

```
Raw Input → API Service → Inference Pipeline → Prediction → Response
    ↓           ↓              ↓                    ↓
Validation → Auth Check → Preprocessing → Model → Formatting
```

## Deployment Architecture

### Local Development
```
docker-compose.yml
├── API Service (port 8000)
└── Dashboard Service (port 8501)
```

### Production (AWS)
```
AWS ECS Cluster
├── housing-api service
│   ├── Task Definition
│   ├── Load Balancer
│   └── Auto Scaling
└── housing-streamlit service
    ├── Task Definition
    ├── Load Balancer
    └── Auto Scaling
```

## Security Architecture

### Authentication
- API key-based authentication for API endpoints
- Environment variable-based secrets management
- No hardcoded credentials

### Data Protection
- Input validation and sanitization
- Secure S3 integration for model artifacts
- Environment-specific configuration

## Monitoring & Observability

### Health Checks
- `/health` endpoint for service status
- Model availability validation
- Dependency health monitoring

### Logging
- Structured logging with context
- Error tracking with stack traces
- Performance monitoring logs

### Metrics (Future Enhancement)
- Prediction latency tracking
- Error rate monitoring
- Model performance metrics

## Scalability Considerations

### Horizontal Scaling
- Stateless API services
- Independent service scaling
- Load balancer distribution

### Performance Optimization
- Model caching and lazy loading
- Efficient data preprocessing
- Optimized Docker images

## Development Workflow

### Local Development
1. `make install` - Install dependencies
2. `make run-compose` - Start all services
3. `make test` - Run test suite
4. `make format` - Code formatting

### CI/CD Pipeline
1. Code quality checks (linting, formatting)
2. Security scanning
3. Automated testing
4. Docker image building
5. Deployment to staging/production

## Technology Stack

### Core Technologies
- **Python 3.13+**: Primary language
- **FastAPI**: API framework
- **Streamlit**: Dashboard framework
- **Pandas/Polars**: Data processing
- **Scikit-learn/XGBoost**: ML libraries

### Infrastructure
- **Docker**: Containerization
- **AWS ECS**: Container orchestration
- **S3**: Model artifact storage
- **ECR**: Container registry

### Development Tools
- **uv**: Python package management
- **Black/isort/flake8**: Code quality
- **Pytest**: Testing framework
- **Makefile**: Development automation

## Configuration Management

### Environment Variables
```bash
# Application
ENVIRONMENT=production
LOG_LEVEL=INFO

# AWS
AWS_REGION=eu-west-2
S3_BUCKET=housing-data-artifacts

# API
API_HOST=0.0.0.0
API_PORT=8000

# Security
API_KEY=your-secure-api-key
```

### Configuration Files
- `.env`: Local environment variables
- `pyproject.toml`: Python project configuration
- `docker-compose.yml`: Local service orchestration