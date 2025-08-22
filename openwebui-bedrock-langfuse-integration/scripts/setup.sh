#!/bin/bash

# OpenWebUI + Bedrock + Langfuse Integration Setup Script

set -e  # Exit on any error

echo "🚀 OpenWebUI + AWS Bedrock + Langfuse Integration Setup"
echo "======================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed and running
check_docker() {
    print_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose."
        exit 1
    fi
    
    print_status "Docker is installed and running"
}

# Check if AWS CLI is configured
check_aws() {
    print_info "Checking AWS configuration..."
    
    if ! command -v aws &> /dev/null; then
        print_warning "AWS CLI is not installed. You may need to configure AWS credentials manually."
        return
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_warning "AWS credentials are not configured. Please run 'aws configure' or set environment variables."
        return
    fi
    
    print_status "AWS credentials are configured"
}

# Create environment file
setup_environment() {
    print_info "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_status "Created .env file from template"
            print_warning "Please edit .env file with your actual configuration"
        else
            print_error ".env.example file not found"
            exit 1
        fi
    else
        print_warning ".env file already exists. Skipping creation."
    fi
}

# Pull required Docker images
pull_images() {
    print_info "Pulling required Docker images..."
    
    docker-compose pull
    
    print_status "Docker images pulled successfully"
}

# Start services
start_services() {
    print_info "Starting services..."
    
    # Start Langfuse and its dependencies first
    print_info "Starting Langfuse services..."
    docker-compose up -d langfuse-db langfuse-redis langfuse-clickhouse langfuse-minio
    
    # Wait for databases to be ready
    print_info "Waiting for databases to be ready..."
    sleep 30
    
    # Start Langfuse
    docker-compose up -d langfuse
    
    # Wait for Langfuse to be ready
    print_info "Waiting for Langfuse to be ready..."
    sleep 20
    
    # Start backend
    print_info "Starting backend service..."
    docker-compose up -d backend
    
    # Wait for backend to be ready
    print_info "Waiting for backend to be ready..."
    sleep 15
    
    # Start OpenWebUI
    print_info "Starting OpenWebUI..."
    docker-compose up -d openwebui
    
    print_status "All services started successfully"
}

# Test services
test_services() {
    print_info "Testing service connectivity..."
    
    # Test Langfuse
    if curl -f -s http://localhost:3000 > /dev/null; then
        print_status "Langfuse is accessible at http://localhost:3000"
    else
        print_warning "Langfuse may not be ready yet. Please check in a few minutes."
    fi
    
    # Test Backend
    if curl -f -s http://localhost:8081/health > /dev/null; then
        print_status "Backend is accessible at http://localhost:8081"
    else
        print_warning "Backend may not be ready yet. Please check in a few minutes."
    fi
    
    # Test OpenWebUI
    if curl -f -s http://localhost:8080 > /dev/null; then
        print_status "OpenWebUI is accessible at http://localhost:8080"
    else
        print_warning "OpenWebUI may not be ready yet. Please check in a few minutes."
    fi
}

# Show final instructions
show_instructions() {
    echo ""
    echo "🎉 Setup completed successfully!"
    echo "================================"
    echo ""
    echo "🌐 Access your applications:"
    echo "   • OpenWebUI:      http://localhost:8080"
    echo "   • Langfuse:       http://localhost:3000"
    echo "   • Backend API:    http://localhost:8081"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Open Langfuse at http://localhost:3000"
    echo "   2. Create a new project and get API keys"
    echo "   3. Update .env file with your Langfuse API keys"
    echo "   4. Restart backend: docker-compose restart backend"
    echo "   5. Open OpenWebUI at http://localhost:8080"
    echo "   6. Complete OpenWebUI setup"
    echo "   7. Configure custom backend URL: http://backend:8081"
    echo ""
    echo "🔧 Useful commands:"
    echo "   • View logs:       docker-compose logs -f"
    echo "   • Stop services:   docker-compose down"
    echo "   • Restart:         docker-compose restart"
    echo "   • Update:          docker-compose pull && docker-compose up -d"
    echo ""
    echo "📚 Documentation: See README.md for detailed instructions"
}

# Main execution
main() {
    check_docker
    check_aws
    setup_environment
    pull_images
    start_services
    sleep 10  # Give services time to start
    test_services
    show_instructions
}

# Run main function
main
