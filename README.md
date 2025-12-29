# Todo Web Application

A full-stack todo application built with Next.js 16+ and FastAPI, featuring JWT authentication, real-time updates, and a modern UI.

## Overview

This is a production-ready monorepo implementing a spec-driven todo application with:
- Modern Next.js 16+ frontend with App Router
- FastAPI backend with SQLModel ORM
- PostgreSQL (Neon Serverless) database
- JWT-based authentication with Better Auth
- Rate limiting and security hardening
- Comprehensive test coverage (80% backend, 70% frontend)
- Responsive design with Tailwind CSS

## Tech Stack

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **State Management**: Zustand
- **Authentication**: Better Auth with JWT
- **UI Components**: Shadcn/ui (Radix UI)
- **Forms**: React Hook Form + Zod
- **Animations**: Framer Motion
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.13+
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Passlib with bcrypt
- **Validation**: Pydantic v2
- **Logging**: Structlog
- **ASGI Server**: Uvicorn

## Project Structure

```
testing-hackthon2/
├── frontend/              # Next.js 16+ frontend application
│   ├── src/
│   │   ├── app/          # App Router pages and layouts
│   │   ├── components/   # Reusable React components
│   │   ├── lib/          # Utilities and API client
│   │   ├── stores/       # Zustand state management
│   │   └── styles/       # Global styles
│   ├── tests/            # Frontend tests (Jest + React Testing Library)
│   └── package.json
├── backend/              # FastAPI backend application
│   ├── src/
│   │   ├── routes/       # API route handlers
│   │   ├── models.py     # SQLModel database models
│   │   ├── auth.py       # JWT authentication
│   │   ├── db.py         # Database connection
│   │   ├── services/     # Business logic layer
│   │   ├── schemas/      # Pydantic request/response models
│   │   ├── middleware/   # Rate limiting, logging, etc.
│   │   └── utils/        # Helper functions
│   ├── tests/            # Backend tests (pytest)
│   └── pyproject.toml
├── specs/                # Specification documents
│   ├── features/         # Feature specifications
│   ├── api/              # API endpoint documentation
│   ├── database/         # Database schema specs
│   └── 1-todo-web-app/   # Project planning docs
├── docs/                 # Additional documentation
│   ├── api.md           # API reference
│   ├── security.md      # Security review
│   └── deployment.md    # Deployment guide
├── docker-compose.yml   # Docker orchestration
└── README.md           # This file
```

## Quick Start

### Prerequisites

