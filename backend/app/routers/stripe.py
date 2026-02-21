"""
Stripe payment and subscription router
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Header
from sqlalchemy.orm import Session
import stripe
import os
from typing import Optional

from ..database import get_db
from ..models import User, Subscription
from ..auth import get_current_user
from ..schemas import SubscriptionCreate, SubscriptionResponse
from ..config import settings
from ..email import send_payment_failed_email, send_subscription_cancelled_email

router = APIRouter(prefix="/stripe", tags=["stripe"])

# Initialize Stripe (only if configured)
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/create-checkout-session")
async def create_checkout_session(
    plan: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create Stripe checkout session for subscription
    
    Plans:
    - starter: $29/month (100 validations)
    - pro: $79/month (500 validations)
    - enterprise: $199/month (unlimited)
    """
    
    price_ids = {
        "starter": settings.STRIPE_PRICE_ID_STARTER,
        "pro": settings.STRIPE_PRICE_ID_PRO,
        "enterprise": settings.STRIPE_PRICE_ID_ENTERPRISE,
    }
    
    if plan not in price_ids:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            line_items=[
                {
                    "price": price_ids[plan],
                    "quantity": 1,
                },
            ],
            mode="subscription",
            success_url=f"{settings.FRONTEND_URL}/dashboard?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/pricing",
            metadata={
                "user_id": str(current_user.id),
                "plan": plan,
            },
        )
        
        return {"checkout_url": checkout_session.url}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhooks
    """
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await handle_checkout_completed(session, db)
    
    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        await handle_subscription_updated(subscription, db)
    
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        await handle_subscription_deleted(subscription, db)
    
    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        await handle_payment_failed(invoice, db)
    
    return {"status": "success"}


async def handle_checkout_completed(session, db: Session):
    """Handle successful checkout"""
    user_id = session["metadata"]["user_id"]
    plan = session["metadata"]["plan"]
    
    # Get Stripe subscription
    stripe_subscription = stripe.Subscription.retrieve(session["subscription"])
    
    # Create or update subscription in DB
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
    
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    
    if subscription:
        # Update existing
        subscription.stripe_subscription_id = stripe_subscription.id
        subscription.stripe_customer_id = stripe_subscription.customer
        subscription.plan = plan
        subscription.status = "active"
        subscription.current_period_end = stripe_subscription.current_period_end
    else:
        # Create new
        subscription = Subscription(
            user_id=user_id,
            stripe_subscription_id=stripe_subscription.id,
            stripe_customer_id=stripe_subscription.customer,
            plan=plan,
            status="active",
            current_period_end=stripe_subscription.current_period_end,
        )
        db.add(subscription)
    
    db.commit()


async def handle_subscription_updated(subscription_data, db: Session):
    """Handle subscription updates"""
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_data["id"]
    ).first()
    
    if subscription:
        subscription.status = subscription_data["status"]
        subscription.current_period_end = subscription_data["current_period_end"]
        db.commit()


async def handle_subscription_deleted(subscription_data, db: Session):
    """Handle subscription cancellation"""
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_data["id"]
    ).first()
    
    if subscription:
        subscription.status = "cancelled"
        db.commit()
        
        # Send email notification
        user = db.query(User).filter(User.id == subscription.user_id).first()
        if user:
            try:
                await send_subscription_cancelled_email(user.email, user.full_name)
            except Exception as e:
                print(f"Failed to send cancellation email: {e}")


async def handle_payment_failed(invoice, db: Session):
    """Handle failed payment"""
    subscription = db.query(Subscription).filter(
        Subscription.stripe_customer_id == invoice["customer"]
    ).first()
    
    if subscription:
        subscription.status = "past_due"
        db.commit()
        
        # Send email notification
        user = db.query(User).filter(User.id == subscription.user_id).first()
        if user:
            try:
                await send_payment_failed_email(user.email, user.full_name)
            except Exception as e:
                print(f"Failed to send payment failed email: {e}")


@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        return {"status": "none"}
    
    return {
        "plan": subscription.plan,
        "status": subscription.status,
        "current_period_end": subscription.current_period_end,
    }


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel user's subscription"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription")
    
    try:
        # Cancel at period end (no immediate cancellation)
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        return {"status": "cancellation_scheduled"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
