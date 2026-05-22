# Deployment Guide

This project deploys cleanly as two services:

- Frontend: Vercel, from `frontend/`
- Backend API: Render, from `backend/`
- Database: Supabase Postgres
- Redis: Upstash Redis

## 1. Create Your Own GitHub Repository

```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

## 2. Backend: Render

Create a Render Blueprint from this repository. The root `render.yaml` creates the API service.

Required backend environment variables:

```env
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/postgres
DATABASE_SSL=true
REDIS_URL=redis://default:PASSWORD@HOST:PORT
SECRET_KEY=generate-a-long-random-secret
CORS_ORIGINS=["https://YOUR_FRONTEND_DOMAIN"]
APP_NAME=Enterprise Grade AI Copilot API
SEED_DEMO_USERS=false
```

Optional AI and product integrations:

```env
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
TAVILY_API_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

Verify after deployment:

```bash
curl https://YOUR_BACKEND_DOMAIN/health
```

## 3. Frontend: Vercel

Import the same GitHub repository in Vercel and set the root directory to `frontend`.

Required frontend environment variables:

```env
NEXT_PUBLIC_APP_URL=https://YOUR_FRONTEND_DOMAIN
NEXT_PUBLIC_APP_NAME=Enterprise Grade AI Copilot
NEXT_PUBLIC_API_URL=https://YOUR_BACKEND_DOMAIN
NEXT_PUBLIC_WS_URL=wss://YOUR_BACKEND_DOMAIN
NEXTAUTH_URL=https://YOUR_FRONTEND_DOMAIN
NEXTAUTH_SECRET=generate-a-long-random-secret
```

Optional OAuth and telemetry:

```env
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
AZURE_AD_CLIENT_ID=
AZURE_AD_CLIENT_SECRET=
AZURE_AD_TENANT_ID=
NEXT_PUBLIC_POSTHOG_KEY=
NEXT_PUBLIC_SENTRY_DSN=
```

## 4. Production Checks

Before public launch:

- Keep `SEED_DEMO_USERS=false`.
- Confirm no inherited demo credentials are shown in the UI.
- Confirm `CORS_ORIGINS` contains the exact frontend URL.
- Upload at least one document and test chat citations.
- Test `/auth/register`, `/auth/login`, `/knowledge/documents/upload`, and `/conversations`.
- Replace all placeholder legal/contact emails with your real domain emails.
