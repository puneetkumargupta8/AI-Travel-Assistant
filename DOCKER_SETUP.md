# Docker Containerization Guide

## Overview
This document explains how to containerize your FastAPI backend and n8n service using Docker and docker-compose.

## Architecture Changes

### Before (Local Setup)
```
Streamlit (local) → FastAPI backend (local) → n8n (Docker) → SMTP Email
```

### After (Containerized Setup)
```
Streamlit (local) → FastAPI (container) → n8n (container) → SMTP Email
```

## Containerized Services

### 1. FastAPI Backend Service
- **Base Image**: Python 3.11-slim
- **Features**:
  - Installs dependencies from requirements.txt
  - Runs as non-root user for security
  - Exposes port 8000
  - Built from local Dockerfile

### 2. n8n Service
- **Image**: n8nio/n8n official image
- **Features**:
  - Exposes port 5678
  - Persists data via volume mapping
  - Sets secure cookie to false for local development
  - Automatic restart unless stopped

## Docker Networking

### Internal Docker Network
- Both services run on the same Docker network: `travel-network`
- FastAPI calls n8n using internal hostname: `http://n8n:5678/webhook/itinerary-export`
- This allows services to communicate internally without exposing ports unnecessarily

### Why We Changed the Webhook URL
- **Before**: `http://localhost:5678/webhook/itinerary-export`
- **After**: `http://n8n:5678/webhook/itinerary-export`

When services run in separate containers, `localhost` refers to the individual container's own network space. Using the service name `n8n` as the hostname allows Docker's internal DNS to route requests between containers on the same network.

## Files Created

### Dockerfile
- Python 3.11 base image
- Installs requirements.txt dependencies
- Copies app code
- Runs as non-root user
- Exposes port 8000
- Uses uvicorn to run the application

### docker-compose.yml
- Defines fastapi and n8n services
- Sets up shared Docker network
- Maps necessary ports
- Configures environment variables and volumes
- Sets restart policies

### Updated .env.example
- Updated webhook URL to use Docker service name
- Maintains all other environment variables

## Volume Persistence

The n8n service uses volume mapping to persist data:
```
./n8n_data:/home/node/.n8n
```
This ensures your n8n workflows and configurations are preserved between container restarts.

## Getting Started

### Prerequisites
- Docker Desktop installed and running
- Docker Compose plugin enabled

### Setup Instructions

1. **Prepare Environment Variables**
   ```bash
   cp .env.example .env
   ```
   
2. **Edit .env file with your actual values**
   ```bash
   # Edit the .env file to include your actual API keys
   # Make sure GEMINI_API_KEY and SMTP settings are configured
   ```

3. **Start Services**
   ```bash
   docker compose up --build
   ```

4. **Access Services**
   - FastAPI API: http://localhost:8000
   - FastAPI Health: http://localhost:8000/health
   - n8n Interface: http://localhost:5678

5. **Stopping Services**
   ```bash
   # Press Ctrl+C to stop services gracefully
   # Or run from another terminal:
   docker compose down
   ```

## Testing the Setup

### 1. Verify FastAPI is Running
```bash
curl http://localhost:8000/health
```

### 2. Verify n8n is Running
Open http://localhost:5678 in your browser

### 3. Test the Integration
- Start your Streamlit frontend locally
- Use the Streamlit interface to trigger the export itinerary flow
- The FastAPI backend should call the n8n webhook successfully
- n8n should send the email via SMTP

## Environment Variables Handling

### In Docker
- `.env` file is loaded by docker-compose but not copied into the container
- This keeps sensitive data secure
- The container gets environment variables at runtime from the host

### Security Considerations
- Never commit `.env` file to version control
- The Dockerfile does not copy the `.env` file into the image
- Environment variables are loaded at container runtime via docker-compose

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```
   ERROR: for fastapi  Cannot start service fastapi: driver failed programming external connectivity
   ```
   - Make sure local instances of FastAPI or n8n are stopped
   - Check with `netstat -an | findstr :8000` or `:5678`

2. **Permission Issues with n8n Volume**
   ```
   Permission denied when accessing /home/node/.n8n
   ```
   - Ensure the ./n8n_data directory exists and has proper permissions
   - On Windows, you might need to adjust file permissions

3. **Connection Issues Between Containers**
   - Verify both services are on the same network
   - Check that the webhook URL uses the service name `n8n`

### Useful Commands

```bash
# View logs
docker compose logs fastapi
docker compose logs n8n

# View running containers
docker compose ps

# Execute commands in running container
docker compose exec fastapi bash
docker compose exec n8n bash

# Rebuild and restart
docker compose up --build --force-recreate
```

## Production Considerations

For production deployment, consider:
- Using HTTPS with reverse proxy (nginx/Traefik)
- Adding a database service
- Implementing proper secrets management
- Setting up monitoring and logging
- Configuring health checks
- Using tagged versions instead of latest