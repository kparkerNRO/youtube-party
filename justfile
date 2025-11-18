# YouTube Party - Task Runner
# https://github.com/casey/just

# Default recipe to display help information
default:
    @just --list

# Install all dependencies (backend and frontend)
install:
    @echo "📦 Installing backend dependencies..."
    uv sync
    @echo "📦 Installing frontend dependencies..."
    cd frontend && npm install
    @echo "✅ All dependencies installed!"

# Start both backend and frontend in development mode
dev:
    @echo "🚀 Starting YouTube Party in development mode..."
    @echo "   Backend: http://localhost:8000"
    @echo "   Frontend: http://localhost:3000"
    @echo ""
    just _parallel backend frontend

# Start only the backend server
backend:
    @echo "🔧 Starting backend server..."
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Start only the frontend dev server
frontend:
    @echo "⚡ Starting Vite dev server..."
    cd frontend && npm run dev

# Start production server (single process)
prod:
    @echo "🚀 Starting production server..."
    python backend/main.py

# Build frontend for production
build:
    @echo "🏗️  Building frontend..."
    cd frontend && npm run build
    @echo "✅ Build complete! Output in frontend/dist"

# Clean build artifacts and caches
clean:
    @echo "🧹 Cleaning build artifacts..."
    rm -rf frontend/dist
    rm -rf frontend/node_modules/.vite
    rm -rf backend/__pycache__
    rm -rf .pytest_cache
    rm -f queue_state.json
    @echo "✅ Clean complete!"

# Format code with black and prettier
format:
    @echo "🎨 Formatting Python code..."
    -uv run black backend/
    @echo "🎨 Formatting JavaScript code..."
    -cd frontend && npx prettier --write "**/*.{js,html,css}"
    @echo "✅ Formatting complete!"

# Run Python tests
test:
    @echo "🧪 Running tests..."
    uv run pytest
    @echo "✅ Tests complete!"

# Check code quality
lint:
    @echo "🔍 Linting Python code..."
    -uv run ruff check backend/
    @echo "🔍 Linting JavaScript code..."
    -cd frontend && npx eslint static/js/
    @echo "✅ Linting complete!"

# Show server info (IP addresses and URLs)
info:
    @echo "📡 Server Information:"
    @echo ""
    @echo "Local URLs:"
    @echo "  - http://localhost:8000 (Production)"
    @echo "  - http://localhost:3000 (Development)"
    @echo ""
    @echo "Network URLs:"
    @python3 -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); ip = s.getsockname()[0]; s.close(); print(f'  - http://{ip}:8000 (Production)'); print(f'  - http://{ip}:3000 (Development)')"

# Reset queue state
reset-queue:
    @echo "🗑️  Resetting queue..."
    rm -f queue_state.json
    @echo "✅ Queue reset complete!"

# Show logs from queue state file
show-queue:
    @echo "📋 Current queue state:"
    @cat queue_state.json 2>/dev/null || echo "Queue is empty or file doesn't exist"

# Check if required tools are installed
check-deps:
    @echo "🔍 Checking dependencies..."
    @command -v python3 >/dev/null 2>&1 || echo "❌ python3 not found"
    @command -v uv >/dev/null 2>&1 || echo "❌ uv not found (install from https://docs.astral.sh/uv/)"
    @command -v node >/dev/null 2>&1 || echo "❌ node not found"
    @command -v npm >/dev/null 2>&1 || echo "❌ npm not found"
    @echo "✅ Dependency check complete!"

# Update dependencies to latest versions
update:
    @echo "⬆️  Updating backend dependencies..."
    uv lock --upgrade
    @echo "⬆️  Updating frontend dependencies..."
    cd frontend && npm update
    @echo "✅ Dependencies updated!"

# Run backend and frontend in parallel (internal helper)
_parallel +args:
    #!/usr/bin/env bash
    set -euo pipefail

    # Trap to kill background processes on exit
    trap 'kill $(jobs -p) 2>/dev/null' EXIT

    # Start backend
    just backend &

    # Give backend time to start
    sleep 2

    # Start frontend
    just frontend &

    # Wait for both processes
    wait
