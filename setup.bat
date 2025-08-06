@echo off
echo Document Data Extractor - Setup and Run Script
echo ===============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found!
echo.

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup completed!
echo.

:: Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and fill in your values
    echo.
    if exist ".env.example" (
        copy .env.example .env
        echo Created .env file from template. Please edit it with your values.
    )
    echo.
)

:: Create documents folder if it doesn't exist
if not exist "documents" (
    mkdir documents
    echo Created 'documents' folder for your input files.
    echo.
)

echo To run the extractor:
echo 1. Edit the .env file with your Google Cloud credentials
echo 2. Add documents to the 'documents' folder
echo 3. Run: python document_extractor.py
echo.
echo Or run examples: python examples.py
echo Or verify setup: python setup.py --verify
echo.

pause
