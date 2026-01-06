#!/bin/bash

# Quickstart Validation Script
# Validates that the AI chatbot implementation works end-to-end

set -e

echo "🚀 Starting AI Chatbot Quickstart Validation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if required files exist
echo "📋 Checking required files..."

required_files=(
    "backend/.env"
    "frontend/.env.local"
    "backend/src/mcp_server.py"
    "backend/src/routes/chat.py"
    "frontend/src/app/dashboard/chat/page.tsx"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "Found $file"
    else
        print_error "Missing $file"
        exit 1
    fi
done

# Check environment variables
echo "🔧 Checking environment configuration..."

if [ -f "backend/.env" ]; then
    if grep -q "DATABASE_URL" backend/.env && grep -q "GEMINI_API_KEY" backend/.env; then
        print_status "Backend environment configured"
    else
        print_error "Backend .env missing required variables"
        exit 1
    fi
fi

if [ -f "frontend/.env.local" ]; then
    if grep -q "NEXT_PUBLIC_API_URL" frontend/.env.local; then
        print_status "Frontend environment configured"
    else
        print_error "Frontend .env.local missing required variables"
        exit 1
    fi
fi

# Start backend server
echo "🔄 Starting backend server..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    print_warning "No virtual environment found. Creating one..."
    python -m venv venv
    source venv/bin/activate
    pip install -e ".[dev]"
else
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
fi

# Start backend in background
echo "Starting FastAPI server..."
uvicorn src.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    print_status "Backend server is running"
else
    print_error "Backend server failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Start MCP server
echo "🤖 Starting MCP server..."
python src/mcp_server.py &
MCP_PID=$!

# Wait for MCP server to start
sleep 3

# Check if MCP server is running
if curl -s http://localhost:8001/health > /dev/null; then
    print_status "MCP server is running"
else
    print_warning "MCP server may not be running (this is optional for some setups)"
fi

cd ..

# Start frontend server
echo "🎨 Starting frontend server..."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    print_warning "Installing frontend dependencies..."
    npm install
fi

# Start frontend in background
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 10

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null; then
    print_status "Frontend server is running"
else
    print_error "Frontend server failed to start"
    kill $BACKEND_PID $MCP_PID $FRONTEND_PID 2>/dev/null || true
    exit 1
fi

cd ..

# Test API endpoints
echo "🧪 Testing API endpoints..."

# Test health endpoint
if curl -s http://localhost:8000/health | grep -q "ok"; then
    print_status "Health endpoint working"
else
    print_error "Health endpoint failed"
fi

# Test chat endpoint (requires authentication, so we expect 401)
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/1/chat | grep -q "401"; then
    print_status "Chat endpoint requires authentication (expected)"
else
    print_warning "Chat endpoint authentication check unclear"
fi

# Manual testing instructions
echo ""
echo "🎯 Manual Testing Instructions:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Register/login with test credentials"
echo "3. Navigate to the Chat page"
echo "4. Try these sample commands:"
echo "   - 'Add a task to buy groceries'"
echo "   - 'Show me my tasks'"
echo "   - 'Mark task 1 as complete'"
echo "   - 'Delete all tasks' (should show confirmation)"
echo ""
echo "Expected behavior:"
echo "✅ Messages appear with typing animation"
echo "✅ Task operations create/update/delete tasks"
echo "✅ Bulk operations show confirmation dialog"
echo "✅ Chat history persists on page reload"
echo ""

# Keep servers running for manual testing
echo "🔄 Servers are running. Press Ctrl+C to stop all services."
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $BACKEND_PID $MCP_PID $FRONTEND_PID 2>/dev/null || true
    print_status "All services stopped"
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Wait for user to stop
wait
