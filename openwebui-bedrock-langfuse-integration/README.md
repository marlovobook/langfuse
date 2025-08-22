# OpenWebUI + AWS Bedrock + Langfuse Integration

A comprehensive integration that combines:
- **OpenWebUI** - Modern web interface for chat interactions
- **AWS Bedrock** - Scalable AI model backend
- **Langfuse** - Advanced observability and analytics

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  OpenWebUI  │    │   Custom     │    │   AWS       │
│  (Frontend) │───▶│   Backend    │───▶│   Bedrock   │
│             │    │   Server     │    │  (Models)   │
└─────────────┘    └──────────────┘    └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  Langfuse   │
                   │(Observability)│
                   └─────────────┘
```

## Features

### 🌐 OpenWebUI Integration
- Modern chat interface with real-time streaming
- User authentication and session management
- Conversation history and export
- Mobile-responsive design
- Docker deployment

### 🚀 AWS Bedrock Backend
- Support for multiple AI models:
  - Anthropic Claude 3 (Haiku, Sonnet, Opus)
  - Amazon Titan models
  - Meta Llama 2/3 models
- Automatic cost tracking
- AWS profile and IAM role support
- Error handling and retry logic

### 📊 Langfuse Observability
- Real-time conversation tracking
- Token usage analytics
- Cost monitoring
- Performance metrics
- Error tracking and debugging
- User session analytics

## Quick Start

### Prerequisites
- Docker and Docker Compose
- AWS Account with Bedrock access
- Python 3.11+

### 1. Clone and Setup
```bash
cd openwebui-bedrock-langfuse-integration
cp .env.example .env
```

### 2. Configure Environment
Edit `.env` file:
```bash
# AWS Configuration
AWS_PROFILE=your-profile-name
AWS_REGION=us-east-1

# Langfuse Configuration
LANGFUSE_HOST=http://localhost:3000
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...

# OpenWebUI Configuration
OPENWEBUI_PORT=8080
BACKEND_PORT=8081
```

### 3. Start Services
```bash
# Start all services
docker-compose up -d

# Or start individually
docker-compose up -d langfuse    # Start Langfuse first
docker-compose up -d backend     # Start custom backend
docker-compose up -d openwebui   # Start OpenWebUI
```

### 4. Access Applications
- **OpenWebUI**: http://localhost:8080
- **Langfuse Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8081

## Project Structure

```
openwebui-bedrock-langfuse-integration/
├── backend/                     # Custom backend server
│   ├── bedrock_langfuse/       # Bedrock + Langfuse integration
│   ├── openwebui_backend.py    # OpenWebUI-compatible API server
│   ├── models.py               # Data models
│   └── requirements.txt        # Python dependencies
├── config/                     # Configuration files
│   ├── docker-compose.yml     # Main compose file
│   ├── langfuse.yml           # Langfuse configuration
│   └── openwebui.yml         # OpenWebUI configuration
├── scripts/                   # Utility scripts
│   ├── setup.sh              # Complete setup script
│   ├── test_integration.py   # Integration tests
│   └── demo.py               # Demo script
├── docs/                     # Documentation
│   ├── API.md               # API documentation
│   ├── DEPLOYMENT.md        # Deployment guide
│   └── TROUBLESHOOTING.md   # Common issues
├── .env.example             # Environment template
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

## Components

### Backend Server
The custom backend server (`backend/openwebui_backend.py`) implements the OpenWebUI-compatible API while integrating with AWS Bedrock and Langfuse:

- `/v1/chat/completions` - Chat completions endpoint
- `/v1/models` - List available models
- `/health` - Health check endpoint

### Model Support
Currently supported models:
- `anthropic.claude-3-haiku-20240307-v1:0`
- `anthropic.claude-3-sonnet-20240229-v1:0`
- `anthropic.claude-3-opus-20240229-v1:0`
- `amazon.titan-text-express-v1`
- `meta.llama2-13b-chat-v1`
- `meta.llama2-70b-chat-v1`

### Observability Features
- **Real-time Tracking**: Every conversation is tracked in Langfuse
- **Cost Analytics**: Automatic cost calculation per request
- **Performance Monitoring**: Response times and token usage
- **Error Tracking**: Comprehensive error logging and analysis
- **User Analytics**: Session tracking and user behavior insights

## Configuration

### AWS Setup
1. Configure AWS credentials:
   ```bash
   aws configure --profile your-profile-name
   ```

2. Enable Bedrock models in AWS Console
3. Set appropriate IAM permissions

### Langfuse Setup
1. Access http://localhost:3000 after starting services
2. Create a new project
3. Copy API keys to `.env` file

### OpenWebUI Setup
1. Access http://localhost:8080
2. Complete initial setup
3. Configure custom backend URL: `http://backend:8081`

## API Examples

### Chat Completion
```python
import requests

response = requests.post('http://localhost:8081/v1/chat/completions', 
    json={
        "model": "anthropic.claude-3-haiku-20240307-v1:0",
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "stream": False
    }
)
```

### List Models
```python
response = requests.get('http://localhost:8081/v1/models')
models = response.json()
```

## Monitoring and Analytics

### Langfuse Dashboard
- Navigate to http://localhost:3000
- View real-time conversations
- Analyze token usage and costs
- Monitor performance metrics
- Track user sessions

### Health Monitoring
- Backend health: `GET /health`
- Model availability: `GET /v1/models`
- Langfuse connection: Check dashboard accessibility

## Troubleshooting

### Common Issues
1. **AWS Credentials**: Ensure proper AWS profile configuration
2. **Bedrock Access**: Verify model access in AWS Console
3. **Port Conflicts**: Check if ports 3000, 8080, 8081 are available
4. **Docker Issues**: Ensure Docker daemon is running

### Logs
```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f openwebui
docker-compose logs -f langfuse
```

## Development

### Running Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Start backend only
cd backend
python openwebui_backend.py

# Run tests
python -m pytest tests/
```

### Adding New Models
1. Update `backend/bedrock_langfuse/models.py`
2. Add model configuration in `backend/openwebui_backend.py`
3. Test with integration script

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting guide
- Review the documentation

---

Built with ❤️ using OpenWebUI, AWS Bedrock, and Langfuse
