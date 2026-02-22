#!/bin/bash
# Script to start the containerized services

echo "Starting FastAPI and n8n services..."
echo "Make sure you have Docker Desktop running!"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed or not in PATH. Please install Docker Desktop."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker compose &> /dev/null; then
    echo "Docker Compose is not available. Please ensure Docker Desktop includes the Compose plugin."
    exit 1
fi

echo "Building and starting services..."
docker compose up --build