- **Node.js**: 20+ (for frontend)
- **Python**: 3.13+ (for backend)
- **UV**: Python package manager ([install](https://github.com/astral-sh/uv))
- **PostgreSQL**: Neon Serverless account ([sign up](https://neon.tech))
- **Git**: Version control

### 1. Clone the Repository

```bash
git clone <repository-url>
cd testing-hackthon2
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies with UV
uv pip install -e ".[dev]"

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
BETTER_AUTH_SECRET=your-strong-secret-key-change-this-in-production
CORS_ORIGIN=http://localhost:3000
LOG_LEVEL=INFO
EOF

# Update the .env file with your actual database credentials

# Run database migrations
python -c "from src.db import create_tables; import asyncio; asyncio.run(create_tables())"

# Start the backend server
uvicorn src.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from root)
cd frontend

# Install dependencies
npm install

# Create .env.local file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-strong-secret-key-change-this-in-production
EOF

# Make sure BETTER_AUTH_SECRET matches the backend value

# Start the development server
npm run dev
```

Frontend will be available at: http://localhost:3000

### 4. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

## Development

### Backend Development

```bash
cd backend

# Run with auto-reload
uvicorn src.main:app --reload --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Using Docker Compose

Run both frontend and backend together:

```bash
# Start all services
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Environment Variables

### Backend (.env)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `BETTER_AUTH_SECRET` | JWT secret key (min 32 chars) | Yes | - |
| `CORS_ORIGIN` | Allowed CORS origins | No | `http://localhost:3000` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No | `INFO` |

**Important**: Never commit `.env` files to version control. Use `.env.example` as a template.

### Frontend (.env.local)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | Yes | - |
| `BETTER_AUTH_SECRET` | JWT secret (must match backend) | Yes | - |

## Features

### Implemented User Stories

- [x] **User Registration & Login (US1)**: Secure account creation and authentication
- [x] **Task CRUD Operations (US2)**: Create, read, update, and delete tasks
- [x] **User Logout (US3)**: Secure session termination
- [x] **Toggle Task Completion (US4)**: Mark tasks as complete/incomplete
- [x] **User Data Isolation (US5)**: Users can only access their own tasks
- [x] **Responsive UI & Polish (US6)**: Mobile-first design with animations

### Security Features

- JWT-based authentication with token blacklisting
- Bcrypt password hashing with automatic salt generation
- Rate limiting (60 requests/minute per user)
- CORS protection
- SQL injection prevention via parameterized queries
- XSS prevention via React's built-in escaping
- Input validation with Pydantic and Zod
- Secure headers and HTTPS enforcement (production)

### API Features

- RESTful API design
- Comprehensive OpenAPI/Swagger documentation
- Request/response validation
- Structured error responses
- Rate limit headers
- Request ID tracking
- Response time metrics

## Testing

### Backend Tests

Located in `backend/tests/`:
- Unit tests for models, services, and utilities
- Integration tests for API endpoints
- Contract tests for API specifications
- Test coverage: 80%+

```bash
cd backend
pytest
pytest --cov=src --cov-report=html
```

### Frontend Tests

Located in `frontend/tests/`:
- Component tests with React Testing Library
- Integration tests for user flows
- Form validation tests
- Test coverage: 70%+

```bash
cd frontend
npm test
npm run test:coverage
```

## API Documentation

Complete API documentation is available at:
- Interactive docs: http://localhost:8000/docs (Swagger UI)
- Reference docs: http://localhost:8000/redoc (ReDoc)
- Markdown docs: [docs/api.md](docs/api.md)

### Key Endpoints

**Authentication**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user

**Tasks**
- `GET /api/{user_id}/tasks` - List all tasks
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks/{id}` - Get task details
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion

## Monitoring & Observability

### Logging

The backend implements structured JSON logging with:
- Request ID tracking for distributed tracing
- Response time metrics
- Authentication event logging
- Database error logging
- No sensitive data in logs (passwords, tokens)

### Health Checks

- `GET /health` - Application health status
- Database connection verification
- JWT secret validation

## Deployment

See [docs/deployment.md](docs/deployment.md) for comprehensive deployment instructions including:
- Production environment setup
- Database migrations
- Frontend build and deployment
- Backend deployment strategies
- Environment variable configuration
- Health checks and monitoring
- CI/CD integration

## Contributing

This project follows spec-driven development using GitHub Spec-Kit:

1. Review specifications in `/specs`
2. Reference specs when implementing: `@specs/features/file.md`
3. Update specs if requirements change
4. Follow the implementation workflow:
   - Read spec → Implement backend → Implement frontend → Test

## Documentation

- [Project Overview](specs/overview.md)
- [API Reference](docs/api.md)
- [Security Review](docs/security.md)
- [Deployment Guide](docs/deployment.md)
- [Quickstart Guide](specs/1-todo-web-app/quickstart.md)
- [Feature Specifications](specs/features/)
- [Database Schema](specs/database/schema.md)

## Troubleshooting

### Common Issues

**CORS Errors**
```bash
# Check that CORS_ORIGIN in backend .env matches your frontend URL
CORS_ORIGIN=http://localhost:3000
```

**Database Connection Failed**
```bash
# Verify DATABASE_URL format
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
# Ensure Neon database is active and credentials are correct
```

**JWT Errors**
```bash
# Ensure BETTER_AUTH_SECRET matches between frontend and backend
# Must be at least 32 characters for production
```

**Rate Limit Issues**
```bash
# Check headers in response:
# X-RateLimit-Limit: 60
# X-RateLimit-Remaining: 59
# X-RateLimit-Reset: 1735315200
```

**Port Already in Use**
```bash
# Backend (8000)
lsof -ti:8000 | xargs kill -9

# Frontend (3000)
lsof -ti:3000 | xargs kill -9
```

## Performance

- Backend API response time: < 200ms (p95)
- Frontend Lighthouse score: > 85
- Database query optimization with indexes
- Optimistic UI updates for better UX
- Lazy loading and code splitting

## Browser Support

- Chrome/Edge: Last 2 versions
- Firefox: Last 2 versions
- Safari: Last 2 versions
- Mobile: iOS 14+, Android 10+

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions:
1. Check existing documentation in `/docs` and `/specs`
2. Review [Troubleshooting](#troubleshooting) section
3. Open an issue with detailed description and logs

## Acknowledgments

Built with:
- [Next.js](https://nextjs.org/) - React framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL database ORM
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS
- [Better Auth](https://www.better-auth.com/) - Authentication library
- [Shadcn/ui](https://ui.shadcn.com/) - UI component library
- [Neon](https://neon.tech/) - Serverless PostgreSQL

---

**Version**: 1.0.0
**Last Updated**: 2025-12-27
**Generated with**: Spec-Kit Plus
