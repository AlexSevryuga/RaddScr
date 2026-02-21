# Reddit SaaS Validator - Frontend

Next.js 14 frontend with TypeScript, Tailwind CSS, and Stripe integration.

## Features

✅ **Modern Stack** - Next.js 14 App Router + TypeScript + Tailwind CSS  
✅ **Authentication** - JWT-based auth with React Context  
✅ **Stripe Checkout** - Integrated payment flows  
✅ **Real-time Updates** - Auto-polling for validation status  
✅ **Responsive Design** - Mobile-first Tailwind UI  

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
# Copy example env
cp .env.local.example .env.local

# Edit .env.local with your values
nano .env.local
```

Required variables:
- `NEXT_PUBLIC_API_URL` - Backend API URL (e.g., `http://localhost:8000`)
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` - Stripe publishable key

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── (auth)/
│   │   ├── login/         # Login page
│   │   └── register/      # Registration page
│   ├── dashboard/         # Dashboard (protected)
│   │   ├── new/          # Create project
│   │   └── projects/[id]/ # Project details
│   ├── pricing/          # Pricing page
│   ├── billing/          # Billing management
│   ├── layout.tsx        # Root layout
│   └── page.tsx          # Landing page
├── components/           # Reusable components
│   └── Navigation.tsx    # Dashboard navigation
├── lib/                  # Utilities
│   ├── api.ts           # API client (axios)
│   └── auth-context.tsx # Auth React Context
└── types/               # TypeScript types
    └── index.ts         # Shared types
```

## Pages

### Public
- `/` - Landing page
- `/login` - User login
- `/register` - User registration
- `/pricing` - Pricing plans

### Protected (requires auth)
- `/dashboard` - Projects list
- `/dashboard/new` - Create new project
- `/dashboard/projects/[id]` - Project results
- `/billing` - Subscription management

## API Integration

API client in `src/lib/api.ts`:
- `authApi.register()`
- `authApi.login()`
- `authApi.getMe()`
- `projectsApi.list()`
- `projectsApi.create()`
- `projectsApi.get(id)`
- `projectsApi.delete(id)`
- `projectsApi.validate(id)`
- `stripeApi.createCheckoutSession(plan)`
- `stripeApi.getSubscription()`
- `stripeApi.cancelSubscription()`

## Stripe Integration

Payment flow:
1. User clicks "Subscribe" on pricing page
2. Frontend calls `/stripe/create-checkout-session`
3. Redirect to Stripe Checkout
4. After payment, Stripe webhook updates subscription
5. User returns to dashboard

## Authentication

JWT token stored in `localStorage`:
- Set on login/register
- Included in API requests via axios interceptor
- Cleared on logout or 401 error

## Development

### Build for Production

```bash
npm run build
npm start
```

### Linting

```bash
npm run lint
```

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy!

### Environment Variables (Production)

```
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

## Troubleshooting

**"Failed to fetch" errors?**
- Check `NEXT_PUBLIC_API_URL` is correct
- Ensure backend is running
- Check CORS settings in backend

**Stripe checkout not working?**
- Verify `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`
- Check Stripe webhook is configured
- Use test mode for development

**Auth redirect loop?**
- Clear localStorage
- Check backend JWT configuration

## License

MIT
