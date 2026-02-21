"""
Email service using Resend
"""
import resend
from .config import settings
from typing import Optional

# Initialize Resend
resend.api_key = settings.RESEND_API_KEY


async def send_email(
    to: str,
    subject: str,
    html: str,
    text: Optional[str] = None
):
    """Send email via Resend"""
    try:
        params = {
            "from": settings.FROM_EMAIL,
            "to": [to],
            "subject": subject,
            "html": html,
        }
        
        if text:
            params["text"] = text
        
        email = resend.Emails.send(params)
        return {"success": True, "id": email.get("id")}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


async def send_welcome_email(user_email: str, user_name: Optional[str] = None):
    """Send welcome email to new user"""
    name = user_name or user_email.split("@")[0]
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #4F46E5;">Welcome to Reddit SaaS Validator! 🚀</h1>
            
            <p>Hi {name},</p>
            
            <p>Thanks for joining Reddit SaaS Validator! We're excited to help you validate your next big idea.</p>
            
            <h2 style="color: #4F46E5;">What's Next?</h2>
            <ul>
                <li><strong>Create your first project</strong> - Add your SaaS idea and keywords</li>
                <li><strong>Run validation</strong> - We'll analyze Reddit, Twitter, and LinkedIn</li>
                <li><strong>Get insights</strong> - Review market demand and pain points</li>
            </ul>
            
            <p style="margin-top: 30px;">
                <a href="{settings.FRONTEND_URL}/dashboard" 
                   style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                    Go to Dashboard
                </a>
            </p>
            
            <p style="margin-top: 30px; color: #666; font-size: 14px;">
                Questions? Just reply to this email - we're here to help!
            </p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="color: #999; font-size: 12px;">
                Reddit SaaS Validator<br>
                <a href="{settings.FRONTEND_URL}" style="color: #4F46E5;">Visit Website</a>
            </p>
        </div>
    </body>
    </html>
    """
    
    text = f"""
    Welcome to Reddit SaaS Validator!
    
    Hi {name},
    
    Thanks for joining! We're excited to help you validate your next big idea.
    
    What's Next?
    - Create your first project
    - Run validation across Reddit, Twitter, and LinkedIn
    - Get actionable insights
    
    Get started: {settings.FRONTEND_URL}/dashboard
    
    Questions? Just reply to this email!
    """
    
    return await send_email(user_email, "Welcome to Reddit SaaS Validator!", html, text)


async def send_validation_complete_email(
    user_email: str,
    project_name: str,
    score: int,
    verdict: str,
    project_id: int
):
    """Send notification when validation is complete"""
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #4F46E5;">Validation Complete! ✅</h1>
            
            <p>Your validation for <strong>{project_name}</strong> is ready!</p>
            
            <div style="background-color: #F3F4F6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h2 style="margin-top: 0;">Results Summary</h2>
                <p style="font-size: 32px; font-weight: bold; color: #4F46E5; margin: 10px 0;">
                    {score}/100
                </p>
                <p style="font-size: 18px; margin: 10px 0;">
                    {verdict}
                </p>
            </div>
            
            <p>
                <a href="{settings.FRONTEND_URL}/projects/{project_id}" 
                   style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                    View Full Results
                </a>
            </p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="color: #999; font-size: 12px;">
                Reddit SaaS Validator<br>
                <a href="{settings.FRONTEND_URL}" style="color: #4F46E5;">Visit Website</a>
            </p>
        </div>
    </body>
    </html>
    """
    
    text = f"""
    Validation Complete!
    
    Your validation for "{project_name}" is ready!
    
    Score: {score}/100
    Verdict: {verdict}
    
    View results: {settings.FRONTEND_URL}/projects/{project_id}
    """
    
    return await send_email(user_email, f"Validation Complete: {project_name}", html, text)


async def send_payment_failed_email(user_email: str, user_name: Optional[str] = None):
    """Send notification when payment fails"""
    name = user_name or user_email.split("@")[0]
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #DC2626;">Payment Failed ⚠️</h1>
            
            <p>Hi {name},</p>
            
            <p>We couldn't process your payment for Reddit SaaS Validator.</p>
            
            <p>This usually happens when:</p>
            <ul>
                <li>Your card has expired</li>
                <li>Insufficient funds</li>
                <li>Your bank declined the charge</li>
            </ul>
            
            <p>Please update your payment method to continue using our service.</p>
            
            <p>
                <a href="{settings.FRONTEND_URL}/billing" 
                   style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                    Update Payment Method
                </a>
            </p>
            
            <p style="margin-top: 30px; color: #666; font-size: 14px;">
                Need help? Reply to this email or contact support.
            </p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="color: #999; font-size: 12px;">
                Reddit SaaS Validator<br>
                <a href="{settings.FRONTEND_URL}" style="color: #4F46E5;">Visit Website</a>
            </p>
        </div>
    </body>
    </html>
    """
    
    text = f"""
    Payment Failed
    
    Hi {name},
    
    We couldn't process your payment for Reddit SaaS Validator.
    
    Please update your payment method: {settings.FRONTEND_URL}/billing
    
    Need help? Reply to this email.
    """
    
    return await send_email(user_email, "Payment Failed - Action Required", html, text)


async def send_subscription_cancelled_email(user_email: str, user_name: Optional[str] = None):
    """Send notification when subscription is cancelled"""
    name = user_name or user_email.split("@")[0]
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #4F46E5;">Subscription Cancelled</h1>
            
            <p>Hi {name},</p>
            
            <p>Your Reddit SaaS Validator subscription has been cancelled.</p>
            
            <p>You'll continue to have access until the end of your billing period.</p>
            
            <p>We're sad to see you go! If there's anything we could have done better, we'd love to hear from you.</p>
            
            <p>
                <a href="{settings.FRONTEND_URL}/dashboard" 
                   style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                    Reactivate Subscription
                </a>
            </p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="color: #999; font-size: 12px;">
                Reddit SaaS Validator<br>
                <a href="{settings.FRONTEND_URL}" style="color: #4F46E5;">Visit Website</a>
            </p>
        </div>
    </body>
    </html>
    """
    
    text = f"""
    Subscription Cancelled
    
    Hi {name},
    
    Your Reddit SaaS Validator subscription has been cancelled.
    
    You'll continue to have access until the end of your billing period.
    
    Reactivate anytime: {settings.FRONTEND_URL}/dashboard
    """
    
    return await send_email(user_email, "Subscription Cancelled", html, text)
