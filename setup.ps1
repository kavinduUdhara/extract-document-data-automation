# Document Data Extractor - PowerShell Setup Script

Write-Host "Document Data Extractor - Setup and Run Script" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Virtual environment created!" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Setup completed!" -ForegroundColor Green
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "Please copy .env.example to .env and fill in your values" -ForegroundColor Yellow
    Write-Host ""
    
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "Created .env file from template. Please edit it with your values." -ForegroundColor Green
    }
    Write-Host ""
}

# Create documents folder if it doesn't exist
if (-not (Test-Path "documents")) {
    New-Item -ItemType Directory -Name "documents" | Out-Null
    Write-Host "Created 'documents' folder for your input files." -ForegroundColor Green
    Write-Host ""
}

Write-Host "To run the extractor:" -ForegroundColor Cyan
Write-Host "1. Edit the .env file with your Google Cloud credentials" -ForegroundColor White
Write-Host "2. Add documents to the 'documents' folder" -ForegroundColor White
Write-Host "3. Run: python document_extractor.py" -ForegroundColor White
Write-Host ""
Write-Host "Or run examples: python examples.py" -ForegroundColor White
Write-Host "Or verify setup: python setup.py --verify" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to continue"
