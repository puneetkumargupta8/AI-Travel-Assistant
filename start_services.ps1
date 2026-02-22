# PowerShell script to start the containerized services

Write-Host "Starting FastAPI and n8n services..." -ForegroundColor Green
Write-Host "Make sure you have Docker Desktop running!" -ForegroundColor Yellow
Write-Host ""

# Check if Docker is available
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is not installed or not in PATH. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "Building and starting services..." -ForegroundColor Cyan
docker compose up --build