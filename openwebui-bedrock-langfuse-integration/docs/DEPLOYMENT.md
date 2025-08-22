# Deployment Guide

## Overview

This guide covers different deployment scenarios for the OpenWebUI + AWS Bedrock + Langfuse integration.

## Prerequisites

### System Requirements
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 10GB free space for Docker volumes
- **Network**: Internet access for pulling images and AWS API calls

### AWS Requirements
- **AWS Account** with Bedrock access
- **AWS CLI** configured (optional but recommended)
- **IAM Permissions** for Bedrock model access
- **AWS Credentials** (profile or environment variables)

### Bedrock Model Access
Ensure you have requested access to the models you want to use:

1. Go to AWS Console → Amazon Bedrock
2. Navigate to Model Access
3. Request access for desired models:
   - Anthropic Claude 3 models
   - Amazon Titan models
   - Meta Llama 2 models

## Local Development Deployment

### Quick Start

1. **Clone the project**
   ```bash
   git clone <repository-url>
   cd openwebui-bedrock-langfuse-integration
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run setup script**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

4. **Access applications**
   - OpenWebUI: http://localhost:8080
   - Langfuse: http://localhost:3000
   - Backend API: http://localhost:8081

### Manual Setup

1. **Environment Configuration**
   ```bash
   # Copy and edit environment file
   cp .env.example .env
   
   # Required variables:
   # AWS_PROFILE=your-aws-profile
   # LANGFUSE_SECRET_KEY=sk-lf-...
   # LANGFUSE_PUBLIC_KEY=pk-lf-...
   ```

2. **Start Services**
   ```bash
   # Start all services
   docker-compose up -d
   
   # Or start step by step
   docker-compose up -d langfuse-db langfuse-redis langfuse-clickhouse langfuse-minio
   sleep 30
   docker-compose up -d langfuse
   sleep 20
   docker-compose up -d backend
   sleep 15
   docker-compose up -d openwebui
   ```

3. **Verify Deployment**
   ```bash
   # Check service health
   curl http://localhost:8081/health
   curl http://localhost:3000
   curl http://localhost:8080
   
   # Run integration tests
   python scripts/test_integration.py
   ```

## Production Deployment

### Security Considerations

1. **Environment Variables**
   ```bash
   # Use secure values
   WEBUI_SECRET_KEY=$(openssl rand -hex 32)
   NEXTAUTH_SECRET=$(openssl rand -hex 32)
   SALT=$(openssl rand -hex 16)
   
   # Enable authentication
   WEBUI_AUTH=true
   ```

2. **Network Security**
   ```yaml
   # docker-compose.prod.yml
   services:
     openwebui:
       ports:
         - "127.0.0.1:8080:8080"  # Bind to localhost only
     
     backend:
       ports:
         - "127.0.0.1:8081:8081"  # Bind to localhost only
   ```

3. **SSL/TLS Setup**
   Use a reverse proxy (nginx, traefik) for SSL termination:
   
   ```nginx
   # nginx configuration
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # ... (same services as main compose file)
  
  # Add reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - openwebui
      - backend
    networks:
      - app-network

  # Resource limits
  backend:
    # ... existing config
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### Environment-Specific Configurations

#### Development
```bash
DEBUG=true
TELEMETRY_ENABLED=false
WEBUI_AUTH=false
```

#### Staging
```bash
DEBUG=false
TELEMETRY_ENABLED=true
WEBUI_AUTH=true
LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES=true
```

#### Production
```bash
DEBUG=false
TELEMETRY_ENABLED=false
WEBUI_AUTH=true
LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES=false
```

## Cloud Deployment

### AWS ECS Deployment

1. **Create ECS Task Definition**
   ```json
   {
     "family": "openwebui-bedrock-langfuse",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "2048",
     "memory": "4096",
     "taskRoleArn": "arn:aws:iam::account:role/ecs-bedrock-role",
     "containerDefinitions": [
       {
         "name": "backend",
         "image": "your-registry/openwebui-backend:latest",
         "portMappings": [
           {"containerPort": 8081, "protocol": "tcp"}
         ],
         "environment": [
           {"name": "AWS_REGION", "value": "us-east-1"},
           {"name": "LANGFUSE_HOST", "value": "https://cloud.langfuse.com"}
         ]
       }
     ]
   }
   ```

2. **Create ECS Service**
   ```bash
   aws ecs create-service \
     --cluster your-cluster \
     --service-name openwebui-backend \
     --task-definition openwebui-bedrock-langfuse \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
   ```

### Kubernetes Deployment

1. **Create Namespace**
   ```yaml
   apiVersion: v1
   kind: Namespace
   metadata:
     name: openwebui-bedrock-langfuse
   ```

