

#!/bin/bash

# ChronoStories Installation Script for Unix/Linux/macOS
# ============================================

set -e  # Exit on any error

echo "ChronoStories Installation Script"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed or not in PATH${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check Python version
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo -e "${RED}ERROR: Python 3.8 or higher is required${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python version check passed${NC}"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}WARNING: pip3 not found, trying to install...${NC}"
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y python3-pip
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3-pip
    elif command -v brew &> /dev/null; then
        brew install python3
    else
        echo -e "${RED}ERROR: Could not install pip. Please install manually.${NC}"
        exit 1
    fi
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to create virtual environment${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Virtual environment created${NC}"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to activate virtual environment${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}WARNING: Failed to upgrade pip, continuing anyway...${NC}"
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to install dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}WARNING: Failed to install Playwright browsers${NC}"
    echo "You may need to install them manually later"
fi

echo -e "${GREEN}✅ Playwright browsers installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created from .env.example${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env file with your actual API keys${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p logs instance app/static/uploads app/static/generated_images

echo -e "${GREEN}✅ Directories created${NC}"

# Initialize database
echo "Initializing database..."
python3 -c "from app import create_app, db; app = create_app(); with app.app_context(): db.create_all(); print('Database initialized successfully!')"
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to initialize database${NC}"
    echo "You may need to initialize it manually"
    exit 1
fi

echo -e "${GREEN}✅ Database initialized${NC}"

echo ""
echo "================================="
echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your actual API keys"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Start the application: python app.py"
echo "4. Open your browser to: http://localhost:40268"
echo ""
echo "For more information, see the README.md file"


