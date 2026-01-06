.PHONY: backend-dev mcp-dev frontend-dev chat-dev install test clean

# Run backend API server
backend-dev:
	cd backend && uv run uvicorn src.main:app --reload --port 8000

# Run MCP server (required for AI chat)
mcp-dev:
	cd backend && uv run python -m src.mcp_server

# Run frontend dev server
frontend-dev:
	cd frontend && npm run dev

# Run all three services for chat development (requires tmux or run in separate terminals)
chat-dev:
	@echo "Starting all services..."
	@echo "Run these commands in separate terminals:"
	@echo ""
	@echo "  Terminal 1: make backend-dev"
	@echo "  Terminal 2: make mcp-dev"
	@echo "  Terminal 3: make frontend-dev"
	@echo ""
	@echo "Or use: make chat-dev-parallel (requires GNU parallel)"

# Run all services in background (logs to files)
chat-dev-bg:
	@echo "Starting backend..."
	cd backend && uv run uvicorn src.main:app --reload --port 8000 > ../backend.log 2>&1 &
	@echo "Starting MCP server..."
	cd backend && uv run python -m src.mcp_server > ../mcp.log 2>&1 &
	@echo "Starting frontend..."
	cd frontend && npm run dev > ../frontend.log 2>&1 &
	@echo ""
	@echo "All services started in background!"
	@echo "Logs: backend.log, mcp.log, frontend.log"
	@echo "Stop with: make stop"

# Stop all background services
stop:
	@echo "Stopping services..."
	-pkill -f "uvicorn src.main:app"
	-pkill -f "python -m src.mcp_server"
	-pkill -f "next dev"
	-lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	-lsof -ti:8001 | xargs kill -9 2>/dev/null || true
	-lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@echo "Clearing logs..."
	-rm -f *.log
	@echo "Services stopped and logs cleared."

# Install all dependencies
install:
	cd backend && uv sync
	cd frontend && npm install

# Run all tests
test:
	cd backend && pytest
	cd frontend && npm test

# Backend tests only
test-backend:
	cd backend && pytest

# Frontend tests only
test-frontend:
	cd frontend && npm test

# Clean logs and temp files
clean:
	rm -f *.log
	rm -rf backend/__pycache__ backend/src/__pycache__
	rm -rf frontend/.next

# Show help
help:
	@echo "Available commands:"
	@echo "  make backend-dev    - Run backend API server (port 8000)"
	@echo "  make mcp-dev        - Run MCP server for AI tools"
	@echo "  make frontend-dev   - Run frontend dev server (port 3000)"
	@echo "  make chat-dev       - Show instructions for all services"
	@echo "  make chat-dev-bg    - Run all services in background"
	@echo "  make stop           - Stop all background services"
	@echo "  make install        - Install all dependencies"
	@echo "  make test           - Run all tests"
	@echo "  make clean          - Clean logs and temp files"