2. **Deploy Backend**
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: backend
     namespace: openwebui-bedrock-langfuse
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: backend
     template:
       metadata:
         labels:
           app: backend
       spec:
         containers:
         - name: backend
           image: your-registry/openwebui-backend:latest
           ports:
           - containerPort: 8081
           env:
           - name: AWS_REGION
             value: "us-east-1"
           - name: LANGFUSE_SECRET_KEY
             valueFrom:
               secretKeyRef:
                 name: langfuse-secrets
                 key: secret-key
   ```

3. **Deploy Service**
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: backend-service
     namespace: openwebui-bedrock-langfuse
   spec:
     selector:
       app: backend
     ports:
     - port: 8081
       targetPort: 8081
     type: LoadBalancer
   ```

## Monitoring and Maintenance

### Health Checks

1. **Service Health Endpoints**
   ```bash
   # Backend health
   curl http://localhost:8081/health
   
   # Langfuse health
   curl http://localhost:3000/api/public/health
   
   # OpenWebUI health
   curl http://localhost:8080/health
   ```

2. **Automated Health Monitoring**
   ```bash
   # Create monitoring script
   #!/bin/bash
   # health-check.sh
   
   BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/health)
   LANGFUSE_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
   OPENWEBUI_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080)
   
   if [ $BACKEND_HEALTH -ne 200 ]; then
     echo "Backend unhealthy"
     # Send alert
   fi
   ```

### Log Management

1. **View Logs**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f backend
   docker-compose logs -f langfuse
   docker-compose logs -f openwebui
   ```

2. **Log Rotation**
   ```yaml
   # docker-compose.yml
   services:
     backend:
       logging:
         driver: "json-file"
         options:
           max-size: "100m"
           max-file: "3"
   ```

### Backup and Recovery

1. **Database Backups**
   ```bash
   # Backup Langfuse database
   docker-compose exec langfuse-db pg_dump -U langfuse langfuse > langfuse_backup.sql
   
   # Backup OpenWebUI data
   docker-compose exec openwebui tar -czf /tmp/openwebui_backup.tar.gz /app/backend/data
   docker cp $(docker-compose ps -q openwebui):/tmp/openwebui_backup.tar.gz ./openwebui_backup.tar.gz
   ```

2. **Restore from Backup**
   ```bash
   # Restore Langfuse database
   docker-compose exec -T langfuse-db psql -U langfuse langfuse < langfuse_backup.sql
   
   # Restore OpenWebUI data
   docker cp ./openwebui_backup.tar.gz $(docker-compose ps -q openwebui):/tmp/
   docker-compose exec openwebui tar -xzf /tmp/openwebui_backup.tar.gz -C /
   ```

### Updates and Upgrades

1. **Update Images**
   ```bash
   # Pull latest images
   docker-compose pull
   
   # Restart with new images
   docker-compose up -d
   ```

2. **Rolling Updates**
   ```bash
   # Update backend only
   docker-compose pull backend
   docker-compose up -d --no-deps backend
   ```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :8080
   netstat -tulpn | grep :8081
   netstat -tulpn | grep :3000
   
   # Change ports in .env file
   OPENWEBUI_PORT=8090
   BACKEND_PORT=8091
   ```

2. **AWS Permission Issues**
   ```bash
   # Test AWS access
   aws bedrock list-foundation-models --region us-east-1
   
   # Check IAM permissions
   aws iam simulate-principal-policy \
     --principal-arn arn:aws:iam::account:user/username \
     --action-names bedrock:InvokeModel \
     --resource-arns "*"
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase memory limits
   # In docker-compose.yml:
   deploy:
     resources:
       limits:
         memory: 4G
   ```

### Performance Optimization

1. **Resource Allocation**
   ```yaml
   # docker-compose.yml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '2.0'
             memory: 4G
           reservations:
             cpus: '1.0'
             memory: 2G
   ```

2. **Caching**
   ```bash
   # Enable Redis caching for Langfuse
   REDIS_CONNECTION_STRING=redis://langfuse-redis:6379
   ```

3. **Database Optimization**
   ```yaml
   # PostgreSQL tuning
   langfuse-db:
     environment:
       POSTGRES_SHARED_PRELOAD_LIBRARIES: pg_stat_statements
       POSTGRES_MAX_CONNECTIONS: 200
       POSTGRES_SHARED_BUFFERS: 256MB
   ```

## Security Best Practices

1. **Network Security**
   - Use internal networks for service communication
   - Expose only necessary ports
   - Implement firewall rules

2. **Secret Management**
   - Use Docker secrets or external secret management
   - Rotate API keys regularly
   - Avoid hardcoding credentials

3. **Access Control**
   - Enable OpenWebUI authentication
   - Use IAM roles for AWS access
   - Implement proper user permissions

4. **Monitoring**
   - Set up alerts for failures
   - Monitor resource usage
   - Track API usage and costs

This deployment guide covers the essential aspects of deploying the OpenWebUI + Bedrock + Langfuse integration in various environments. Choose the deployment method that best fits your use case and security requirements.
