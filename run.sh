#!/usr/bin/env bash
#===============================================================================
# Freelancer SDK Demo - Docker Control Script
# Based on esapyi structure
#
# Usage:
#   ./run.sh dev      - Start development server with hot reload
#   ./run.sh prod     - Start production server with gunicorn
#   ./run.sh test     - Run tests
#   ./run.sh db       - Start only the database
#   ./run.sh shell    - Open a shell in the app container
#   ./run.sh logs     - View logs
#   ./run.sh stop     - Stop all containers
#   ./run.sh clean    - Remove all containers and volumes
#===============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        log_warn ".env file not found. Creating from template..."
        if [ -f .env.example ]; then
            cp .env.example .env
            log_info "Created .env from .env.example"
            log_warn "Please edit .env with your Freelancer API credentials"
        else
            log_error "No .env.example found. Please create .env manually"
            exit 1
        fi
    fi
}

# Start development environment
dev() {
    log_info "Starting development environment..."
    check_env
    docker compose up --build
}

# Start production environment
prod() {
    log_info "Starting production environment..."
    check_env
    docker compose --profile production up --build app-prod db
}

# Start only database
db() {
    log_info "Starting database..."
    docker compose up -d db
    log_success "Database started on port 5432"
}

# Run tests
test() {
    log_info "Running tests..."
    docker compose run --rm app python -m pytest tests/ -v
}

# Open shell in app container
shell() {
    log_info "Opening shell in app container..."
    docker compose run --rm app /bin/bash
}

# View logs
logs() {
    docker compose logs -f
}

# Stop all containers
stop() {
    log_info "Stopping all containers..."
    docker compose down
    log_success "All containers stopped"
}

# Clean up everything
clean() {
    log_warn "This will remove all containers, volumes, and images for this project."
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up..."
        docker compose down -v --rmi local
        log_success "Cleanup complete"
    else
        log_info "Cleanup cancelled"
    fi
}

# Show help
help() {
    echo "Freelancer SDK Demo - Docker Control Script"
    echo ""
    echo "Usage: ./run.sh <command>"
    echo ""
    echo "Commands:"
    echo "  dev      Start development server with hot reload"
    echo "  prod     Start production server with gunicorn"
    echo "  test     Run tests"
    echo "  db       Start only the database"
    echo "  shell    Open a shell in the app container"
    echo "  logs     View container logs"
    echo "  stop     Stop all containers"
    echo "  clean    Remove all containers and volumes"
    echo "  help     Show this help message"
    echo ""
    echo "Environment:"
    echo "  Copy .env.example to .env and fill in your Freelancer API credentials"
}

# Main command handler
case "${1}" in
    "dev")
        dev
        ;;
    "prod")
        prod
        ;;
    "test")
        test
        ;;
    "db")
        db
        ;;
    "shell")
        shell
        ;;
    "logs")
        logs
        ;;
    "stop")
        stop
        ;;
    "clean")
        clean
        ;;
    "help"|"--help"|"-h"|"")
        help
        ;;
    *)
        log_error "Unknown command: ${1}"
        help
        exit 1
        ;;
esac
