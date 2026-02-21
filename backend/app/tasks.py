"""
Celery tasks for async validation
"""
from celery import Task
from sqlalchemy.orm import Session
import sys
import os
from datetime import datetime

# Add parent directory to path to import validation scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from .celery_app import celery_app
from .database import SessionLocal
from .models import Project, Analysis, AnalysisStatus, User
from .email import send_validation_complete_email

# Import validation scripts
try:
    from src.reddit_scraper import RedditValidator
    from src.twitter_scraper import TwitterValidator
    from src.linkedin_scraper import LinkedInValidator
    from src.multiplatform_validator import MultiPlatformValidator
except ImportError:
    # Fallback for development
    RedditValidator = None
    TwitterValidator = None
    LinkedInValidator = None
    MultiPlatformValidator = None


class DatabaseTask(Task):
    """Base task with database session"""
    _db = None
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.run_validation")
def run_validation(self, project_id: int):
    """
    Run full validation for a project
    
    Steps:
    1. Update project status to PROCESSING
    2. Run Reddit validation
    3. Run Twitter validation  
    4. Run LinkedIn validation
    5. Combine results
    6. Save to database
    7. Send email notification
    8. Update status to COMPLETED
    """
    db = self.db
    
    try:
        # Get project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise Exception(f"Project {project_id} not found")
        
        # Update status
        project.status = AnalysisStatus.PROCESSING
        db.commit()
        
        # Get or create analysis
        analysis = db.query(Analysis).filter(Analysis.project_id == project_id).first()
        if not analysis:
            analysis = Analysis(project_id=project_id)
            db.add(analysis)
            db.commit()
        
        # Prepare validation params
        idea = f"{project.name}. {project.description or ''}"
        keywords = project.keywords or []
        
        # Run validations
        results = {}
        
        # 1. Reddit validation
        if RedditValidator:
            try:
                reddit_validator = RedditValidator()
                reddit_data = reddit_validator.validate_idea(idea, keywords)
                results['reddit'] = reddit_data
                analysis.reddit_data = reddit_data
            except Exception as e:
                print(f"Reddit validation failed: {e}")
                results['reddit'] = {"error": str(e)}
        
        # 2. Twitter validation
        if TwitterValidator:
            try:
                twitter_validator = TwitterValidator()
                twitter_data = twitter_validator.analyze_idea(idea, keywords)
                results['twitter'] = twitter_data
                analysis.twitter_data = twitter_data
            except Exception as e:
                print(f"Twitter validation failed: {e}")
                results['twitter'] = {"error": str(e)}
        
        # 3. LinkedIn validation
        if LinkedInValidator:
            try:
                linkedin_validator = LinkedInValidator()
                linkedin_data = linkedin_validator.analyze_b2b_potential(idea, keywords)
                results['linkedin'] = linkedin_data
                analysis.linkedin_data = linkedin_data
            except Exception as e:
                print(f"LinkedIn validation failed: {e}")
                results['linkedin'] = {"error": str(e)}
        
        # 4. Combine results
        if MultiPlatformValidator:
            try:
                mp_validator = MultiPlatformValidator()
                combined = mp_validator.validate_idea(idea, keywords)
                
                # Extract results
                analysis.overall_score = combined.get('overall_score', 0)
                analysis.verdict = combined.get('verdict', 'Unknown')
                analysis.key_insights = combined.get('key_insights', [])
                analysis.recommendations = combined.get('recommendations', [])
            except Exception as e:
                print(f"Multi-platform validation failed: {e}")
                # Fallback: calculate simple average
                scores = []
                if 'reddit' in results and 'score' in results['reddit']:
                    scores.append(results['reddit']['score'])
                if 'twitter' in results and 'score' in results['twitter']:
                    scores.append(results['twitter']['score'])
                if 'linkedin' in results and 'score' in results['linkedin']:
                    scores.append(results['linkedin']['score'])
                
                analysis.overall_score = int(sum(scores) / len(scores)) if scores else 0
                analysis.verdict = "Analysis completed with limited data"
        
        # Update timestamps
        analysis.completed_at = datetime.utcnow()
        project.status = AnalysisStatus.COMPLETED
        
        db.commit()
        db.refresh(analysis)
        
        # Send email notification
        user = db.query(User).filter(User.id == project.user_id).first()
        if user:
            try:
                send_validation_complete_email(
                    user.email,
                    project.name,
                    analysis.overall_score or 0,
                    analysis.verdict or "Unknown",
                    project.id
                )
            except Exception as e:
                print(f"Failed to send completion email: {e}")
        
        return {
            "status": "completed",
            "project_id": project_id,
            "score": analysis.overall_score,
            "verdict": analysis.verdict
        }
    
    except Exception as e:
        # Update project status to FAILED
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = AnalysisStatus.FAILED
            db.commit()
        
        raise e


@celery_app.task(name="app.tasks.test_task")
def test_task(message: str):
    """Simple test task"""
    print(f"Test task executed: {message}")
    return {"status": "success", "message": message}
