# ChronoStories: The Autonomous AI News Story Engine

An autonomous, self-perpetuating web platform that ingests real-time global news and trending topics, and uses a suite of AI models to automatically transform them into visually compelling, anime-style web stories.

## 🌟 Features

- **Dual-Pronged Content Ingestion**: Reactive news stream (GNews API) + Proactive trend scraping (Google Trends, Twitter/X, Reddit)
- **AI Brain**: Central intelligence that manages content generation, scraping, and performance analysis
- **Advanced Image Generation**: Uses `gemini-2.5-flash-image-preview` for anime-style story visuals
- **Web Stories Format**: Mobile-first, tappable stories like Instagram/Google Web Stories
- **Complete Authentication System**: User registration, login, profile management
- **Real-time Task Status**: Track story generation progress with task status endpoints

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Virtual environment (recommended)

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/Ashutoshchoudhary3/AniStory.git
cd AniStory
```

2. **Create and activate virtual environment**
```bash
# On Windows
py -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the root directory:
```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///chronostories.db

# API Keys (Required)
GEMINI_API_KEY=your-gemini-api-key-here
GNEWS_API_KEY=your-gnews-api-key-here

# Optional API Keys
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Server Configuration
SERVER_NAME=localhost:40268
```

5. **Initialize the database**
```bash
# On Windows
py -c "from app import create_app, db; app = create_app(); with app.app_context(): db.create_all(); print('Database initialized!')"

# On macOS/Linux
python3 -c "from app import create_app, db; app = create_app(); with app.app_context(): db.create_all(); print('Database initialized!')"
```

6. **Start the application**
```bash
# On Windows
py app.py

# On macOS/Linux
python3 app.py
```

7. **Access the application**
Open your browser and go to: `http://localhost:40268`

## 📋 API Documentation

### Authentication Endpoints
- `GET /auth/login` - Login page
- `POST /auth/login` - Authenticate user
- `GET /auth/signup` - Registration page
- `POST /auth/signup` - Create new user
- `GET /auth/logout` - Logout user
- `GET /auth/profile` - User profile page

### Story Endpoints
- `GET /api/stories` - List all stories
- `GET /api/story-status/<task_id>` - Get story generation status
- `POST /api/generate-story` - Generate new story (requires authentication)

### Main Pages
- `GET /` - Homepage
- `GET /dashboard` - User dashboard (requires authentication)

## 🔧 Configuration

### Required API Keys

1. **Gemini API Key** (for image generation)
   - Get it from: https://makersuite.google.com/app/apikey
   - Required for anime-style image generation

2. **GNews API Key** (for news ingestion)
   - Get it from: https://gnews.io/
   - Required for real-time news fetching

### Optional API Keys

3. **OpenAI API Key** (for text generation)
   - Get it from: https://platform.openai.com/api-keys
   - Alternative text generation provider

4. **Anthropic API Key** (for Claude)
   - Get it from: https://console.anthropic.com/
   - Alternative AI provider

## 🗄️ Database Schema

The application uses SQLite with the following main tables:
- `users` - User accounts and profiles
- `stories` - Generated stories with metadata
- `trends` - Trending topics and keywords
- `analytics` - User engagement and performance metrics
- `news_sources` - News source configurations
- `image_generation_logs` - Image generation history
- `scraping_logs` - Web scraping activity logs

## 🐛 Troubleshooting

### Common Issues

1. **"Task not found" error on story-status endpoint**
   - Ensure the task ID exists in the database
   - Check that the Flask app is running on the correct port (40268)
   - Verify database initialization

2. **Flask app won't start**
   - Check that all dependencies are installed: `pip install -r requirements.txt`
   - Verify Python version is 3.8+
   - Check for missing environment variables

3. **Database errors**
   - Reinitialize the database: `python -c "from app import create_app, db; app = create_app(); with app.app_context(): db.create_all()"`
   - Check database file permissions

4. **API endpoint 404 errors**
   - Verify SERVER_NAME in config.py matches your actual port (40268)
   - Check that all blueprints are properly registered
   - Ensure Flask app factory pattern is working correctly

5. **Image generation fails**
   - Verify Gemini API key is valid and has proper permissions
   - Check API rate limits
   - Review image generation logs in the database

### Debug Mode

To run in debug mode with detailed logging:
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

## 📁 Project Structure

```
AniStory/
├── app/                    # Flask application package
│   ├── __init__.py        # App factory and configuration
│   ├── models.py          # SQLAlchemy models
│   ├── routes.py          # Flask routes and endpoints
│   ├── static/            # CSS, JavaScript, images
│   └── templates/         # HTML templates
├── ai_brain/              # AI Brain module
│   ├── ai_brain.py        # Main AI Brain logic
│   └── ai_core.py         # Core AI functionality
├── config.py              # Configuration settings
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
└── instance/              # Instance-specific files
    └── chronostories.db   # SQLite database
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section above

## 🎯 Next Steps

After successful installation:
1. Configure your API keys in the `.env` file
2. Test the story generation with a sample news topic
3. Customize the anime style prompts for your brand
4. Set up automated scraping schedules
5. Monitor analytics to optimize content performance

---

**Happy storytelling with ChronoStories!** 🎨📰✨
