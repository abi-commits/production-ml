# Deployment Guide

## Overview

This guide covers deploying the Housing ML system to production environments with enterprise-grade practices.

## Prerequisites

### AWS Resources
- ECR Repository: `housing-api` and `housing-streamlit`
- ECS Cluster: `housing-api-cluster-ecs`
- S3 Bucket: `housing-data-artifacts`
- IAM Roles with appropriate permissions

### Local Tools
- AWS CLI configured
- Docker installed
- Git for version control

## Environment Configuration

### Production Environment Variables

Create `.env.prod` file:

```bash
# Application
ENVIRONMENT=production
LOG_LEVEL=INFO

# AWS
AWS_REGION=ap-south-1
S3_BUCKET=housing-data-artifacts

# API Service
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Dashboard Service
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
API_URL=http://housing-api-service:8000/predict

# Security
API_KEY=your-production-api-key-here
SECRET_KEY=your-production-secret-key

# MLflow (Future)
MLFLOW_TRACKING_URI=http://mlflow-server:5000
```

## Local Development Deployment

### Using Docker Compose

1. **Start all services:**
```bash
make run-compose
```

2. **Verify services:**
```bash
# API Health Check
curl http://localhost:8000/health

# Dashboard
open http://localhost:8501
```

3. **Stop services:**
```bash
docker-compose down
```

### Individual Service Testing

```bash
# Build API
make build-api

# Run API locally
make run

# Build Dashboard
make build-dashboard

# Run Dashboard locally
make run-dashboard
```

## AWS Production Deployment

### Step 1: Build and Push Docker Images

The CI/CD pipeline automatically handles this, but for manual deployment:

```bash
# Authenticate with ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com

# Build and push API image
docker build -t housing-api .
docker tag housing-api:latest YOUR_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/housing-api:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/housing-api:latest

# Build and push Dashboard image
docker build -f Dockerfile.streamlit -t housing-streamlit .
docker tag housing-streamlit:latest YOUR_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/housing-streamlit:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/housing-streamlit:latest
```

### Step 2: Update ECS Services

```bash
# Force deployment of API service
aws ecs update-service \
  --cluster housing-api-cluster-ecs \
  --service housing-api-service \
  --force-new-deployment

# Force deployment of Dashboard service
aws ecs update-service \
  --cluster housing-api-cluster-ecs \
  --service housing-streamlit-service \
  --force-new-deployment
```

### Step 3: Verify Deployment

```bash
# Check service status
aws ecs describe-services \
  --cluster housing-api-cluster-ecs \
  --services housing-api-service housing-streamlit-service

# Check task status
aws ecs list-tasks --cluster housing-api-cluster-ecs

# View logs
aws ecs describe-tasks --cluster housing-api-cluster-ecs --tasks <task-arn>
```

## Infrastructure as Code

### ECS Task Definitions

#### API Service Task Definition
```json
{
  "family": "housing-api-task",
  "taskRoleArn": "arn:aws:iam::261899902410:role/ecsTaskExecutionRole",
  "executionRoleArn": "arn:aws:iam::261899902410:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "housing-api",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/housing-api:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "AWS_REGION", "value": "ap-south-1"},
        {"name": "S3_BUCKET", "value": "housing-data-artifacts"},
        {"name": "API_HOST", "value": "0.0.0.0"},
        {"name": "API_PORT", "value": "8000"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "secrets": [
        {"name": "API_KEY", "valueFrom": "arn:aws:secretsmanager:ap-south-1:YOUR_ACCOUNT_ID:secret:housing-api-key"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/housing-api",
          "awslogs-region": "ap-south-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

#### Dashboard Service Task Definition
```json
{
  "family": "housing-streamlit-task",
  "taskRoleArn": "arn:aws:iam::261899902410:role/ecsTaskExecutionRole",
  "executionRoleArn": "arn:aws:iam::261899902410:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "housing-streamlit",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/housing-streamlit:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "STREAMLIT_SERVER_PORT", "value": "8501"},
        {"name": "STREAMLIT_SERVER_ADDRESS", "value": "0.0.0.0"},
        {"name": "API_URL", "value": "http://housing-api-service:8000/predict"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/housing-streamlit",
          "awslogs-region": "ap-south-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

## Monitoring and Observability

### CloudWatch Logs

- **API Logs**: `/ecs/housing-api`
- **Dashboard Logs**: `/ecs/housing-streamlit`

### Health Checks

- Load balancer health checks every 30 seconds
- Container health checks via `/health` endpoint
- ECS service health monitoring

### Metrics to Monitor

- **API Metrics**:
  - Request latency (p95, p99)
  - Error rate (4xx, 5xx responses)
  - Throughput (requests per second)

- **System Metrics**:
  - CPU utilization
  - Memory usage
  - Network I/O

## Scaling

### Auto Scaling Policies

#### API Service
```json
{
  "PolicyName": "housing-api-scale-out",
  "PolicyType": "TargetTrackingScaling",
  "TargetTrackingScalingPolicyConfiguration": {
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleOutCooldown": 60,
    "ScaleInCooldown": 300
  }
}
```

#### Dashboard Service
```json
{
  "PolicyName": "housing-streamlit-scale-out",
  "PolicyType": "TargetTrackingScaling",
  "TargetTrackingScalingPolicyConfiguration": {
    "TargetValue": 50.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleOutCooldown": 60,
    "ScaleInCooldown": 300
  }
}
```

## Backup and Recovery

### Model Artifacts
- S3 versioning enabled for model files
- Regular backups of trained models
- Model registry with MLflow (future enhancement)

### Database Backups (Future)
- PostgreSQL RDS with automated backups
- Point-in-time recovery capability
- Cross-region backup replication

## Security

### Network Security
- VPC with private subnets
- Security groups restricting access
- Load balancers with SSL/TLS termination

### Access Control
- IAM roles with least privilege
- API key authentication
- Secrets management with AWS Secrets Manager

### Compliance
- Encryption at rest and in transit
- Regular security updates
- Vulnerability scanning in CI/CD

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check ECS events
aws ecs describe-services --cluster housing-api-cluster-ecs --services housing-api-service

# Check CloudWatch logs
aws logs tail /ecs/housing-api --follow
```

#### Health Check Failures
```bash
# Manual health check
curl -f https://your-api-endpoint/health

# Check load balancer target health
aws elbv2 describe-target-health --target-group-arn <target-group-arn>
```

#### High Latency
1. Check CloudWatch metrics for CPU/memory
2. Review application logs for bottlenecks
3. Consider scaling up task size or count

### Rollback Procedure

1. **Identify Issue**: Check logs and metrics
2. **Stop Current Deployment**: Reduce service count to 0
3. **Deploy Previous Version**: Update service with previous task definition
4. **Verify**: Test functionality and performance
5. **Scale Up**: Gradually increase service count

## Cost Optimization

### Right-sizing
- Monitor resource utilization
- Adjust CPU/memory allocations based on usage
- Use spot instances for non-critical workloads

### Auto Scaling
- Scale down during low-traffic periods
- Use scheduled scaling for predictable patterns
- Set appropriate cooldown periods

## Support

For deployment issues:
1. Check AWS service health dashboard
2. Review CloudWatch logs and metrics
3. Contact DevOps team with relevant log excerpts
4. Include ECS task ARNs and timestamps for faster resolution