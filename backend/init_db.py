"""Initialize database tables"""
from app.database import engine, Base
from app import models

# Create all tables
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully!")
