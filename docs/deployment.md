# Deployment Guide

**Version**: 1.0.0
**Last Updated**: 2025-12-27

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Database Deployment](#database-deployment)
- [Backend Deployment](#backend-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Docker Deployment](#docker-deployment)
- [Health Checks & Monitoring](#health-checks--monitoring)
- [CI/CD Integration](#cicd-integration)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers deploying the Todo Web Application to production environments. The application consists of three main components:

1. **Database**: PostgreSQL (Neon Serverless)
2. **Backend**: FastAPI application (Python)
3. **Frontend**: Next.js application (Node.js)

### Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Load Balancer                      │
│                  (Optional: Nginx)                   │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌──────────────┐      ┌──────────────┐
│   Frontend   │      │   Backend    │
│  (Next.js)   │      │  (FastAPI)   │
│  Port: 3000  │      │  Port: 8000  │
└──────────────┘      └──────┬───────┘
                              │
                              ▼
                      ┌──────────────┐
                      │  Database    │
                      │ (PostgreSQL) │
                      └──────────────┘
```

### Supported Platforms

- **Frontend**: Vercel, Netlify, AWS Amplify, Docker
- **Backend**: Railway, Render, AWS ECS, Google Cloud Run, Docker
- **Database**: Neon, AWS RDS, Google Cloud SQL, Supabase

---

## Prerequisites

### Required Accounts

- [ ] **Neon**: PostgreSQL database hosting ([Sign up](https://neon.tech))
- [ ] **Vercel**: Frontend hosting (recommended) ([Sign up](https://vercel.com))
- [ ] **Railway/Render**: Backend hosting ([Railway](https://railway.app) | [Render](https://render.com))
- [ ] **GitHub**: Code repository and CI/CD

### Required Tools

- **Git**: Version 2.0+
- **Node.js**: 20+
- **Python**: 3.13+
- **UV**: Python package manager
- **Docker**: Optional, for containerized deployment

### Domain & SSL

- Domain name (optional but recommended)
- SSL certificate (provided by hosting platforms)

---

## Environment Setup

### 1. Environment Variables Validation

Before deployment, validate your environment configuration:

**Backend**:
```bash
cd backend
python validate_env.py
```

**Frontend**:
```bash
cd frontend
node validate-env.js
```

### 2. Generate Secure Secrets

**JWT Secret** (must match between frontend and backend):
```bash
# Generate a secure 32+ character secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Example output: Xq9J4mKp7nR2tY8wZ3vB5cD6fG1hL0o_4jK9mN2pQ8r
```

**Store this value** - you'll need it for both frontend and backend configuration.

### 3. Environment Variables Checklist

#### Backend (.env)

```env
# Database - Neon PostgreSQL connection string
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# JWT Secret (32+ characters, cryptographically random)
BETTER_AUTH_SECRET=Xq9J4mKp7nR2tY8wZ3vB5cD6fG1hL0o_4jK9mN2pQ8r

# CORS - Your frontend URL(s), comma-separated
CORS_ORIGIN=https://your-app.vercel.app

# Logging level
LOG_LEVEL=INFO
```

#### Frontend (.env.local or Platform Secrets)

```env
# Backend API URL
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# JWT Secret (must match backend exactly)
BETTER_AUTH_SECRET=Xq9J4mKp7nR2tY8wZ3vB5cD6fG1hL0o_4jK9mN2pQ8r
```

---

## Database Deployment

### Option 1: Neon (Recommended)

**Why Neon?**
- Serverless PostgreSQL
- Auto-scaling
- Built-in backups
- Pay-per-use pricing
- Excellent for FastAPI + SQLModel

#### Setup Steps

1. **Create Neon Account**: https://neon.tech

2. **Create New Project**:
   ```
   Project Name: todo-app-prod
   Region: Choose closest to your users
   PostgreSQL Version: 15 (or latest)
   ```

3. **Get Connection String**:
   - Navigate to project dashboard
   - Copy connection string
   - Format: `postgresql://user:password@host/neondb?sslmode=require`

4. **Create Database Tables**:
   ```bash
   # Set DATABASE_URL environment variable
   export DATABASE_URL="postgresql://user:password@host/neondb?sslmode=require"

   # Run migrations
   cd backend
   python -c "from src.db import create_tables; import asyncio; asyncio.run(create_tables())"
   ```

5. **Verify Connection**:
   ```bash
   # Test database connection
   python -c "from src.db import engine; import asyncio; asyncio.run(engine.connect())"
   ```

### Option 2: AWS RDS

1. **Create RDS Instance**:
   ```
   Engine: PostgreSQL 15
   Instance Class: db.t3.micro (start small)
   Storage: 20 GB (SSD)
   Public Access: Yes (restrict by security group)
   ```

2. **Configure Security Group**:
   - Allow inbound PostgreSQL (port 5432) from your backend servers
   - Never allow 0.0.0.0/0 in production

3. **Create Database**:
   ```sql
   CREATE DATABASE todo_db;
   ```

4. **Connection String**:
   ```
   postgresql://username:password@instance.region.rds.amazonaws.com:5432/todo_db?sslmode=require
   ```

### Database Security Checklist

- [ ] SSL/TLS enabled (`sslmode=require`)
- [ ] Strong password (20+ characters)
- [ ] Network access restricted to backend servers only
- [ ] Regular backups enabled (automatic on Neon)
- [ ] Monitoring and alerts configured

---

## Backend Deployment

### Option 1: Railway (Recommended for FastAPI)

**Why Railway?**
- Simple Python deployments
- Automatic HTTPS
- Built-in PostgreSQL (or use external)
- Environment variable management
- Free tier available

#### Deployment Steps

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize Project**:
   ```bash
   cd backend
   railway init
   ```

4. **Add Environment Variables**:
   ```bash
   railway variables set DATABASE_URL="postgresql://..."
   railway variables set BETTER_AUTH_SECRET="Xq9..."
   railway variables set CORS_ORIGIN="https://your-frontend.vercel.app"
   railway variables set LOG_LEVEL="INFO"
   ```

5. **Create Procfile** (if not exists):
   ```bash
   cat > Procfile << EOF
   web: uvicorn src.main:app --host 0.0.0.0 --port \$PORT
   EOF
   ```

6. **Deploy**:
   ```bash
   railway up
   ```

7. **Get Deployment URL**:
   ```bash
   railway domain
   # Example: https://your-backend.railway.app
   ```

8. **Verify Deployment**:
   ```bash
   curl https://your-backend.railway.app/health
   # Expected: {"status": "healthy"}
   ```

### Option 2: Render

1. **Create Render Account**: https://render.com

2. **Create New Web Service**:
   - Connect GitHub repository
   - Select `backend` directory
   - Runtime: Python 3.13

3. **Configure Build & Start**:
   ```
   Build Command: pip install -e .
   Start Command: uvicorn src.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Environment Variables** (in Render dashboard):
   ```
   DATABASE_URL=postgresql://...
   BETTER_AUTH_SECRET=Xq9...
   CORS_ORIGIN=https://your-frontend.vercel.app
   LOG_LEVEL=INFO
   ```

5. **Deploy**: Click "Create Web Service"

### Option 3: AWS ECS (Docker)

1. **Build Docker Image**:
   ```bash
   cd backend
   docker build -t todo-backend:latest .
   ```

2. **Push to ECR**:
   ```bash
   aws ecr create-repository --repository-name todo-backend
   docker tag todo-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/todo-backend:latest
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/todo-backend:latest
   ```

3. **Create ECS Task Definition**:
   ```json
   {
     "family": "todo-backend",
     "containerDefinitions": [{
       "name": "backend",
       "image": "<account>.dkr.ecr.us-east-1.amazonaws.com/todo-backend:latest",
       "portMappings": [{"containerPort": 8000}],
       "environment": [
         {"name": "DATABASE_URL", "value": "postgresql://..."},
         {"name": "BETTER_AUTH_SECRET", "value": "Xq9..."},
         {"name": "CORS_ORIGIN", "value": "https://..."},
         {"name": "LOG_LEVEL", "value": "INFO"}
       ]
     }]
   }
   ```

4. **Create ECS Service**:
   ```bash
   aws ecs create-service \
     --cluster todo-cluster \
     --service-name backend \
     --task-definition todo-backend \
     --desired-count 2 \
     --launch-type FARGATE
   ```

### Backend Health Check

After deployment, verify:

```bash
# Health check
curl https://your-backend.railway.app/health
# Expected: {"status": "healthy"}

# API info
curl https://your-backend.railway.app/
# Expected: {"name": "Todo API", "version": "1.0.0", "docs": "/docs"}

# API docs
open https://your-backend.railway.app/docs
```

---

## Frontend Deployment

### Option 1: Vercel (Recommended for Next.js)

**Why Vercel?**
- Built by Next.js creators
- Automatic HTTPS
- Edge network (CDN)
- Preview deployments
- Zero configuration

#### Deployment Steps

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from Frontend Directory**:
   ```bash
   cd frontend
   vercel
   ```

4. **Add Environment Variables** (via Vercel dashboard or CLI):
   ```bash
   vercel env add NEXT_PUBLIC_API_URL
   # Enter: https://your-backend.railway.app

   vercel env add BETTER_AUTH_SECRET
   # Enter: Xq9J4mKp7nR2tY8wZ3vB5cD6fG1hL0o_4jK9mN2pQ8r
   ```

5. **Production Deployment**:
   ```bash
   vercel --prod
   ```

6. **Custom Domain** (optional):
   ```bash
   vercel domains add your-domain.com
   ```

### Option 2: Netlify

1. **Create Netlify Account**: https://netlify.com

2. **Connect Repository**:
   - Link GitHub repository
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `.next`

3. **Add Environment Variables** (in Netlify dashboard):
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   BETTER_AUTH_SECRET=Xq9...
   ```

4. **Deploy**: Click "Deploy site"

### Option 3: Docker (Self-hosted)

1. **Build Frontend**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Create Dockerfile** (if not exists):
   ```dockerfile
   FROM node:20-alpine
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci --only=production
   COPY . .
   RUN npm run build
   EXPOSE 3000
   CMD ["npm", "start"]
   ```

3. **Build and Run**:
   ```bash
   docker build -t todo-frontend .
   docker run -p 3000:3000 \
     -e NEXT_PUBLIC_API_URL=https://your-backend.railway.app \
     -e BETTER_AUTH_SECRET=Xq9... \
     todo-frontend
   ```

### Frontend Verification

After deployment:

```bash
# Check frontend is live
curl https://your-app.vercel.app

# Test API connection
# Open browser and try to register/login
```

---

## Docker Deployment

### Full Stack with Docker Compose

1. **Create Production docker-compose.yml**:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/todo_db
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - CORS_ORIGIN=https://your-frontend-domain.com
      - LOG_LEVEL=INFO
    depends_on:
      - db
    restart: always

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=https://your-backend-domain.com
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
    depends_on:
      - backend
    restart: always

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=todo_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: always

volumes:
  postgres_data:
```

2. **Deploy with Docker Compose**:
   ```bash
   # Create .env file with secrets
   echo "BETTER_AUTH_SECRET=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" > .env
   echo "DB_PASSWORD=$(python -c 'import secrets; print(secrets.token_urlsafe(16))')" >> .env

   # Deploy
   docker-compose up -d

   # Check logs
   docker-compose logs -f
   ```

---

## Health Checks & Monitoring

### Health Check Endpoints

#### Backend Health Check

```bash
curl https://your-backend.railway.app/health
```

**Expected Response**:
```json
{"status": "healthy"}
```

**Monitoring Script**:
```bash
#!/bin/bash
# health-check.sh
BACKEND_URL="https://your-backend.railway.app"

response=$(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/health)

if [ $response -eq 200 ]; then
  echo "✓ Backend is healthy"
  exit 0
else
  echo "✗ Backend is down (HTTP $response)"
  exit 1
fi
```

### Application Monitoring

#### 1. Uptime Monitoring

**Tools**:
- **UptimeRobot**: Free uptime monitoring
- **Pingdom**: Advanced monitoring
- **DataDog**: Full observability

**Setup Example (UptimeRobot)**:
- Monitor: https://your-backend.railway.app/health
- Check interval: 5 minutes
- Alert on: Status != 200

#### 2. Error Tracking

**Sentry Integration**:

```python
# backend/src/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

```typescript
// frontend/src/lib/sentry.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: "your-sentry-dsn",
  tracesSampleRate: 1.0,
});
```

#### 3. Performance Monitoring

**Key Metrics**:
- API response time (target: < 200ms p95)
- Database query time
- Frontend page load time (target: < 2s)
- Error rate (target: < 1%)

**CloudWatch Alarms** (AWS):
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name backend-high-error-rate \
  --alarm-description "Backend error rate > 5%" \
  --metric-name Errors \
  --threshold 5.0 \
  --comparison-operator GreaterThanThreshold
```

### Logging

#### Centralized Logging

**Options**:
1. **CloudWatch Logs** (AWS)
2. **Google Cloud Logging**
3. **Papertrail**
4. **Logtail**

**Backend Logging**:
```python
# Already implemented in src/utils/logger.py
logger.info("user_registered", user_id=user_id, email=email)
```

**Frontend Logging**:
```typescript
// Add Vercel Analytics
import { Analytics } from '@vercel/analytics/react';

export default function App() {
  return (
    <>
      <YourApp />
      <Analytics />
    </>
  );
}
```

---

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install backend dependencies
        run: |
          cd backend
          pip install -e ".[dev]"

      - name: Run backend tests
        run: |
          cd backend
          pytest

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci

      - name: Run frontend tests
        run: |
          cd frontend
          npm test

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm install -g @railway/cli
          cd backend
          railway up --service backend

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        run: |
          npm install -g vercel
          cd frontend
          vercel --prod --token=$VERCEL_TOKEN
```

### Required Secrets

Add to GitHub repository secrets:
- `RAILWAY_TOKEN`: Get from Railway dashboard
- `VERCEL_TOKEN`: Get from Vercel account settings

---

## Rollback Procedures

### Quick Rollback

#### Backend (Railway)

```bash
# List deployments
railway deployments

# Rollback to previous deployment
railway rollback <deployment-id>
```

#### Frontend (Vercel)

```bash
# List deployments
vercel ls

# Rollback to previous deployment
vercel rollback <deployment-url>
```

### Database Rollback

**Important**: Always backup before migrations!

```bash
# Neon: Use point-in-time recovery
# Go to Neon dashboard → Backups → Restore to timestamp

# Manual backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql $DATABASE_URL < backup_20251227_100000.sql
```

---

## Troubleshooting

### Common Issues

#### 1. CORS Errors

**Symptom**: Frontend can't connect to backend

**Solution**:
```python
# backend/src/main.py
# Ensure CORS_ORIGINS includes your frontend URL
CORS_ORIGINS = [
    "https://your-app.vercel.app",
    "https://your-app-git-main.vercel.app",  # Add preview URLs
]
```

#### 2. JWT Secret Mismatch

**Symptom**: "Invalid token" errors

**Solution**:
```bash
# Verify secrets match
# Backend
railway variables | grep BETTER_AUTH_SECRET

# Frontend
vercel env ls | grep BETTER_AUTH_SECRET

# Update if needed
vercel env add BETTER_AUTH_SECRET production
```

#### 3. Database Connection Failures

**Symptom**: "Connection refused" or "SSL error"

**Solution**:
```bash
# Verify DATABASE_URL includes sslmode=require
echo $DATABASE_URL
# Should end with: ?sslmode=require

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

#### 4. Build Failures

**Frontend**:
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

**Backend**:
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
pip install --force-reinstall -e .
```

### Debugging Checklist

- [ ] Check application logs
- [ ] Verify environment variables
- [ ] Test health endpoints
- [ ] Check database connectivity
- [ ] Verify CORS configuration
- [ ] Test JWT token generation
- [ ] Check rate limiting
- [ ] Verify SSL/TLS certificates
- [ ] Review recent deployments
- [ ] Check DNS configuration (if custom domain)

---

## Post-Deployment Checklist

### Security

- [ ] HTTPS enabled on all endpoints
- [ ] JWT_SECRET is strong and unique
- [ ] Database SSL/TLS enabled
- [ ] CORS properly configured (no wildcards)
- [ ] Rate limiting active
- [ ] Error messages don't leak sensitive info
- [ ] Logging configured (no passwords/tokens)

### Performance

- [ ] CDN enabled (Vercel/Netlify do this automatically)
- [ ] Database connection pooling configured
- [ ] API response time < 200ms p95
- [ ] Frontend Lighthouse score > 85

### Monitoring

- [ ] Uptime monitoring configured
- [ ] Error tracking enabled (Sentry)
- [ ] Log aggregation configured
- [ ] Alerts configured for critical issues
- [ ] Health check endpoints monitored

### Backup & Recovery

- [ ] Database backups enabled
- [ ] Backup retention policy defined
- [ ] Recovery procedures documented
- [ ] Rollback procedures tested

---

## Support & Resources

### Documentation

- [API Reference](api.md)
- [Security Guide](security.md)
- [README](../README.md)

### Platform Documentation

- **Railway**: https://docs.railway.app
- **Vercel**: https://vercel.com/docs
- **Neon**: https://neon.tech/docs
- **Render**: https://render.com/docs

### Community

- GitHub Issues: For bug reports and feature requests
- GitHub Discussions: For questions and general discussion

---

**Last Updated**: 2025-12-27
**Version**: 1.0.0
**Next Review**: Monthly
