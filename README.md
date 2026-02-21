# Reddit SaaS Validator

🚀 **Multi-platform SaaS idea validation tool**

Validate your SaaS ideas through Reddit, Twitter/X, and LinkedIn analysis before you build.

![Status](https://img.shields.io/badge/status-production-green)
![Tests](https://img.shields.io/badge/tests-7/7_passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## Features

✅ **Multi-platform Analysis**
- Reddit: Scan subreddits for pain points and demand signals
- Twitter/X: Analyze tweets for market sentiment and trends
- LinkedIn: Evaluate B2B potential and enterprise readiness

✅ **Full-Stack SaaS**
- User authentication (JWT)
- Stripe subscription management (3 tiers)
- Email notifications (Resend)
- Async background tasks (Celery)
- Real-time validation status updates

✅ **Beautiful UI**
- Modern Next.js 14 dashboard
- Responsive Tailwind CSS design
- Real-time polling for validation progress
- Comprehensive results with scores and insights

---

## Tech Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL + SQLAlchemy
- **Auth:** JWT (python-jose)
- **Payments:** Stripe
- **Email:** Resend
- **Tasks:** Celery + Redis
- **APIs:** PRAW (Reddit), Tweepy (Twitter), linkedin-api

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **HTTP:** Axios
- **State:** React Context API

---

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL
- Redis

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your keys

# Initialize database
python init_db.py

# Start server
uvicorn app.main:app --reload
```

Backend runs on http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with your backend URL

# Start dev server
npm run dev
```

Frontend runs on http://localhost:3000

### Start Celery Worker (Optional)

```bash
cd backend
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info
```

---

## Deployment

See [DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md) for detailed deployment instructions.

**Quick Deploy:**
- **Backend:** Railway.app (with PostgreSQL + Redis)
- **Frontend:** Vercel

---

## API Documentation

Once the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Main Endpoints

**Authentication:**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

**Projects:**
- `GET /projects` - List user's projects
- `POST /projects` - Create new project (triggers validation)
- `GET /projects/{id}` - Get project with analysis results
- `DELETE /projects/{id}` - Delete project

**Stripe:**
- `POST /stripe/create-checkout-session` - Start subscription
- `POST /stripe/webhook` - Handle Stripe webhooks
- `GET /stripe/subscription` - Get user's subscription
- `POST /stripe/cancel-subscription` - Cancel subscription

---

## Pricing Tiers

| Plan | Price | Validations |
|------|-------|-------------|
| **Starter** | $29/mo | 100/month |
| **Pro** | $79/mo | 500/month |
| **Enterprise** | $199/mo | Unlimited |

---

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest
```

### End-to-End Tests

See [TEST_LOG.md](./TEST_LOG.md) for detailed test results.

**Latest Results:** 7/7 tests PASSED ✅

---

## Project Structure

```
reddit-saas-validator/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── routers/     # API endpoints
│   │   ├── models.py    # SQLAlchemy models
│   │   ├── schemas.py   # Pydantic schemas
│   │   ├── auth.py      # JWT authentication
│   │   ├── email.py     # Resend email service
│   │   └── tasks.py     # Celery tasks
│   ├── migrations/      # Alembic migrations
│   └── src/             # Validation scripts
│       ├── reddit_scraper.py
│       ├── twitter_scraper.py
│       ├── linkedin_scraper.py
│       └── multiplatform_validator.py
├── frontend/            # Next.js frontend
│   └── src/
│       ├── app/         # Next.js pages
│       ├── components/  # React components
│       ├── lib/         # Utils (API client, auth)
│       └── types/       # TypeScript types
└── DEPLOY_GUIDE.md      # Deployment instructions
```

---

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe
STRIPE_SECRET_KEY=sk_...
STRIPE_PUBLISHABLE_KEY=pk_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_STARTER=price_...
STRIPE_PRICE_ID_PRO=price_...
STRIPE_PRICE_ID_ENTERPRISE=price_...

# Email
RESEND_API_KEY=re_...
FROM_EMAIL=noreply@yourdomain.com

# Redis
REDIS_URL=redis://localhost:6379/0

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_...
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License - see [LICENSE](./LICENSE) for details

---

## Support

- **Documentation:** See `/docs` folder
- **Issues:** GitHub Issues
- **Email:** support@yourdomain.com

---

## Roadmap

- [x] MVP launch
- [x] Stripe integration
- [x] Email notifications
- [x] Async validation
- [ ] API rate limiting
- [ ] Export reports (PDF/CSV)
- [ ] Custom branding (Enterprise)
- [ ] Webhooks API
- [ ] Multi-language support

---

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI powered by [Next.js](https://nextjs.org/) and [Tailwind CSS](https://tailwindcss.com/)
- Icons from [Heroicons](https://heroicons.com/)

---

**Made with ❤️ by the Reddit SaaS Validator team**

🌟 Star us on GitHub if you find this useful!
