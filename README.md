# Housing ML - Enterprise-Grade MLOps Project

A production-ready machine learning system for housing price prediction with enterprise-grade features including centralized configuration, structured logging, authentication, and comprehensive error handling.

## Features

- **ML Pipeline**: Complete ML pipeline with data preprocessing, feature engineering, model training, and inference
- **API Service**: FastAPI-based REST API for real-time predictions
- **Dashboard**: Streamlit-based web dashboard for model interaction
- **Configuration Management**: Pydantic-based centralized configuration with environment variable support
- **Logging**: Structured logging with JSON output for production
- **Authentication**: API key-based authentication for secure access
- **Error Handling**: Comprehensive exception handling with custom error types
- **CI/CD**: GitHub Actions for automated testing and deployment to AWS ECS
- **Containerization**: Multi-service Docker setup for API and dashboard
- **Code Quality**: Linting, formatting, and testing tools

## Project Structure

```
housing-ml/
├── src/
│   ├── api/                 # FastAPI application
│   ├── batch/               # Batch processing jobs
│   ├── config/              # Configuration management
│   ├── feature_pipeline/    # Data preprocessing and feature engineering
│   ├── inference_pipeline/  # Model inference logic
│   ├── model_training/      # Model training and evaluation
│   └── utils/               # Utilities (logging, exceptions)
├── test/                    # Unit and integration tests
├── models/                  # Trained models and encoders
├── notebooks/               # Jupyter notebooks for experimentation
├── .github/workflows/       # CI/CD pipelines
├── Dockerfile               # API service container
├── Dockerfile.streamlit     # Dashboard container
├── docker-compose.yml       # Local development setup
├── pyproject.toml           # Project dependencies and configuration
├── Makefile                 # Common development tasks
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.13+
- uv (Python package manager)
- Docker (for containerized deployment)
- AWS CLI (for cloud deployment)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd housing-ml
```

2. Install dependencies:
```bash
make install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Development

1. Run both services locally with docker-compose:
```bash
make run-compose
```

2. Or run the API locally:
```bash
make run
```

3. Run the dashboard locally:
```bash
make run-dashboard
```

2. Run tests:
```bash
make test
```

3. Format code:
```bash
make format
```

4. Lint code:
```bash
make lint
```

## API Usage

### Authentication

All API endpoints require an API key in the `X-API-Key` header.

### Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /predict` - Real-time predictions
- `POST /run_batch` - Trigger batch predictions
- `GET /latest_predictions` - Get latest batch predictions

### Example Prediction Request

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '[
       {
         "date": "2023-01-01",
         "price": 500000,
         "bedrooms": 3,
         "bathrooms": 2,
         "sqft_living": 2000,
         "zipcode": "98101"
       }
     ]'
```

## Configuration

The application uses Pydantic settings for configuration. Key settings include:

- `ENVIRONMENT`: development/production
- `AWS_REGION`: AWS region for S3 and ECS
- `S3_BUCKET`: S3 bucket for model artifacts
- `API_KEY`: API key for authentication
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)

## Deployment

### Local Development

```bash
make build
make run
```

### Production Deployment

The project includes GitHub Actions for automated deployment to AWS ECS:

1. Push to `main` branch
2. GitHub Actions builds and pushes Docker images
3. Deploys to ECS cluster

### Environment Variables

For production, set the following environment variables:

- `ENVIRONMENT=production`
- `AWS_REGION=ap-south-1`
- `S3_BUCKET=housing-data-artifacts`
- `API_KEY=<secure-api-key>`
- `LOG_LEVEL=INFO`

## Monitoring

- Structured logging with JSON output in production
- Health check endpoints for monitoring
- Error tracking with detailed exception information

## Security

- API key authentication
- Input validation and sanitization
- Secure configuration management
- No hardcoded secrets

## Documentation

- **[Architecture Guide](docs/architecture.md)** - System design and components
- **[API Documentation](docs/api.md)** - Complete API reference
- **[Deployment Guide](docs/deployment.md)** - Production deployment instructions
- **[Development Guide](docs/development.md)** - Development workflow and standards

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Use `make format` and `make lint` before committing

## License

[Add your license here]