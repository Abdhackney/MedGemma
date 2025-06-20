import os
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn
from gradio_client import Client, handle_file
import asyncio
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Medical AI Service",
    description="Python service for MedGemma-4B-IT medical AI queries via Gradio Client",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Supabase domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Environment variables
API_KEY = os.getenv("API_KEY", "your-secure-api-key-here")
HUGGINGFACE_SPACE = os.getenv("HUGGINGFACE_SPACE", "Abdhack/medgemma-4b-it")
HF_TOKEN = os.getenv("HF_TOKEN")  # Optional: for private spaces or rate limiting

# Pydantic models
class MessageInput(BaseModel):
    text: str = Field(..., description="The medical query text")
    files: list = Field(default=[], description="List of file paths (currently not used)")

class MedGemmaRequest(BaseModel):
    message: MessageInput
    system_prompt: str = Field(
        default="You are a helpful medical expert. Provide accurate, evidence-based medical information while emphasizing the importance of consulting healthcare professionals for diagnosis and treatment.",
        description="System prompt for the AI"
    )
    max_tokens: int = Field(default=2048, ge=1, le=4096, description="Maximum number of tokens to generate")
    user_id: Optional[str] = Field(None, description="User ID for logging purposes")

class MedGemmaResponse(BaseModel):
    response: str
    confidence: float
    source: str
    processing_time: float
    user_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    gradio_space: str

# Global client instance
gradio_client = None

@lru_cache()
def get_gradio_client():
    """Get or create Gradio client instance with caching"""
    global gradio_client
    if gradio_client is None:
        try:
            logger.info(f"Initializing Gradio client for space: {HUGGINGFACE_SPACE}")
            
            # Initialize client with optional HF token
            if HF_TOKEN:
                gradio_client = Client(HUGGINGFACE_SPACE, hf_token=HF_TOKEN)
                logger.info("Gradio client initialized with HF token")
            else:
                gradio_client = Client(HUGGINGFACE_SPACE)
                logger.info("Gradio client initialized without HF token")
                
        except Exception as e:
            logger.error(f"Failed to initialize Gradio client: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to AI service: {str(e)}"
            )
    
    return gradio_client

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key if provided"""
    if credentials is None:
        # Allow requests without API key for development
        if os.getenv("REQUIRE_API_KEY", "false").lower() == "true":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required"
            )
        return None
    
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return credentials.credentials

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="Medical AI Service",
        version="1.0.0",
        gradio_space=HUGGINGFACE_SPACE
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check endpoint"""
    try:
        # Test Gradio client connection
        client = get_gradio_client()
        
        return HealthResponse(
            status="healthy",
            service="Medical AI Service",
            version="1.0.0",
            gradio_space=HUGGINGFACE_SPACE
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.post("/query-medgemma", response_model=MedGemmaResponse)
async def query_medgemma(
    request: MedGemmaRequest,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """
    Query the MedGemma-4B-IT model via Gradio Client
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(f"Processing medical query for user: {request.user_id}")
        logger.info(f"Query text length: {len(request.message.text)} characters")
        
        # Get Gradio client
        client = get_gradio_client()
        
        # Prepare the request for Gradio
        message_dict = {
            "text": request.message.text,
            "files": request.message.files  # Currently empty for text-only queries
        }
        
        logger.info("Sending request to Gradio client...")
        
        # Make the prediction using the Gradio client
        # Based on the API specification you provided
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.predict(
                message=message_dict,
                param_2=request.system_prompt,  # System prompt
                param_3=request.max_tokens,     # Max tokens
                api_name="/chat"
            )
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Gradio client response received in {processing_time:.2f} seconds")
        
        # Extract response text
        response_text = str(result) if result else "No response generated"
        
        # Calculate confidence score (simplified heuristic)
        confidence = calculate_confidence_score(response_text, request.message.text)
        
        # Add medical disclaimer if not present
        if not contains_medical_disclaimer(response_text):
            response_text = add_medical_disclaimer(response_text)
        
        logger.info(f"Successfully processed query for user: {request.user_id}")
        
        return MedGemmaResponse(
            response=response_text,
            confidence=confidence,
            source="medgemma-4b-it-gradio",
            processing_time=processing_time,
            user_id=request.user_id
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error processing medical query: {str(e)}")
        logger.error(f"Error occurred after {processing_time:.2f} seconds")
        
        # Return a graceful error response
        return MedGemmaResponse(
            response=f"I apologize, but I encountered an error processing your medical query: {str(e)}. Please try again later or consult with a healthcare professional for immediate assistance.",
            confidence=0.0,
            source="error-fallback",
            processing_time=processing_time,
            user_id=request.user_id
        )

def calculate_confidence_score(response: str, query: str) -> float:
    """
    Calculate a confidence score based on response characteristics
    This is a simplified heuristic - in production, you might use more sophisticated methods
    """
    try:
        # Basic heuristics for confidence scoring
        confidence = 0.5  # Base confidence
        
        # Longer responses tend to be more comprehensive
        if len(response) > 200:
            confidence += 0.2
        
        # Responses with medical terms might be more relevant
        medical_terms = [
            'symptom', 'diagnosis', 'treatment', 'medication', 'doctor', 
            'physician', 'medical', 'health', 'condition', 'disease'
        ]
        
        response_lower = response.lower()
        medical_term_count = sum(1 for term in medical_terms if term in response_lower)
        confidence += min(medical_term_count * 0.05, 0.3)
        
        # Responses with disclaimers show appropriate caution
        if 'disclaimer' in response_lower or 'consult' in response_lower:
            confidence += 0.1
        
        # Cap confidence at reasonable maximum
        return min(confidence, 0.95)
        
    except Exception:
        return 0.5  # Default confidence if calculation fails

def contains_medical_disclaimer(text: str) -> bool:
    """Check if the response already contains a medical disclaimer"""
    text_lower = text.lower()
    disclaimer_keywords = [
        'disclaimer', 'consult', 'healthcare professional', 
        'medical advice', 'professional medical', 'seek medical'
    ]
    return any(keyword in text_lower for keyword in disclaimer_keywords)

def add_medical_disclaimer(text: str) -> str:
    """Add a medical disclaimer to the response"""
    disclaimer = "\n\n⚠️ **Medical Disclaimer**: This information is for educational purposes only and should not replace professional medical advice. Please consult with a healthcare provider for medical concerns."
    return text + disclaimer

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP exception: {exc.detail}")
    return {
        "response": f"Service error: {exc.detail}",
        "confidence": 0.0,
        "source": "service-error",
        "processing_time": 0.0
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return {
        "response": "An unexpected error occurred. Please try again later.",
        "confidence": 0.0,
        "source": "unexpected-error",
        "processing_time": 0.0
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting Medical AI Service on {host}:{port}")
    logger.info(f"Using Hugging Face Space: {HUGGINGFACE_SPACE}")
    logger.info(f"API Key required: {os.getenv('REQUIRE_API_KEY', 'false')}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT", "production") == "development"
    )