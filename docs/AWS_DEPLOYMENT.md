# AWS Deployment Guide

This guide deploys the project from scratch on AWS:

- Frontend: AWS Amplify Hosting
- Backend: AWS Elastic Beanstalk, Python platform
- Database: Amazon RDS PostgreSQL
- Redis: disabled/skipped for the first deploy

Use one AWS region for all services. For India, prefer Mumbai (`ap-south-1`) if the free tier options you need are available.

## 1. Push The Repo To GitHub

Elastic Beanstalk can deploy from a zip file, but Amplify works best from GitHub.

```bash
git status
git add .
git commit -m "Add AWS deployment configuration"
git push
```

## 2. Create RDS PostgreSQL

In AWS Console:

1. Open RDS.
2. Create database.
3. Choose Standard create.
4. Engine: PostgreSQL.
5. Template: Free tier.
6. DB instance identifier: `enterprise-grade-db`.
7. Master username: `postgres`.
8. Set and save the master password.
9. Public access: Yes for the first deploy.
10. Create database.

After the database is available, copy the endpoint from RDS.

Your backend connection string will be:

```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@YOUR_RDS_ENDPOINT:5432/postgres
DATABASE_SSL=false
```

If your password has special characters such as `@`, `/`, `:`, `?`, `&`, or `%`, URL-encode it or reset it to a strong alphanumeric password.

## 3. Open RDS Security Group

For first deploy:

1. Open the RDS database.
2. Open its VPC security group.
3. Edit inbound rules.
4. Add PostgreSQL rule:
   - Type: PostgreSQL
   - Port: 5432
   - Source: the Elastic Beanstalk instance security group when known

During initial setup only, you may temporarily use your own IP as the source for local testing. Avoid leaving `0.0.0.0/0` open.

## 4. Deploy Backend On Elastic Beanstalk

Create a zip from the backend folder:

```bash
cd backend
zip -r ../backend-eb.zip . -x "venv/*" "__pycache__/*" "*.pyc" "uploads/*"
cd ..
```

In AWS Console:

1. Open Elastic Beanstalk.
2. Create application.
3. Application name: `enterprise-grade-ai-copilot-api`.
4. Platform: Python.
5. Platform branch: latest Python 3.
6. Application code: upload `backend-eb.zip`.
7. Environment type: Single instance.
8. Create environment.

Set Elastic Beanstalk environment properties:

```env
APP_NAME=Enterprise Grade AI Copilot API
APP_VERSION=1.0.0
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@YOUR_RDS_ENDPOINT:5432/postgres
DATABASE_SSL=false
SECRET_KEY=PASTE_OPENSSL_SECRET
CORS_ORIGINS=["http://localhost:3000"]
SEED_DEMO_USERS=false
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
TAVILY_API_KEY=
```

Do not set `REDIS_URL` for the first deploy unless you also create Redis. The app can start without Redis, but password-reset endpoints require Redis and will not work until you add ElastiCache/MemoryDB or another Redis provider.

Generate `SECRET_KEY` locally:

```bash
openssl rand -hex 32
```

After deployment, test:

```bash
curl http://YOUR_EB_DOMAIN/health
```

Expected response:

```json
{"status":"ok"}
```

## 5. Deploy Frontend On Amplify

In AWS Console:

1. Open AWS Amplify.
2. Create new app.
3. Choose GitHub.
4. Select this repository and branch.
5. Amplify should detect `amplify.yml`.
6. Confirm app root is `frontend`.

Set Amplify environment variables:

```env
NEXT_PUBLIC_APP_URL=https://YOUR_AMPLIFY_DOMAIN
NEXT_PUBLIC_APP_NAME=Enterprise Grade AI Copilot
NEXT_PUBLIC_API_URL=http://YOUR_EB_DOMAIN
NEXT_PUBLIC_WS_URL=ws://YOUR_EB_DOMAIN
NEXTAUTH_URL=https://YOUR_AMPLIFY_DOMAIN
NEXTAUTH_SECRET=PASTE_OPENSSL_SECRET
```

Generate `NEXTAUTH_SECRET` locally:

```bash
openssl rand -hex 32
```

Deploy the frontend.

## 6. Update Backend CORS

After Amplify gives you a frontend URL, update Elastic Beanstalk environment properties:

```env
CORS_ORIGINS=["https://YOUR_AMPLIFY_DOMAIN"]
```

Apply changes and wait for Elastic Beanstalk to restart.

## 7. Final Smoke Test

1. Open the Amplify frontend URL.
2. Register a new user.
3. Log in.
4. Visit `/knowledge`.
5. Upload a small text/PDF document.
6. Ask a chat question.

## 8. Cost Safety

Before leaving the app running:

1. Create an AWS Budget alert.
2. Use single-instance Elastic Beanstalk.
3. Use RDS free tier settings only.
4. Stop/delete the Elastic Beanstalk environment and RDS instance when you are not using them.

## Notes

- Elastic Beanstalk official docs support Python apps with a `Procfile`.
- Amplify official docs require `appRoot` in monorepo build settings.
- This project currently builds the frontend with type/lint validation disabled in `frontend/next.config.js`; clean TypeScript should be fixed before serious production use.
