"""
RaddScr API - Simplified for deployment
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Reddit SaaS Validator API",
    description="API for validating SaaS ideas via Reddit, Twitter, and LinkedIn analysis",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """API root"""
    return {
        "message": "Reddit SaaS Validator API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": os.getenv("DATABASE_URL", "").split("@")[1] if "@" in os.getenv("DATABASE_URL", "") else "not_configured",
        "redis": "configured" if os.getenv("REDIS_URL") else "not_configured"
    }

@app.get("/test")
def test():
    """Test endpoint"""
    return {
        "message": "API is working!",
        "env_vars": {
            "database": bool(os.getenv("DATABASE_URL")),
            "redis": bool(os.getenv("REDIS_URL")),
            "secret_key": bool(os.getenv("SECRET_KEY"))
        }
    }
