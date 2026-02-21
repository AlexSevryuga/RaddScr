# 🚀 Quick Deploy Instructions

## Status: READY TO DEPLOY ✅

All code is prepared and tested. Follow these steps:

---

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `reddit-saas-validator`
3. Description: "Multi-platform SaaS idea validation tool"
4. Visibility: **Private** (recommended) or Public
5. **Do NOT** initialize with README (we already have one)
6. Click "Create repository"

---

## Step 2: Push Code to GitHub

```bash
cd /Users/aleksej/clawd/reddit-saas-validator

# Set remote (replace with YOUR GitHub username)
git remote set-url origin https://github.com/YOUR_USERNAME/reddit-saas-validator.git

# Push to GitHub
git push -u origin main
```

---

## Step 3: Deploy Backend on Railway

### 3.1 Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub

### 3.2 Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Authorize Railway to access your GitHub
4. Select `reddit-saas-validator`

### 3.3 Add PostgreSQL
1. In Railway project → Click "New"
2. Select "Database" → "PostgreSQL"
3. Wait for deployment (Railway auto-sets DATABASE_URL)

### 3.4 Add Redis
1. In Railway project → Click "New"
2. Select "Database" → "Redis"
3. Wait for deployment (Railway auto-sets REDIS_URL)

### 3.5 Configure Backend Service
1. Click on your backend service
2. Go to "Variables" tab
3. Add these variables:

```bash
SECRET_KEY=generate-this-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Stripe Test Keys (get from https://dashboard.stripe.com/test/apikeys)
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
STRIPE_PRICE_ID_STARTER=price_your_starter_id
STRIPE_PRICE_ID_PRO=price_your_pro_id
STRIPE_PRICE_ID_ENTERPRISE=price_your_enterprise_id

# Resend Email (get from https://resend.com/api-keys)
RESEND_API_KEY=re_your_key_here
FROM_EMAIL=noreply@yourdomain.com

# URLs (update after Vercel deployment)
FRONTEND_URL=https://your-app.vercel.app
BACKEND_URL=${{RAILWAY_PUBLIC_DOMAIN}}
```

### 3.6 Set Root Directory
1. In Railway backend service → Settings
2. Root Directory: `backend`
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3.7 Deploy
1. Railway will auto-deploy on push
2. Get your backend URL from service settings

### 3.8 Initialize Database
1. In Railway → Backend service → Shell
2. Run: `python init_db.py`

---

## Step 4: Deploy Frontend on Vercel

### 4.1 Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub

### 4.2 Import Project
1. Click "New Project"
2. Import `reddit-saas-validator`
3. Framework Preset: Next.js (auto-detected)
4. **Root Directory:** `frontend`
5. Click "Deploy"

### 4.3 Configure Environment Variables
After deployment:
1. Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add these:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
```

### 4.4 Redeploy
1. Trigger new deployment (Vercel → Deployments → Redeploy)

---

## Step 5: Configure Stripe Webhook

1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Endpoint URL: `https://your-backend.up.railway.app/stripe/webhook`
4. Select events to send:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
5. Copy webhook signing secret
6. Update `STRIPE_WEBHOOK_SECRET` in Railway

---

## Step 6: Update Backend Environment

In Railway, update `FRONTEND_URL`:
```bash
FRONTEND_URL=https://your-app.vercel.app
```

Trigger redeploy.

---

## Step 7: Test Production

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Register a new account
3. Create a test project
4. Try Stripe checkout (test mode: `4242 4242 4242 4242`)

---

## Step 8: (Optional) Deploy Celery Worker

### 8.1 Add Celery Service
1. In Railway → Click "New" → "Empty Service"
2. Name: "celery-worker"
3. Connect to same GitHub repo
4. Root Directory: `backend`

### 8.2 Configure Variables
1. Copy ALL environment variables from backend service
2. Add these:
```bash
# Same as backend (copy all)
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
# ... rest of variables
```

### 8.3 Set Start Command
```bash
celery -A app.celery_app worker --loglevel=info --queues=validation,celery
```

### 8.4 Deploy
Worker will start processing validation tasks

---

## Generate Secret Key

```bash
openssl rand -hex 32
```

---

## Create Stripe Products

1. Go to https://dashboard.stripe.com/test/products
2. Create 3 products:
   - **Starter:** $29/month recurring
   - **Pro:** $79/month recurring
   - **Enterprise:** $199/month recurring
3. Copy price IDs (start with `price_...`)
4. Add to Railway environment variables

---

## Monitoring

### Health Checks
- Backend: `https://your-backend.up.railway.app/health`
- Frontend: `https://your-app.vercel.app`

### Logs
- Railway: Project → Backend → Logs
- Vercel: Project → Logs

---

## Troubleshooting

### Backend Not Starting
- Check Railway logs
- Verify all environment variables are set
- Check PostgreSQL is running

### Frontend Can't Connect to Backend
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings in backend
- Ensure Railway backend is running

### Stripe Webhook Fails
- Verify webhook URL is correct
- Check webhook secret matches
- Check Railway backend logs

---

## Cost Summary

**Railway:**
- Backend: ~$5/month
- PostgreSQL: ~$5/month
- Redis: ~$5/month
- Celery worker: ~$5/month
- **Total: ~$20/month**

**Vercel:**
- Free plan (sufficient for MVP)

**Total: ~$20-25/month**

---

## Next Steps After Deployment

1. [ ] Test all features in production
2. [ ] Set up custom domain
3. [ ] Configure production Stripe keys
4. [ ] Set up monitoring/alerting
5. [ ] Create backup strategy
6. [ ] Review security settings
7. [ ] Launch! 🎉

---

## Need Help?

- Full guide: [DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md)
- Test results: [TEST_LOG.md](./TEST_LOG.md)
- Project docs: [README.md](./README.md)

---

**Your application is READY TO DEPLOY! 🚀**

Good luck with your launch!
