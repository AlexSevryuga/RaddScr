# Reddit SaaS Validator - Deployment Guide

## Railway Backend Deployment

### Prerequisites
1. Railway account (https://railway.app)
2. GitHub repository
3. Stripe account (test/production keys)
4. Resend account (API key)

### Step 1: Push to GitHub

```bash
cd /Users/aleksej/clawd/reddit-saas-validator
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Deploy Backend on Railway

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect Python and deploy

### Step 3: Add PostgreSQL Database

1. In Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set `DATABASE_URL` variable

### Step 4: Add Redis

1. In Railway project, click "New"
2. Select "Database" → "Redis"
3. Railway will automatically set `REDIS_URL` variable

### Step 5: Configure Environment Variables

In Railway backend service, add these variables:

```bash
# JWT
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Stripe (from https://dashboard.stripe.com/test/apikeys)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_STARTER=price_...
STRIPE_PRICE_ID_PRO=price_...
STRIPE_PRICE_ID_ENTERPRISE=price_...

# Email (from https://resend.com/api-keys)
RESEND_API_KEY=re_...
FROM_EMAIL=noreply@yourdomain.com

# URLs (will update after deployment)
FRONTEND_URL=https://your-app.vercel.app
BACKEND_URL=https://your-backend.up.railway.app
```

### Step 6: Deploy Celery Worker (Optional)

1. In Railway, duplicate the backend service
2. Rename to "celery-worker"
3. Change start command to:
   ```
   celery -A app.celery_app worker --loglevel=info
   ```
4. Use same environment variables

### Step 7: Run Database Migration

In Railway backend service terminal:
```bash
python init_db.py
```

Or connect via Railway CLI:
```bash
railway run python init_db.py
```

---

## Vercel Frontend Deployment

### Step 1: Install Vercel CLI (optional)

```bash
npm install -g vercel
```

### Step 2: Deploy via Vercel Dashboard

1. Go to https://vercel.com
2. Click "New Project"
3. Import your GitHub repository
4. Set root directory: `frontend`
5. Framework Preset: Next.js (auto-detected)
6. Click "Deploy"

### Step 3: Configure Environment Variables

In Vercel project settings → Environment Variables:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Step 4: Redeploy

After adding variables, trigger a new deployment.

---

## Post-Deployment

### 1. Update Backend Environment

In Railway, update:
```bash
FRONTEND_URL=https://your-app.vercel.app
```

### 2. Configure Stripe Webhook

1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Endpoint URL: `https://your-backend.up.railway.app/stripe/webhook`
4. Events to send:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
5. Copy webhook secret → Update `STRIPE_WEBHOOK_SECRET` in Railway

### 3. Test in Production

1. Visit your Vercel URL
2. Register a new account
3. Create a test project
4. Try Stripe checkout (test mode)

---

## Monitoring

### Railway Logs
```bash
railway logs --service backend
railway logs --service celery-worker
```

### Health Checks
- Backend API: `https://your-backend.up.railway.app/health`
- Frontend: `https://your-app.vercel.app`

---

## Troubleshooting

### Database Connection Error
- Check `DATABASE_URL` is set in Railway
- Verify PostgreSQL service is running

### Stripe Webhook Failing
- Check webhook secret matches Railway env var
- Verify endpoint URL is correct
- Check Railway logs for errors

### Celery Tasks Not Running
- Verify Redis is running
- Check celery-worker logs
- Ensure `REDIS_URL` is set

---

## Scaling

### Railway
- Add more workers: Duplicate celery-worker service
- Upgrade database: Railway dashboard → PostgreSQL settings
- Add more memory/CPU: Service settings

### Vercel
- Automatic scaling (handled by Vercel)
- Upgrade plan for more bandwidth/builds

---

## Cost Estimate

### Railway (Hobby Plan)
- Backend service: ~$5/month
- PostgreSQL: ~$5/month
- Redis: ~$5/month
- Celery worker: ~$5/month
- **Total: ~$20/month**

### Vercel (Free Plan)
- Hosting: Free
- Bandwidth: 100GB/month
- Upgrade to Pro ($20/mo) for production

**Total monthly: ~$20-40**

---

## Quick Deploy Commands

### Backend (Railway CLI)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up

# Add PostgreSQL
railway add --database postgresql

# Add Redis
railway add --database redis

# View logs
railway logs
```

### Frontend (Vercel CLI)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel

# Production deploy
vercel --prod
```

---

## Security Checklist

- [ ] Generate strong SECRET_KEY (32+ characters)
- [ ] Use production Stripe keys (not test)
- [ ] Verify FROM_EMAIL domain in Resend
- [ ] Enable Railway's built-in firewall
- [ ] Set up custom domain with HTTPS
- [ ] Configure CORS properly in backend
- [ ] Review Railway access logs regularly

---

## Backup Strategy

### Database Backups (Railway)
1. Railway dashboard → PostgreSQL
2. Enable automated backups (daily)
3. Or use `pg_dump`:
   ```bash
   railway run pg_dump $DATABASE_URL > backup.sql
   ```

### Code Backups
- GitHub repository (already backed up)
- Tag releases: `git tag v1.0.0 && git push --tags`

---

Good luck with your deployment! 🚀
