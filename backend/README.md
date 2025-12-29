# Todo Backend API

FastAPI backend for the Todo Web Application.

## Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix/MacOS:
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

## Running

```bash
uvicorn src.main:app --reload --port 8000
```

## Testing

```bash
pytest tests/ -v
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `DATABASE_URL` - PostgreSQL connection string
- `BETTER_AUTH_SECRET` - JWT secret key
