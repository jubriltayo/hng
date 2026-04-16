# Profile Management API

A Django-based REST API that integrates with Genderize, Agify, and Nationalize APIs to create enriched user profiles with gender, age, and nationality predictions.

## 📋 Features

- **Multi-API Integration** - Combines data from three external APIs (Genderize, Agify, Nationalize)
- **Smart Classification** - Automatically classifies age groups (child, teenager, adult, senior)
- **Idempotent Creation** - Duplicate name requests return existing profile instead of creating new ones
- **Flexible Filtering** - Filter profiles by gender, country, or age group (case-insensitive)
- **CORS Enabled** - Accessible from any frontend domain
- **Production Ready** - Proper error handling, timeouts, and status codes

## 🛠️ Tech Stack

- **Framework**: Django 6.0+
- **Database**: PostgreSQL (development and production)
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
cd 01-profile-api

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

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/profiles` | Create a new profile (idempotent) |
| GET | `/api/profiles` | List all profiles with optional filters |
| GET | `/api/profiles/{id}` | Retrieve a specific profile |
| DELETE | `/api/profiles/{id}` | Delete a specific profile |

### 1. Create Profile

**POST** `/api/profiles`

**Request Body:**
```json
{
  "name": "john"
}
```

**Success Response (201 Created):**
```json
{
  "status": "success",
  "data": {
    "id": "667bb51e-972c-4dc8-ba92-48351aba1abe",
    "name": "john",
    "gender": "male",
    "gender_probability": 1.0,
    "sample_size": 2692560,
    "age": 75,
    "age_group": "senior",
    "country_id": "NG",
    "country_probability": 0.08,
    "created_at": "2026-04-16T18:39:19Z"
  }
}
```

**Duplicate Name Response (200 OK):**
```json
{
  "status": "success",
  "message": "Profile already exists",
  "data": {
    "id": "667bb51e-972c-4dc8-ba92-48351aba1abe",
    "name": "john",
    "gender": "male",
    "gender_probability": 1.0,
    "sample_size": 2692560,
    "age": 75,
    "age_group": "senior",
    "country_id": "NG",
    "country_probability": 0.08,
    "created_at": "2026-04-16T18:39:19Z"
  }
}
```

### 2. Get All Profiles

**GET** `/api/profiles?gender=male&country_id=NG&age_group=adult`

**Query Parameters (all optional, case-insensitive):**

| Parameter | Values |
|-----------|--------|
| gender | male, female |
| country_id | NG, US, DRC, etc. |
| age_group | child, teenager, adult, senior |

**Success Response (200 OK):**
```json
{
  "status": "success",
  "count": 2,
  "data": [
    {
      "id": "5636d013-7784-4ff8-b644-ba0f5a4dd0a5",
      "name": "tayo",
      "gender": "male",
      "age": 54,
      "age_group": "adult",
      "country_id": "NG"
    },
    {
      "id": "0f54c6c8-feec-40e3-9f93-46d695b0864f",
      "name": "jubril",
      "gender": "male",
      "age": 48,
      "age_group": "adult",
      "country_id": "NG"
    }
  ]
}
```

### 3. Get Single Profile

**GET** `/api/profiles/{id}`

**Success Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "667bb51e-972c-4dc8-ba92-48351aba1abe",
    "name": "john",
    "gender": "male",
    "gender_probability": 1.0,
    "sample_size": 2692560,
    "age": 75,
    "age_group": "senior",
    "country_id": "NG",
    "country_probability": 0.08,
    "created_at": "2026-04-16T18:39:19Z"
  }
}
```

### 4. Delete Profile

**DELETE** `/api/profiles/{id}`

**Success Response:** `204 No Content`

## Error Responses

| Status Code | Scenario | Response |
|-------------|----------|----------|
| 400 | Missing or empty name | `{"status": "error", "message": "Missing or empty name"}` |
| 422 | Invalid type (name not a string) | `{"status": "error", "message": "Invalid type"}` |
| 404 | Profile not found | `{"status": "error", "message": "Profile not found"}` |
| 502 | Genderize/Agify/Nationalize API failure | `{"status": "error", "message": "{API} returned an invalid response"}` |

## Age Group Classification

| Age Range | Age Group |
|-----------|-----------|
| 0–12 | child |
| 13–19 | teenager |
| 20–59 | adult |
| 60+ | senior |

## Nationality Logic

- Fetches top 5 countries with probabilities from Nationalize API
- Selects the country with the highest probability
- Returns country_id and country_probability

## Idempotency

- Creating a profile with a name that already exists returns the existing profile
- No duplicate records are created
- Case-insensitive name matching

## 🧪 Testing

### Local Test

```bash
# Create profile
curl -X POST http://localhost:8000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{"name": "john"}'

# Duplicate name (returns existing)
curl -X POST http://localhost:8000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{"name": "john"}'

# Get all profiles
curl "http://localhost:8000/api/profiles"

# Filter profiles
curl "http://localhost:8000/api/profiles?gender=male&country_id=NG&age_group=adult"

# Get single profile
curl "http://localhost:8000/api/profiles/{id}/"

# Delete profile
curl -X DELETE "http://localhost:8000/api/profiles/{id}/"
```

