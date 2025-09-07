

# ChronoStories API Documentation

## Overview

The ChronoStories API provides endpoints for managing autonomous AI-generated news stories, user authentication, and content management. All API responses follow a consistent JSON format.

## Base URL

```
http://localhost:40268/api
```

## Authentication

Most endpoints require authentication via session cookies. Login through the web interface to establish a session.

## Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Response data here
  }
}
```

Error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error information"
}
```

## Endpoints

### Authentication Endpoints

#### POST /auth/login
Login to establish a session.

**Request:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user_id": 1,
    "username": "user@example.com",
    "redirect_url": "/dashboard"
  }
}
```

#### POST /auth/signup
Register a new user account.

**Request:**
```json
{
  "username": "newuser@example.com",
  "email": "newuser@example.com",
  "password": "securepassword123",
  "confirm_password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Account created successfully",
  "data": {
    "user_id": 2,
    "username": "newuser@example.com"
  }
}
```

#### GET /auth/logout
Logout and clear session.

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### Story Management Endpoints

#### GET /api/stories
Retrieve all stories with pagination and filtering.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)
- `category` (optional): Filter by category
- `status` (optional): Filter by status (pending, completed, failed)
- `search` (optional): Search in titles and content

**Response:**
```json
{
  "success": true,
  "message": "Stories retrieved successfully",
  "data": {
    "stories": [
      {
        "id": 1,
        "title": "AI Revolution in Healthcare",
        "content": "Full story content...",
        "category": "technology",
        "status": "completed",
        "image_url": "/static/generated_images/story_1.jpg",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:35:00Z",
        "tags": ["AI", "healthcare", "innovation"],
        "analytics": {
          "views": 150,
          "likes": 12,
          "shares": 5
        }
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 45,
      "pages": 3
    }
  }
}
```

#### GET /api/stories/{story_id}
Retrieve a specific story by ID.

**Response:**
```json
{
  "success": true,
  "message": "Story retrieved successfully",
  "data": {
    "story": {
      "id": 1,
      "title": "AI Revolution in Healthcare",
      "content": "Full story content...",
      "summary": "Brief summary of the story",
      "category": "technology",
      "status": "completed",
      "image_url": "/static/generated_images/story_1.jpg",
      "image_prompt": "Anime style illustration of AI in healthcare",
      "source_url": "https://example-news-source.com/article",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:35:00Z",
      "tags": ["AI", "healthcare", "innovation"],
      "metadata": {
        "word_count": 450,
        "reading_time": 3,
        "sentiment": "positive"
      }
    }
  }
}
```

#### POST /api/generate-story
Generate a new story from a news topic or URL.

**Request:**
```json
{
  "source_url": "https://example-news-source.com/article",
  "category": "technology",
  "custom_prompt": "Focus on the human impact of this technology",
  "image_style": "anime",
  "generate_images": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Story generation started",
  "data": {
    "task_id": "task_20240115_143022_123",
    "status": "pending",
    "estimated_completion": "2024-01-15T14:35:00Z"
  }
}
```

#### DELETE /api/stories/{story_id}
Delete a specific story (requires authentication).

**Response:**
```json
{
  "success": true,
  "message": "Story deleted successfully"
}
```

### Task Status Endpoints

#### GET /api/story-status/{task_id}
Check the status of a story generation task.

**Response:**
```json
{
  "success": true,
  "message": "Task status retrieved successfully",
  "data": {
    "task_id": "task_20240115_143022_123",
    "status": "completed",
    "progress": 100,
    "story_id": 1,
    "created_at": "2024-01-15T14:30:22Z",
    "updated_at": "2024-01-15T14:35:45Z",
    "error_message": null,
    "metadata": {
      "steps_completed": ["scraping", "analysis", "text_generation", "image_generation"],
      "current_step": "completed"
    }
  }
}
```

**Status Values:**
- `pending`: Task is queued
- `processing`: Task is currently being processed
- `completed`: Task completed successfully
- `failed`: Task failed with error

### Trending Topics Endpoints

#### GET /api/trends
Retrieve current trending topics.

**Query Parameters:**
- `limit` (optional): Number of trends to return (default: 10)
- `category` (optional): Filter by category
- `timeframe` (optional): Filter by timeframe (hour, day, week)

**Response:**
```json
{
  "success": true,
  "message": "Trends retrieved successfully",
  "data": {
    "trends": [
      {
        "id": 1,
        "keyword": "AI Healthcare",
        "category": "technology",
        "volume": 8500,
        "growth_rate": 23.5,
        "region": "global",
        "source": "google_trends",
        "discovered_at": "2024-01-15T12:00:00Z"
      }
    ],
    "metadata": {
      "total_trends": 25,
      "last_updated": "2024-01-15T14:30:00Z"
    }
  }
}
```

#### POST /api/trends/analyze
Analyze a trending topic for story potential.

**Request:**
```json
{
  "trend_id": 1,
  "deep_analysis": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Trend analysis completed",
  "data": {
    "analysis": {
      "story_potential": "high",
      "sentiment": "positive",
      "key_entities": ["OpenAI", "Healthcare", "Innovation"],
      "recommended_angle": "Focus on patient benefits",
      "estimated_engagement": "high",
      "competition_analysis": "low competition in this angle"
    }
  }
}
```

### Analytics Endpoints

#### GET /api/analytics/overview
Get overall platform analytics.

**Response:**
```json
{
  "success": true,
  "message": "Analytics retrieved successfully",
  "data": {
    "overview": {
      "total_stories": 156,
      "total_users": 23,
      "total_views": 12450,
      "average_engagement": 0.68,
      "top_category": "technology",
      "growth_rate": 15.3
    },
    "time_series": {
      "views": [
        {"date": "2024-01-14", "views": 850},
        {"date": "2024-01-15", "views": 920}
      ]
    }
  }
}
```

#### GET /api/analytics/stories/{story_id}
Get analytics for a specific story.

**Response:**
```json
{
  "success": true,
  "message": "Story analytics retrieved successfully",
  "data": {
    "analytics": {
      "story_id": 1,
      "views": 450,
      "unique_views": 380,
      "average_time_spent": 45,
      "bounce_rate": 0.23,
      "likes": 25,
      "shares": 8,
      "comments": 3,
      "click_through_rate": 0.15,
      "conversion_rate": 0.08
    }
  }
}
```

### Image Generation Endpoints

#### POST /api/generate-image
Generate an image for a story.

**Request:**
```json
{
  "prompt": "Anime style illustration of AI helping doctors",
  "style": "anime",
  "size": "1024x1024",
  "model": "gemini-2.5-flash-image-preview"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Image generated successfully",
  "data": {
    "image_url": "/static/generated_images/img_20240115_143022.jpg",
    "prompt_used": "Anime style illustration of AI helping doctors",
    "generation_time": 3.5,
    "model": "gemini-2.5-flash-image-preview"
  }
}
```

### System Health Endpoints

#### GET /api/health
Check system health status.

**Response:**
```json
{
  "success": true,
  "message": "System is healthy",
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-15T14:30:00Z",
    "services": {
      "database": "connected",
      "redis": "connected",
      "ai_services": {
        "gemini": "operational",
        "openai": "operational"
      }
    },
    "metrics": {
      "active_tasks": 3,
      "queue_size": 0,
      "response_time": "120ms"
    }
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400  | Bad Request - Invalid parameters |
| 401  | Unauthorized - Authentication required |
| 403  | Forbidden - Insufficient permissions |
| 404  | Not Found - Resource doesn't exist |
| 429  | Too Many Requests - Rate limit exceeded |
| 500  | Internal Server Error |

## Rate Limiting

- **Authentication endpoints**: 5 requests per minute
- **Story generation**: 10 requests per hour per user
- **General API**: 100 requests per hour per IP

## WebSocket Support

Real-time updates for story generation progress:

```javascript
const socket = io('http://localhost:40268');
socket.on('task_update', (data) => {
  console.log('Task update:', data);
});
```

## SDK Examples

### Python
```python
import requests

# Login
session = requests.Session()
login_response = session.post('http://localhost:40268/auth/login', json={
    'username': 'user@example.com',
    'password': 'password123'
})

# Generate story
story_response = session.post('http://localhost:40268/api/generate-story', json={
    'source_url': 'https://example.com/news',
    'category': 'technology'
})

# Check status
task_id = story_response.json()['data']['task_id']
status_response = session.get(f'http://localhost:40268/api/story-status/{task_id}')
```

### JavaScript
```javascript
// Using fetch API
async function generateStory() {
  // Login
  const loginResponse = await fetch('http://localhost:40268/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'user@example.com',
      password: 'password123'
    }),
    credentials: 'include'
  });

  // Generate story
  const storyResponse = await fetch('http://localhost:40268/api/generate-story', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      source_url: 'https://example.com/news',
      category: 'technology'
    }),
    credentials: 'include'
  });

  const storyData = await storyResponse.json();
  console.log('Task ID:', storyData.data.task_id);
}
```

## Testing

Test the API endpoints:

```bash
# Health check
curl http://localhost:40268/api/health

# Get stories (no auth required for GET requests)
curl http://localhost:40268/api/stories

# Check task status
curl http://localhost:40268/api/story-status/task_20240115_143022_123
```

For more examples and testing tools, see the `/tests` directory in the repository.


