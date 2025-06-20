# Deploy Medical AI Service to Render

## Quick Deployment Steps

### Option 1: GitHub Integration (Recommended)

1. **Push to GitHub**:
   ```bash
   # If you haven't already, initialize git in the python_ai_service directory
   cd python_ai_service
   git init
   git add .
   git commit -m "Initial commit: Medical AI Service"
   
   # Create a new repository on GitHub and push
   git remote add origin https://github.com/yourusername/medical-ai-service.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `medical-ai-service` repository
   - Render will auto-detect it's a Python app

3. **Configure the Service**:
   - **Name**: `medical-ai-service`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: Start with "Starter" (free tier)

4. **Set Environment Variables**:
   ```
   API_KEY=your-secure-api-key-here
   REQUIRE_API_KEY=false
   HUGGINGFACE_SPACE=Abdhack/medgemma-4b-it
   HOST=0.0.0.0
   PORT=10000
   ENVIRONMENT=production
   ```

5. **Deploy**: Click "Create Web Service"

### Option 2: Direct Upload

If you prefer not to use GitHub:

1. **Create a ZIP file**:
   ```bash
   cd python_ai_service
   zip -r medical-ai-service.zip . -x "*.git*" "__pycache__/*" "*.pyc"
   ```

2. **Upload to Render**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Choose "Deploy an existing image or upload code"
   - Upload your ZIP file

## Post-Deployment Configuration

### 1. Get Your Service URL

After deployment, Render will provide you with a URL like:
```
https://medical-ai-service-xxxx.onrender.com
```

### 2. Test Your Deployment

```bash
# Test health endpoint
curl https://your-service-url.onrender.com/health

# Test AI query endpoint
curl -X POST "https://your-service-url.onrender.com/query-medgemma" \
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

### 3. Update Supabase Edge Function

1. Go to your Supabase project dashboard
2. Navigate to Edge Functions
3. Add these environment variables:
   - `PYTHON_SERVICE_URL`: `https://your-service-url.onrender.com`
   - `PYTHON_SERVICE_API_KEY`: `your-secure-api-key-here` (if using authentication)

### 4. Update Frontend Environment

Add to your `.env` file:
```
VITE_PYTHON_SERVICE_URL=https://your-service-url.onrender.com
```

## Monitoring Your Deployment

### Render Dashboard
- View logs in real-time
- Monitor resource usage
- Set up alerts
- Configure auto-scaling

### Health Checks
Render automatically monitors your `/health` endpoint and will restart the service if it becomes unhealthy.

### Logs
Access logs through the Render dashboard or via CLI:
```bash
# Install Render CLI
npm install -g @render/cli

# View logs
render logs -s your-service-id
```

## Scaling and Performance

### Free Tier Limitations
- Service spins down after 15 minutes of inactivity
- 750 hours/month of runtime
- Shared CPU and 512MB RAM

### Upgrading
For production use, consider upgrading to:
- **Starter Plan** ($7/month): Always-on, dedicated resources
- **Standard Plan** ($25/month): More CPU and RAM
- **Pro Plan** ($85/month): High-performance instances

## Troubleshooting

### Common Issues

1. **Service Won't Start**:
   - Check build logs for dependency issues
   - Verify Python version compatibility
   - Check environment variables

2. **Gradio Client Errors**:
   - Verify Hugging Face space is accessible
   - Check if HF_TOKEN is needed for the space
   - Monitor rate limiting

3. **Timeout Issues**:
   - Increase timeout settings in Render
   - Optimize model query parameters
   - Consider caching strategies

### Debug Commands

```bash
# Check service status
curl https://your-service-url.onrender.com/

# Detailed health check
curl https://your-service-url.onrender.com/health

# Test with minimal query
curl -X POST "https://your-service-url.onrender.com/query-medgemma" \
     -H "Content-Type: application/json" \
     -d '{"message": {"text": "Hello", "files": []}}'
```

## Security Best Practices

1. **Enable API Key Authentication**:
   ```
   REQUIRE_API_KEY=true
   API_KEY=your-very-secure-random-key
   ```

2. **Use Environment Variables**:
   - Never commit secrets to git
   - Use Render's environment variable management

3. **Monitor Usage**:
   - Set up alerts for unusual activity
   - Monitor API usage patterns

## Next Steps

After successful deployment:

1. **Test Integration**: Verify the Supabase Edge Function can communicate with your Python service
2. **Monitor Performance**: Watch logs and metrics for the first few days
3. **Set Up Alerts**: Configure notifications for service issues
4. **Plan Scaling**: Monitor usage to determine if you need to upgrade plans
5. **Backup Strategy**: Consider backing up your service configuration

Your Medical AI Service should now be live and ready to handle medical queries through the MedGemma-4B-IT model!