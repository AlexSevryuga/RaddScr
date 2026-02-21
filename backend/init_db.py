"""
Database initialization script
Run this after first deployment to create tables
"""
from app.database import engine, Base
from app import models

def init_db():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    init_db()
