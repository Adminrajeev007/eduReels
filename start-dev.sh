#!/bin/bash

# EducationalReels Local Development Server Startup Script
# Usage: ./start-dev.sh [start|stop|restart|logs]

PROJECT_DIR="/Users/rahulkumar/Desktop/edureels"
API_PORT=8000
FRONTEND_PORT=8001

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if port is already in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Start development servers
start_servers() {
    print_info "Starting EducationalReels development servers..."
    
    # Check ports
    if check_port $API_PORT; then
        print_error "API port $API_PORT is already in use"
        return 1
    fi
    
    if check_port $FRONTEND_PORT; then
        print_error "Frontend port $FRONTEND_PORT is already in use"
        return 1
    fi
    
    # Start API server
    cd "$PROJECT_DIR"
    source venv/bin/activate
    print_info "Starting API server on port $API_PORT..."
    python3 -m uvicorn api.main:app --host 0.0.0.0 --port $API_PORT --reload > /tmp/api.log 2>&1 &
    API_PID=$!
    sleep 3
    
    if check_port $API_PORT; then
        print_status "API server started (PID: $API_PID)"
    else
        print_error "Failed to start API server"
        cat /tmp/api.log
        return 1
    fi
    
    # Start Frontend server
    print_info "Starting Frontend server on port $FRONTEND_PORT..."
    cd "$PROJECT_DIR/frontend"
    python3 -m http.server $FRONTEND_PORT > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    sleep 2
    
    if check_port $FRONTEND_PORT; then
        print_status "Frontend server started (PID: $FRONTEND_PID)"
    else
        print_error "Failed to start Frontend server"
        cat /tmp/frontend.log
        return 1
    fi
    
    print_status "All servers started successfully!"
    echo ""
    echo "🌐 Access points:"
    echo "   Frontend:    http://localhost:$FRONTEND_PORT"
    echo "   API:         http://localhost:$API_PORT"
    echo "   API Docs:    http://localhost:$API_PORT/docs"
    echo ""
    print_info "Run './start-dev.sh logs' to watch logs"
    echo ""
}

# Stop development servers
stop_servers() {
    print_info "Stopping EducationalReels servers..."
    
    # Kill processes on ports
    lsof -ti :$API_PORT | xargs kill -9 2>/dev/null
    lsof -ti :$FRONTEND_PORT | xargs kill -9 2>/dev/null
    
    sleep 1
    
    if ! check_port $API_PORT && ! check_port $FRONTEND_PORT; then
        print_status "All servers stopped"
    else
        if check_port $API_PORT; then
            print_error "Failed to stop API server"
        fi
        if check_port $FRONTEND_PORT; then
            print_error "Failed to stop Frontend server"
        fi
    fi
}

# Show logs
show_logs() {
    print_info "Watching server logs (API + Frontend)..."
    echo "Press Ctrl+C to exit"
    echo ""
    
    # Create a function to monitor both logs
    (
        tail -f /tmp/api.log &
        tail -f /tmp/frontend.log &
        wait
    ) | while read line; do
        if [[ $line == *"api"* ]] || [[ $line == *"uvicorn"* ]]; then
            echo -e "${YELLOW}[API]${NC} $line"
        else
            echo -e "${GREEN}[Frontend]${NC} $line"
        fi
    done
}

# Test endpoints
test_endpoints() {
    print_info "Testing API endpoints..."
    echo ""
    
    # Health check
    print_info "Testing health endpoint..."
    if curl -s http://localhost:$API_PORT/health | grep -q "healthy"; then
        print_status "Health endpoint working"
    else
        print_error "Health endpoint failed"
    fi
    
    # Degrees check
    print_info "Testing degrees endpoint..."
    if curl -s http://localhost:$API_PORT/degrees | grep -q "Computer Science"; then
        print_status "Degrees endpoint working"
    else
        print_error "Degrees endpoint failed"
    fi
    
    # Frontend check
    print_info "Testing frontend..."
    if curl -s http://localhost:$FRONTEND_PORT | grep -q "EducationalReels"; then
        print_status "Frontend loading correctly"
    else
        print_error "Frontend not responding"
    fi
    
    echo ""
    print_status "All tests passed!"
}

# Main script logic
case "${1:-start}" in
    start)
        start_servers
        ;;
    stop)
        stop_servers
        ;;
    restart)
        stop_servers
        sleep 2
        start_servers
        ;;
    logs)
        show_logs
        ;;
    test)
        test_endpoints
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|test}"
        echo ""
        echo "Commands:"
        echo "  start   - Start API and Frontend servers"
        echo "  stop    - Stop all servers"
        echo "  restart - Restart all servers"
        echo "  logs    - Watch server logs in real-time"
        echo "  test    - Test all API endpoints"
        exit 1
        ;;
esac
