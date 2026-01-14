# Production ML – Housing Price Prediction

A production-ready machine learning system for housing price prediction with enterprise-grade features including centralized configuration, structured logging, authentication, and comprehensive error handling.

## Features

- ML
  - Data preprocessing and feature engineering
  - Model training and evaluation
  - Batch and real-time inference
- Services
  - FastAPI REST API for predictions
  - Streamlit dashboard for interaction
- Operations
  - Centralized configuration (Pydantic with environment variable support)
  - CI/CD via GitHub Actions to AWS ECS
  - Containerization with Docker and docker-compose
- Observability & Reliability
  - Structured JSON logging
  - Health checks (liveness and readiness)
  - Robust error handling with custom exceptions
- Security & Quality
  - API key authentication
  - Input validation and sanitization
  - Formatting, linting, and testing tools

## Project Structure

```
production-ml/
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

- Python 3.13+ (see alternative setup below for Python 3.12)
- uv (Python package manager)
- Docker (for containerized deployment)
- AWS CLI (for cloud deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/abi-commits/production-ml.git
   cd production-ml
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

4. Alternative install (without uv / Python 3.12):
   ```bash
   python3.12 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
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

4. Run tests:
   ```bash
   make test
   ```

5. Format code:
   ```bash
   make format
   ```

6. Lint code:
   ```bash
   make lint
   ```

## API Usage

### Authentication

All API endpoints require an API key in the `X-API-Key` header.

- Local: set `API_KEY` in your `.env` file
- Production: provide `API_KEY` via ECS task definition secret, Parameter Store, or Secrets Manager
- Rotation: update the secret source (e.g., Parameter Store/Secrets Manager) and redeploy; the service reads the key from environment at startup

### Endpoints

- `GET /` - Health check (liveness)
- `GET /health` - Detailed health status (readiness)
- `POST /predict` - Real-time predictions
- `POST /run_batch` - Trigger batch predictions
- `GET /latest_predictions` - Get latest batch predictions



## Configuration

The application uses Pydantic settings for configuration. Key settings include:

- `ENVIRONMENT`: development/production
- `AWS_REGION`: AWS region for S3 and ECS
- `S3_BUCKET`: S3 bucket for model artifacts
- `MODEL_S3_KEY`: S3 key/path for the model artifact (e.g., `models/latest/model.pkl`)
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)

## Model Artifacts

- Training:
  - Local: run `make train` to generate artifacts into `models/`
  - CI: training jobs can push artifacts to `S3_BUCKET` at `MODEL_S3_KEY`
- Inference:
  - On startup, the API attempts to load the local model from `models/`
  - If not present (or if configured), it downloads the latest model from S3 using `S3_BUCKET` and `MODEL_S3_KEY`
- Versioning:
  - Include model version in responses (e.g., `model_version`) and log metadata for traceability

## Deployment

### Local Development

```bash
make build
make run
```

### Production Deployment

The project includes GitHub Actions for automated deployment to AWS ECS:

1. Push to `main` branch
2. GitHub Actions builds and pushes Docker images to ECR
3. Deploys to ECS cluster

### CI/CD Prerequisites

Configure the following GitHub Actions secrets (names may vary based on workflow):

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `ECR_REGISTRY` (or derive via AWS account/region)
- `ECS_CLUSTER`
- `ECS_SERVICE`
- `API_KEY` (if injected via environment)
- Any additional parameters required by the workflow (e.g., `IMAGE_TAG`, `S3_BUCKET`, `MODEL_S3_KEY`)

Ensure the IAM role used by GitHub Actions has permissions for:
- ECR: push/pull
- ECS: describe services, update services
- S3: read/write artifacts (if training/inference pull from S3)

## Monitoring

- Structured logging with JSON output in production, including fields like `timestamp`, `level`, `message`, `request_id`, `model_version`
- Health check endpoints:
  - `/` liveness: service process is running
  - `/health` readiness: model loaded, S3 connectivity, version info, and dependency status
- Error tracking with detailed exception information

## Security

- API key authentication
- Input validation and sanitization
- Secure configuration management (no hardcoded secrets)
- Key rotation via environment secret sources and redeploy
- Principle of least privilege for IAM roles

## Documentation

- [Architecture Guide](docs/architecture.md) — System design and components
- [API Documentation](docs/api.md) — Complete API reference
- [Deployment Guide](docs/deployment.md) — Production deployment instructions
- [Development Guide](docs/development.md) — Development workflow and standards
