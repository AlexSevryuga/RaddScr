"""
RaddScr API - Incremental deployment
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os

# Try to import optional modules
try:
    from .database import engine, Base
    DB_AVAILABLE = True
except ImportError as e:
    print(f"DB modules not available: {e}")
    DB_AVAILABLE = False
    engine = None
    Base = None

# Try to import routers
ROUTERS_AVAILABLE = False
if DB_AVAILABLE:
    try:
        from .routers import auth, projects
        ROUTERS_AVAILABLE = True
    except ImportError as e:
        print(f"Routers not available: {e}")

app = FastAPI(
    title="Reddit SaaS Validator API",
    description="API for validating SaaS ideas via Reddit, Twitter, and LinkedIn analysis",
    version="1.0.0"
)

# Session middleware (required for OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "default-secret-key-change-in-production")
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers if available
if ROUTERS_AVAILABLE:
    try:
        app.include_router(auth.router)
        app.include_router(projects.router)
        print("✅ Auth and Projects routers loaded")
    except Exception as e:
        print(f"⚠️ Could not load routers: {e}")

@app.get("/")
def root():
    """API root"""
    return {
        "message": "Reddit SaaS Validator API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
        "features": {
            "database": DB_AVAILABLE,
            "auth": DB_AVAILABLE,
            "projects": DB_AVAILABLE
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    db_host = ""
    if os.getenv("DATABASE_URL"):
        db_url = os.getenv("DATABASE_URL", "")
        if "@" in db_url:
            db_host = db_url.split("@")[1].split("/")[0]
    
    return {
        "status": "healthy",
        "database": db_host if db_host else "not_configured",
        "redis": "configured" if os.getenv("REDIS_URL") else "not_configured",
        "features": {
            "database": DB_AVAILABLE
        }
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
        },
        "modules": {
            "database": DB_AVAILABLE
        }
    }

@app.post("/init-db")
def initialize_database():
    """Initialize database tables (run once after deployment)"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database modules not available")
    
    try:
        Base.metadata.create_all(bind=engine)
        return {
            "status": "success",
            "message": "Database tables created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database init failed: {str(e)}")
