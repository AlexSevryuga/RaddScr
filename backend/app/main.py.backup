from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import auth, projects, stripe
from .database import engine, Base

app = FastAPI(
    title="Reddit SaaS Validator API",
    description="API for validating SaaS ideas via Reddit, Twitter, and LinkedIn analysis",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(stripe.router)


@app.get("/")
def root():
    """API root"""
    return {
        "message": "Reddit SaaS Validator API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/init-db")
def initialize_database():
    """Initialize database tables (run once after deployment)"""
    try:
        Base.metadata.create_all(bind=engine)
        return {
            "status": "success",
            "message": "Database tables created successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
