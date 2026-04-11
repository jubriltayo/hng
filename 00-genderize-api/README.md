# Name Gender Classification API

A Django-based REST API that integrates with the Genderize.io API to predict gender from names with confidence scoring.

## 📋 Features

- **Gender Prediction** - Uses Genderize.io database of name-gender associations
- **Confidence Scoring** - Calculates confidence based on probability and sample size
- **CORS Enabled** - Accessible from any frontend domain
- **Production Ready** - Proper error handling, timeouts, and status codes

## 🛠️ Tech Stack

- **Framework**: Django 6.0+
- **HTTP Client**: Requests
- **CORS**: django-cors-headers
- **Package Manager**: uv
- **Linter**: Ruff
- **Server**: Gunicorn (production) / Django runserver (development)

## 📦 Installation

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager

### Setup

```bash
# Clone repository
git clone https://github.com/jubriltayo/hng.git
cd 00-genderize-api

# Install dependencies with uv
uv sync

# Activate virtual environment (uv creates it automatically)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### Development Dependencies

```bash
# Install dev tools (ruff for linting)
uv sync --group dev

# Run linter
ruff check .
```

## 🔌 API Documentation

### Endpoint

```
GET /api/classify?name={name}
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | Yes | First name to classify |

### Success Response (200 OK)

```json
{
  "status": "success",
  "data": {
    "name": "jubril",
    "gender": "male",
    "probability": 0.94,
    "sample_size": 1824,
    "is_confident": true,
    "processed_at": "2026-04-11T00:24:59Z"
  }
}
```

### Error Responses

| Status Code | Scenario | Response |
|-------------|----------|----------|
| 400 | Missing or empty name | `{"status": "error", "message": "Missing or empty name parameter"}` |
| 404 | No prediction available | `{"status": "error", "message": "No prediction available for the provided name"}` |
| 502 | Genderize API failure | `{"status": "error", "message": "Upstream or server failure"}` |

### Confidence Logic

`is_confident = true` ONLY when:
- `probability >= 0.7` AND
- `sample_size >= 100`

Both conditions must be met. If either fails, `is_confident = false`.

## 🧪 Testing

### Local Test

```bash
# Valid name
curl "http://localhost:8000/api/classify?name=john"

# Unknown name
curl "http://localhost:8000/api/classify?name=xkcd"

# Missing parameter
curl "http://localhost:8000/api/classify"
```

### Example Responses

**Known name with high confidence:**
```json
{
  "status": "success",
  "data": {
    "name": "john",
    "gender": "male",
    "probability": 1.0,
    "sample_size": 2692560,
    "is_confident": true,
    "processed_at": "2026-04-11T00:27:50Z"
  }
}
```

**Known name with low confidence:**
```json
{
  "status": "success",
  "data": {
    "name": "bernie",
    "gender": "male",
    "probability": 0.56,
    "sample_size": 14269,
    "is_confident": false,
    "processed_at": "2026-04-11T00:24:07Z"
  }
}
```

## 🏗️ Architecture

```
Request → URL Router → View → Service Layer → Genderize API
                ↓         ↓              ↓
              CORS    Validation    External Call
                        ↓
                  Business Logic
                   (confidence,
                    timestamp)
                        ↓
                  JSON Response
```

### Key Components

| Component | Responsibility |
|-----------|---------------|
| `views.py` | Request validation, response formatting, error handling |
| `services/genderize_client.py` | External API communication with timeout |
| `middleware` | CORS headers (via django-cors-headers) |

## 🚢 Deployment

### Railway (Recommended)

Deploy directly from your GitHub repository:
1. Create account at [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Django and deploys automatically

### Environment Variables (if needed)

```env
# Optional - Genderize API is public
GENDERIZE_API_URL=https://api.genderize.io
REQUEST_TIMEOUT=5
```

## 📁 Project Structure

```
00-genderize-api/
├── api/
│   ├── __init__.py
│   ├── views.py              # Endpoint logic
│   ├── urls.py               # URL routing
│   ├── services/
│   │   ├── __init__.py
│   │   └── genderize_client.py  # API client
│   └── migrations/           # Database migrations (none needed)
├── config/
│   ├── settings.py           # Django config + CORS
│   ├── urls.py               # Main URL config
│   └── wsgi.py              # Production entry point
├── pyproject.toml            # uv project configuration
├── uv.lock                   # Locked dependencies (auto-generated)
├── manage.py
└── README.md
```

## 🔧 Configuration

### CORS Settings (settings.py)

```python
INSTALLED_APPS = [
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be near top
    'django.middleware.common.CommonMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True  # Allow all domains (for grading)
```

### Timeout Configuration

```python
# api/services/genderize_client.py
TIMEOUT = 5  # seconds - prevents hanging requests
```

## ⚡ Performance

- **Response Time**: <500ms (excluding external API latency)
- **Concurrent Requests**: Handles multiple requests without blocking
- **Timeout Protection**: 5-second limit on external API calls

## 🐛 Error Handling Matrix

| Scenario | HTTP Status | User Message |
|----------|-------------|--------------|
| No name parameter | 400 | Missing or empty name parameter |
| Empty name string | 400 | Missing or empty name parameter |
| Genderize API down | 502 | Upstream or server failure |
| Genderize timeout | 502 | Upstream or server failure |
| gender = null | 404 | No prediction available |
| count = 0 | 404 | No prediction available |

## 📝 Development Notes

### Testing Strategy

```bash
# Manual test with curl
curl -I http://localhost:8000/api/classify?name=test  # Check CORS
```