### Example Responses

**Valid creation:**
```json
{
  "status": "success",
  "data": {
    "id": "667bb51e-972c-4dc8-ba92-48351aba1abe",
    "name": "john",
    "gender": "male",
    "gender_probability": 1.0,
    "sample_size": 2692560,
    "age": 75,
    "age_group": "senior",
    "country_id": "NG",
    "country_probability": 0.08,
    "created_at": "2026-04-16T18:39:19Z"
  }
}
```

**Error - Empty name:**
```json
{
  "status": "error",
  "message": "Missing or empty name"
}
```

**Error - Invalid type:**
```json
{
  "status": "error",
  "message": "Invalid type"
}
```

## 🏗️ Architecture

```
Request → URL Router → View → Service Layer → External APIs
                ↓         ↓              ↓
              CORS    Validation    Genderize.io
                        ↓            Agify.io
                  Business Logic     Nationalize.io
                   (age group,
                    country selection)
                        ↓
                    Database
                        ↓
                  JSON Response
```

### Key Components

| Component | Responsibility |
|-----------|---------------|
| `views.py` | Request validation, response formatting, error handling, idempotency |
| `models.py` | Profile data model with UUID primary key and indexes |
| `services/genderize_client.py` | Gender prediction API communication |
| `services/agify_client.py` | Age prediction API communication |
| `services/nationalize_client.py` | Nationality prediction API communication |

## 🚢 Deployment

### Railway (Recommended)

Deploy directly from your GitHub repository:
1. Create account at [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Django and deploys automatically

### Environment Variables

```env
# Production settings
DEBUG=False
SECRET_KEY=your-secret-key

# Hosts
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL)
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
```

## 📁 Project Structure

```
01-profile-api/
├── api/
│   ├── __init__.py
│   ├── views.py                 # Endpoint logic (4 endpoints)
│   ├── urls.py                  # URL routing
│   ├── models.py                # Profile data model
│   ├── admin.py                 # Django admin registration
│   ├── services/
│   │   ├── __init__.py
│   │   ├── genderize_client.py  # Gender API client
│   │   ├── agify_client.py      # Age API client
│   │   └── nationalize_client.py # Nationality API client
│   └── migrations/              # Database migrations
├── config/
│   ├── settings.py              # Django config + CORS
│   ├── urls.py                  # Main URL config
│   └── wsgi.py                  # Production entry point
├── pyproject.toml               # uv project configuration
├── uv.lock                      # Locked dependencies
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
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True
```

### Database Settings

```python
# Development and Production (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
```

### Model Indexes

```python
class Meta:
    indexes = [
        models.Index(fields=['gender']),
        models.Index(fields=['country_id']),
        models.Index(fields=['age_group']),
    ]
```

## ⚡ Performance

- **Response Time**: <1000ms (including external API calls)
- **Concurrent Requests**: Handles multiple requests without blocking
- **Timeout Protection**: 10-second limit on each external API call
- **Database Indexes**: Optimized for filtered queries

## 🐛 Error Handling Matrix

| Scenario | HTTP Status | User Message |
|----------|-------------|--------------|
| Missing name field | 400 | Missing or empty name |
| Empty name string | 400 | Missing or empty name |
| Name as number/object | 422 | Invalid type |
| Profile not found (invalid UUID) | 404 | Profile not found |
| Profile not found (not in DB) | 404 | Profile not found |
| Genderize API fails | 502 | Genderize returned an invalid response |
| Agify API fails | 502 | Agify returned an invalid response |
| Nationalize API fails | 502 | Nationalize returned an invalid response |

## 📝 Development Notes

### Age Group Logic

```python
if age <= 12:
    age_group = "child"
elif age <= 19:
    age_group = "teenager"
elif age <= 59:
    age_group = "adult"
else:
    age_group = "senior"
```

### Country Selection Logic

```python
# Pick country with highest probability
top_country = max(data['country'], key=lambda x: x['probability'])
```

### Idempotency Logic

```python
existing_profile = Profile.objects.filter(name__iexact=name).first()
if existing_profile:
    return existing_profile  # Don't create new one
```

### Testing Strategy

```bash
# Test idempotency
curl -X POST http://localhost:8000/api/profiles -d '{"name":"test"}'
curl -X POST http://localhost:8000/api/profiles -d '{"name":"test"}'  # Returns existing

# Test filters (case-insensitive)
curl "http://localhost:8000/api/profiles?gender=MALE&country_id=ng"

# Test error handling
curl -X POST http://localhost:8000/api/profiles -d '{"name":123}'  # 422
curl -X POST http://localhost:8000/api/profiles -d '{}'  # 400
```

## 🔄 External APIs

| API | Endpoint | Fields Used |
|-----|----------|-------------|
| Genderize | `https://api.genderize.io` | gender, probability, count |
| Agify | `https://api.agify.io` | age |
| Nationalize | `https://api.nationalize.io` | country[].country_id, country[].probability |
