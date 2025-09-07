
#!/usr/bin/env python3
"""
ChronoStories Setup Script
Automated setup for the ChronoStories AI News Story Engine
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} is compatible")

def create_virtual_environment():
    """Create and activate virtual environment"""
    if not os.path.exists("venv"):
        print("\n🔄 Creating virtual environment...")
        result = run_command(f"{sys.executable} -m venv venv", "Creating virtual environment")
        if result is None:
            return False
    return True

def install_dependencies():
    """Install Python dependencies"""
    pip_executable = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip"
    
    print("\n🔄 Upgrading pip...")
    run_command(f"{pip_executable} install --upgrade pip", "Upgrading pip")
    
    print("\n🔄 Installing dependencies...")
    result = run_command(f"{pip_executable} install -r requirements.txt", "Installing dependencies")
    return result is not None

def setup_environment_file():
    """Create .env file from .env.example if it doesn't exist"""
    if not os.path.exists(".env"):
        print("\n🔄 Setting up environment file...")
        shutil.copy(".env.example", ".env")
        print("✅ Created .env file from .env.example")
        print("⚠️  Please edit .env file with your actual API keys before running the application")
        return True
    else:
        print("\n✅ .env file already exists")
        return True

def install_playwright_browsers():
    """Install Playwright browsers for web scraping"""
    print("\n🔄 Installing Playwright browsers...")
    playwright_executable = "venv/bin/playwright" if os.name != 'nt' else "venv\\Scripts\\playwright"
    result = run_command(f"{playwright_executable} install", "Installing Playwright browsers")
    return result is not None

def initialize_database():
    """Initialize the database"""
    print("\n🔄 Initializing database...")
    python_executable = "venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python.exe"
    
    # Create a simple script to initialize the database
    init_script = """
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print("Database initialized successfully!")
"""
    
    with open("init_db.py", "w") as f:
        f.write(init_script)
    
    result = run_command(f"{python_executable} init_db.py", "Initializing database")
    
    # Clean up
    if os.path.exists("init_db.py"):
        os.remove("init_db.py")
    
    return result is not None

def create_directories():
    """Create necessary directories"""
    print("\n🔄 Creating directories...")
    directories = [
        "logs",
        "instance",
        "app/static/uploads",
        "app/static/generated_images"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directories created")

def main():
    """Main setup function"""
    print("🚀 ChronoStories Setup Script")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Install Playwright browsers
    if not install_playwright_browsers():
        print("❌ Failed to install Playwright browsers")
        sys.exit(1)
    
    # Setup environment file
    if not setup_environment_file():
        print("❌ Failed to setup environment file")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit the .env file with your actual API keys")
    print("2. Activate the virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. Start the application:")
    if os.name == 'nt':
        print("   py app.py")
    else:
        print("   python app.py")
    print("4. Open your browser to: http://localhost:40268")
    print("\nFor more information, see the README.md file")

if __name__ == "__main__":
    main()
