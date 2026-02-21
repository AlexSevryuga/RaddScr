from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db
from ..tasks import run_validation

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: schemas.ProjectCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Create new project"""
    # Check user limits based on subscription
    user_projects_count = db.query(models.Project).filter(
        models.Project.user_id == current_user.id
    ).count()
    
    # Free tier: 1 project per month
    if current_user.subscription_tier == models.SubscriptionTier.FREE and user_projects_count >= 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Free tier allows 1 project per month. Upgrade to Premium for unlimited projects."
        )
    
    # Create project
    new_project = models.Project(
        user_id=current_user.id,
        name=project_data.name,
        description=project_data.description,
        keywords=project_data.keywords,
        status=models.AnalysisStatus.PENDING
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # Trigger Celery task for async analysis
    try:
        run_validation.delay(new_project.id)
    except Exception as e:
        print(f"Failed to queue validation task: {e}")
        # Don't fail the request if task queueing fails
    
    return new_project


@router.get("", response_model=List[schemas.ProjectResponse])
def list_projects(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get user's projects"""
    projects = db.query(models.Project).filter(
        models.Project.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return projects


@router.get("/{project_id}", response_model=schemas.ProjectWithAnalysis)
def get_project(
    project_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get project details with analysis"""
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@router.post("/{project_id}/validate")
def trigger_validation(
    project_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger validation for a project"""
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if already processing
    if project.status == models.AnalysisStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validation already in progress"
        )
    
    # Reset status and trigger validation
    project.status = models.AnalysisStatus.PENDING
    db.commit()
    
    try:
        task = run_validation.delay(project_id)
        return {
            "status": "queued",
            "task_id": task.id,
            "project_id": project_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue validation: {str(e)}"
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete project"""
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db.delete(project)
    db.commit()
    
    return None
