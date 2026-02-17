#!/bin/bash

# BetEdge Startup Script - Start all services for local development

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "🚀 Starting BetEdge..."
echo "Project: $PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites OK${NC}"

# Check .env exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  backend/.env not found${NC}"
    echo "Please create backend/.env with required configuration"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Install backend dependencies if needed
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv backend/venv
fi

# Activate venv and install
echo -e "${YELLOW}📦 Installing backend dependencies...${NC}"
source backend/venv/bin/activate
pip install -q -r backend/requirements.txt

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    cd frontend
    npm install --silent
    cd ..
fi

# Initialize database if needed
if [ ! -f "backend/betedge.db" ]; then
    echo -e "${YELLOW}📦 Initializing database...${NC}"
    python3 << 'PYEOF'
import sys
sys.path.insert(0, 'backend')
from app import app, db

with app.app_context():
    db.create_all()
    print('✅ Database initialized')
PYEOF
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Stopping services...${NC}"
    kill %1 2>/dev/null || true
    kill %2 2>/dev/null || true
    wait
    echo -e "${GREEN}✅ All services stopped${NC}"
}

trap cleanup EXIT

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}   🎯 BetEdge Starting...${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""

# Start backend
echo -e "${YELLOW}▶️  Starting API server (port 5000)...${NC}"
source backend/venv/bin/activate
cd backend
python3 -u app.py > ../logs/api.log 2>&1 &
BACKEND_PID=$!
cd ..

sleep 2

# Check if backend started
if ! curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    cat logs/api.log
    exit 1
fi

echo -e "${GREEN}✅ API running at http://localhost:5000${NC}"

# Start frontend
echo -e "${YELLOW}▶️  Starting frontend (port 3000)...${NC}"
cd frontend
npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 5

# Check if frontend started
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${RED}❌ Frontend failed to start${NC}"
    cat logs/frontend.log
    exit 1
fi

echo -e "${GREEN}✅ Frontend running at http://localhost:3000${NC}"

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}   🎉 BetEdge is Running!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "📊 Dashboard: ${YELLOW}http://localhost:3000${NC}"
echo -e "⚙️  API Docs: ${YELLOW}http://localhost:5000/api/docs${NC}"
echo -e "📝 Logs: ${YELLOW}logs/${NC}"
echo ""
echo "Commands:"
echo "  - Ctrl+C to stop"
echo "  - View logs: tail -f logs/api.log"
echo ""

# Keep process running
wait
