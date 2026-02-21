from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    full_name = Column(String, nullable=True)
    
    # OAuth
    google_id = Column(String, nullable=True, unique=True, index=True)
    
    # Subscription
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    subscription_end_date = Column(DateTime, nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="user")


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Project info
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    keywords = Column(JSON, nullable=True)  # List of keywords
    
    # Status
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="projects")
    analysis = relationship("Analysis", back_populates="project", uselist=False)


class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Raw data
    reddit_data = Column(JSON, nullable=True)
    twitter_data = Column(JSON, nullable=True)
    linkedin_data = Column(JSON, nullable=True)
    
    # Results
    overall_score = Column(Integer, nullable=True)  # 0-100
    verdict = Column(String, nullable=True)
    key_insights = Column(JSON, nullable=True)  # List of insights
    recommendations = Column(JSON, nullable=True)  # List of recommendations
    
    # Metadata
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="analysis")


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Stripe data
    stripe_subscription_id = Column(String, nullable=True, unique=True)
    stripe_customer_id = Column(String, nullable=True)
    
    # Plan details
    plan = Column(String, nullable=False)  # starter, pro, enterprise
    status = Column(String, nullable=False)  # active, past_due, cancelled
    current_period_end = Column(Integer, nullable=True)  # Unix timestamp
    
    # Usage limits
    validations_used = Column(Integer, default=0)
    validations_limit = Column(Integer, nullable=True)  # NULL = unlimited
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="subscription_details")
