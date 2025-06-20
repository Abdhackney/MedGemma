# Medical AI Service

A Python FastAPI service that provides medical AI capabilities using the MedGemma-4B-IT model via Gradio Client.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Gradio Client Integration**: Direct connection to Hugging Face MedGemma-4B-IT space
- **Medical Safety**: Built-in medical disclaimers and safety checks
- **Authentication**: Optional API key authentication
- **Error Handling**: Graceful error handling with fallback responses
- **Health Checks**: Built-in health monitoring endpoints
- **Docker Support**: Ready for containerized deployment

## Quick Start

### Local Development

1. **Clone and Setup**:
   ```bash
   cd python_ai_service
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the Service**:
   ```bash
   python main.py
   ```

4. **Test the Service**:
   ```bash
   curl -X POST "http://localhost:8000/query-medgemma" \
        -H "Content-Type: application/json" \
        -d '{
          "message": {
            "text": "What are the symptoms of diabetes?",
            "files": []
          },
          "system_prompt": "You are a helpful medical expert.",
          "max_tokens": 2048
        }'
   ```

### Docker Deployment

1. **Build the Image**:
   ```bash
   docker build -t medical-ai-service .
   ```

2. **Run the Container**:
   ```bash
   docker run -p 8000:8000 \
     -e API_KEY=your-secure-key \
     -e HF_TOKEN=your-hf-token \
     medical-ai-service
   ```

## API Endpoints

### POST /query-medgemma

Query the MedGemma-4B-IT model with a medical question.

**Request Body**:
```json
{
  "message": {
    "text": "What are the symptoms of diabetes?",
    "files": []
  },
  "system_prompt": "You are a helpful medical expert.",
  "max_tokens": 2048,
  "user_id": "optional-user-id"
}
```

**Response**:
```json
{
  "response": "Diabetes symptoms include frequent urination, excessive thirst...",
  "confidence": 0.85,
  "source": "medgemma-4b-it-gradio",
  "processing_time": 2.34,
  "user_id": "optional-user-id"
}
```

### GET /health

Health check endpoint that verifies service status and Gradio client connection.

### GET /

Basic service information endpoint.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | API key for authentication | `your-secure-api-key-here` |
| `REQUIRE_API_KEY` | Whether API key is required | `false` |
| `HUGGINGFACE_SPACE` | Hugging Face space to use | `Abdhack/medgemma-4b-it` |
| `HF_TOKEN` | Hugging Face token (optional) | - |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `ENVIRONMENT` | Environment (development/production) | `production` |

## Deployment Options

### 1. Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python main.py`
5. Add environment variables in Render dashboard

### 2. Google Cloud Run

```bash
# Deploy from source
gcloud run deploy medical-ai-service \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars API_KEY=your-key,HF_TOKEN=your-token
```

### 3. Railway

1. Connect your GitHub repository to Railway
2. Railway will auto-detect the Python app
3. Add environment variables in Railway dashboard
4. Deploy automatically on git push

### 4. Heroku

```bash
# Create Heroku app
heroku create your-medical-ai-service

# Set environment variables
heroku config:set API_KEY=your-secure-key
heroku config:set HF_TOKEN=your-hf-token

# Deploy
git push heroku main
```

## Integration with Supabase

After deploying your Python service, update your Supabase Edge Function environment variables:

1. Go to your Supabase project dashboard
2. Navigate to Edge Functions
3. Set the following environment variables:
   - `PYTHON_SERVICE_URL`: Your deployed service URL (e.g., `https://your-service.onrender.com`)
   - `PYTHON_SERVICE_API_KEY`: Your API key (if using authentication)

## Security Considerations

- **API Key Authentication**: Enable `REQUIRE_API_KEY=true` in production
- **CORS Configuration**: Update CORS origins to match your domain
- **Rate Limiting**: Consider adding rate limiting for production use
- **Input Validation**: The service includes input validation via Pydantic models
- **Medical Disclaimers**: Automatic addition of medical disclaimers to responses

## Monitoring and Logging

- Health check endpoint at `/health`
- Structured logging with request/response tracking
- Processing time measurement
- Error tracking and graceful fallbacks

## Troubleshooting

### Common Issues

1. **Gradio Client Connection Failed**:
   - Check if the Hugging Face space is accessible
   - Verify HF_TOKEN if using a private space
   - Check network connectivity

2. **Service Unavailable**:
   - Check if the service is running on the correct port
   - Verify environment variables are set correctly
   - Check logs for detailed error messages

3. **Authentication Errors**:
   - Verify API_KEY matches between client and server
   - Check if REQUIRE_API_KEY is set correctly

### Logs

The service provides detailed logging for debugging:
- Request/response tracking
- Processing time measurement
- Error details and stack traces
- Gradio client connection status