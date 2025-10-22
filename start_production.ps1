# Quick Start Script for Production Version
# Run this to start the Smart Knowledge Repository

Write-Host ""
Write-Host "🧠 Smart Knowledge Repository - Production v2.0" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "⚠️  No virtual environment found" -ForegroundColor Yellow
    Write-Host "   Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Check if .env exists
if (Test-Path ".env") {
    Write-Host "✅ Environment variables configured" -ForegroundColor Green
} else {
    Write-Host "⚠️  No .env file found" -ForegroundColor Yellow
    Write-Host "   Please create .env with your OPENAI_API_KEY" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📊 Current Status:" -ForegroundColor Yellow

# Get profile count using Python
$profileCount = python -c "from src.services.knowledge_service import KnowledgeService; ks = KnowledgeService(); print(ks.get_profile_count())" 2>$null

if ($profileCount) {
    Write-Host "   Profiles: $profileCount" -ForegroundColor Green
} else {
    Write-Host "   Profiles: 0 (database empty - scrape a website first)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Starting Production Application..." -ForegroundColor Cyan
Write-Host ""

# Stop any existing streamlit processes
Stop-Process -Name "streamlit" -Force -ErrorAction SilentlyContinue

# Start the application
streamlit run main.py --server.port 8501
