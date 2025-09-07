#!/usr/bin/env python3
"""
ChronoStories: The Autonomous AI News Story Engine
Main application entry point
"""

from app import create_app
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 40268))
    
    # Run the application
    logger.info(f"Starting ChronoStories on port {port}")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development',
        threaded=True
    )
