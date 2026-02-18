#!/bin/bash
# Kick Lab AI - Backend Startup Script
# This script starts the Flask API server

set -e  # Exit on error

echo "🚀 Starting Kick Lab AI Backend..."

# Change to project directory
cd "$(dirname "$0")"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "   Copy .env.example to .env and configure your environment variables."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Environment variables loaded"
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "🐍 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found (venv or .venv)"
    echo "   Using system Python: $(which python3)"
fi

# Check if database exists, create it if not
if [ ! -f "backend/instance/kicklab.db" ] && [ ! -f "kicklab.db" ]; then
    echo "🗄️  Database not found. Creating database..."
    python3 -c "
from backend.app import app, db
with app.app_context():
    db.create_all()
    print('✅ Database created successfully')
"
else
    echo "✅ Database exists"
fi

# Set Flask environment variables
export FLASK_APP=backend.app
export FLASK_ENV=${FLASK_ENV:-development}
export PORT=${PORT:-5000}

echo ""
echo "🌐 Starting Flask server on http://localhost:$PORT"
echo "   Press Ctrl+C to stop"
echo ""

# Start the Flask application
python3 -m flask run --host=0.0.0.0 --port=$PORT
