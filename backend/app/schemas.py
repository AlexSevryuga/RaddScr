from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from .models import SubscriptionTier, AnalysisStatus


# Auth schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    subscription_tier: SubscriptionTier
    created_at: datetime
    
    class Config:
        from_attributes = True


# Project schemas
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    keywords: Optional[List[str]] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    keywords: Optional[List[str]] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    keywords: Optional[List[str]]
    status: AnalysisStatus
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Analysis schemas
class AnalysisResponse(BaseModel):
    id: int
    project_id: int
    overall_score: Optional[int]
    verdict: Optional[str]
    key_insights: Optional[List[str]]
    recommendations: Optional[List[str]]
    reddit_data: Optional[dict]
    twitter_data: Optional[dict]
    linkedin_data: Optional[dict]
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectWithAnalysis(ProjectResponse):
    analysis: Optional[AnalysisResponse] = None


# Subscription schemas
class CheckoutSession(BaseModel):
    checkout_url: str


class SubscriptionStatus(BaseModel):
    tier: SubscriptionTier
    is_active: bool
    end_date: Optional[datetime]


class SubscriptionCreate(BaseModel):
    plan: str = Field(..., pattern="^(starter|pro|enterprise)$")


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan: str
    status: str
    current_period_end: Optional[int]
    validations_used: int
    validations_limit: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True
