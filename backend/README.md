# Reddit SaaS Validator - Backend

FastAPI backend with Stripe, Resend, and Celery integration.

## Features

✅ **Authentication** - JWT-based auth with email/password  
✅ **Stripe Integration** - Subscriptions + webhooks  
✅ **Email Service** - Resend for transactional emails  
✅ **Async Validation** - Celery for background tasks  
✅ **Database** - PostgreSQL with SQLAlchemy + Alembic  

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env
cp .env.example .env

# Edit .env with your keys
nano .env
```

**Required keys:**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret (generate with `openssl rand -hex 32`)
- `STRIPE_SECRET_KEY` - From Stripe dashboard
- `STRIPE_WEBHOOK_SECRET` - From Stripe webhook settings
- `RESEND_API_KEY` - From Resend dashboard
- `REDIS_URL` - Redis connection (for Celery)

### 3. Setup Database

```bash
# Run migrations
alembic upgrade head
```

### 4. Start Services

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - FastAPI:**
```bash
uvicorn app.main:app --reload --port 8000
```

**Terminal 3 - Celery Worker:**
```bash
./start_celery.sh
```

## API Endpoints

### Auth
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user

### Projects
- `POST /projects` - Create project (triggers validation)
- `GET /projects` - List user's projects
- `GET /projects/{id}` - Get project with analysis
- `POST /projects/{id}/validate` - Retry validation
- `DELETE /projects/{id}` - Delete project

### Stripe
- `POST /stripe/create-checkout-session` - Create Stripe checkout
- `POST /stripe/webhook` - Stripe webhook handler
- `GET /stripe/subscription` - Get user's subscription
- `POST /stripe/cancel-subscription` - Cancel subscription

## Stripe Plans

| Plan | Price | Validations | Features |
|------|-------|-------------|----------|
| **Starter** | $29/mo | 100/mo | Basic validation |
| **Pro** | $79/mo | 500/mo | + Priority support |
| **Enterprise** | $199/mo | Unlimited | + White-label |

## Celery Tasks

- `run_validation(project_id)` - Run full validation
- `test_task(message)` - Simple test task

Monitor tasks:
```bash
celery -A app.celery_app inspect active
```

## Development

### Run Tests
```bash
pytest
```

### Database Migrations

Create migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

### API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

See [DEPLOY.md](../DEPLOY.md) for Railway deployment instructions.

## Troubleshooting

**Celery not picking up tasks?**
- Check Redis is running: `redis-cli ping`
- Verify `REDIS_URL` in `.env`
- Restart Celery worker

**Database connection error?**
- Check PostgreSQL is running
- Verify `DATABASE_URL` format
- Run migrations: `alembic upgrade head`

**Stripe webhook not working?**
- Use Stripe CLI for local testing: `stripe listen --forward-to localhost:8000/stripe/webhook`
- Copy webhook secret to `.env`

## License

MIT
