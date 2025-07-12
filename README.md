# 🎤 AI Voice Assistant Backend

A Django REST API backend for a voice-based AI assistant that can handle voice commands, process them through AI services, and maintain session transcripts.

## 🚀 Features

- **Session Management**: Start and end demo sessions
- **Voice Command Processing**: Handle voice commands with AI integration
- **Transcript Generation**: Full session history with timestamps
- **Admin Interface**: Comprehensive admin panel for session monitoring
- **Security**: Environment-based configuration and proper validation
- **Logging**: Detailed logging for debugging and monitoring

## 🛠️ Tech Stack

- **Django 5.2.4**: Web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Database
- **OpenAI API**: AI command processing
- **Python 3.11+**: Runtime

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL
- OpenAI API key

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd project
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_NAME=project_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# OpenAI Settings
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb project_db

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 4. Run the Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/backend/`

## 📚 API Documentation

### Endpoints

#### 1. Start Session
```http
POST /api/backend/start-session/
```

**Response:**
```json
{
  "message": "Session started successfully",
  "data": {
    "session_id": "uuid-here",
    "started_at": "2024-01-01T12:00:00Z",
    "ended_at": null,
    "is_active": true
  }
}
```

#### 2. Send Command
```http
POST /api/backend/send-command/
```

**Request Body:**
```json
{
  "session_id": "uuid-here",
  "command": "hello"
}
```

**Response:**
```json
{
  "response": "Hello! How can I assist you today?"
}
```

#### 3. Get Transcript
```http
GET /api/backend/transcript/{session_id}/
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "started_at": "2024-01-01T12:00:00Z",
  "ended_at": null,
  "is_active": true,
  "total_commands": 2,
  "commands": [
    {
      "timestamp": "2024-01-01T12:00:00Z",
      "command": "hello",
      "response": "Hello! How can I assist you today?",
      "is_ai_response": false,
      "processing_time_ms": 50
    }
  ]
}
```

#### 4. End Session
```http
POST /api/backend/end-session/{session_id}/
```

**Response:**
```json
{
  "message": "Session ended successfully"
}
```

## 🎯 Command Types

### Dummy Commands
- `hello` - Greeting response
- `time` - Current time
- `help` - Available commands

### AI Commands
- `ai: your question here` - Processed through OpenAI GPT

## 🔧 Development

### Running Tests
```bash
python manage.py test backend
```

### Code Quality
The project follows Django best practices:
- Service layer separation
- Comprehensive error handling
- Input validation
- Proper logging
- Security best practices

### Admin Interface
Access the admin interface at `http://localhost:8000/admin/` to:
- View all sessions
- Monitor command logs
- Track AI vs dummy responses
- View processing times

## 🏗️ Architecture

```
backend/
├── models.py          # Database models
├── services.py        # Business logic layer
├── views.py          # API endpoints
├── serializers.py    # Data validation
├── admin.py          # Admin interface
├── tests.py          # Test suite
└── urls.py           # URL routing
```

## 🔒 Security Features

- Environment-based configuration
- Input validation and sanitization
- Proper error handling
- Session state management
- Comprehensive logging

## 📝 License

This project is part of a hackathon submission.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Happy Hacking! 🚀** 