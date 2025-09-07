
@echo off
echo ChronoStories Installation Script for Windows
echo ============================================
echo.

REM Check if Python is installed
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Check Python version
py -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.8 or higher is required
    pause
    exit /b 1
)

echo ✅ Python version check passed

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    py -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo ✅ Virtual environment created

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated

REM Upgrade pip
echo Upgrading pip...
py -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing anyway...
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install
if errorlevel 1 (
    echo WARNING: Failed to install Playwright browsers
    echo You may need to install them manually later
)

echo ✅ Playwright browsers installed

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo ✅ .env file created from .env.example
    echo ⚠️  Please edit .env file with your actual API keys
) else (
    echo ✅ .env file already exists
)

REM Create necessary directories
echo Creating directories...
if not exist "logs" mkdir logs
if not exist "instance" mkdir instance
if not exist "app\static\uploads" mkdir app\static\uploads
if not exist "app\static\generated_images" mkdir app\static\generated_images

echo ✅ Directories created

REM Initialize database
echo Initializing database...
py -c "from app import create_app, db; app = create_app(); with app.app_context(): db.create_all(); print('Database initialized successfully!')"
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    echo You may need to initialize it manually
    pause
    exit /b 1
)

echo ✅ Database initialized

echo.
echo ============================================
echo 🎉 Installation completed successfully!
echo.
echo Next steps:
echo 1. Edit the .env file with your actual API keys
echo 2. Activate the virtual environment: venv\Scripts\activate
echo 3. Start the application: py app.py
echo 4. Open your browser to: http://localhost:40268
echo.
echo For more information, see the README.md file
echo.
echo Press any key to exit...
pause >nul

