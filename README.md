# SCM API - Content Moderation Service

A FastAPI-based content moderation service that uses LLMs (OpenAI GPT-4 and Google Gemini) to analyze text and images for inappropriate content, with automatic notifications via Slack and email.

Versions overview
- v1 (local-first): PostgreSQL via docker-compose; endpoints under /api/v1.
- v2 (deployment-focused): Hugging Face Spaces (Docker) with SQLite; endpoints under /api/v2. Same features, deployment-optimized defaults.

Links to fill in
- v1 tag/branch: <N/A>
- v2 tag/branch: <N/A>
- Live Endpoint URL: <https://lamaq-scm-api-service-lamaq.hf.space/docs>

## 🏗️ Architecture

The backend is structured into three main components:

1. **Database Layer** - SQLAlchemy models and session management
2. **API Endpoints** - FastAPI routes with proper request/response schemas
3. **LLM Services** - OpenAI and Gemini integration for content analysis

### Directory Structure (key parts)

```
app/backend/
├── api/
│   └── v1/
│       ├── endpoints/
│       │   ├── moderation.py    # Text/Image moderation endpoints
│       │   └── analytics.py     # Analytics endpoints
│       └── router.py            # v1 API router
│   └── v2/
│       └── router.py            # v2 router (re-exports v1 endpoints)
├── database/
│   ├── base.py                  # SQLAlchemy Base
│   └── session.py               # Database session management
├── models/
│   └── moderation.py            # Database models
├── schemas/
│   ├── moderation.py            # Request/Response schemas
│   └── analytics.py             # Analytics schemas
├── services/
│   ├── llm_service.py           # LLM integration (OpenAI/Gemini)
│   ├── notification_service.py  # Slack/Email notifications
│   ├── moderation_service.py    # Main business logic
│   └── analytics_service.py     # Analytics and reporting
└── core/
   └── config.py                # Configuration management

app/
├── main.py                      # FastAPI app entrypoint (mounts /api/v1 and /api/v2)
└── deployment/                  # v2 deployment bundle (repo-scoped)
   ├── Dockerfile               # Build for Spaces (uses app/ code)
   ├── docker-compose.hf.yml    # Local test of deployment image
   ├── .env.example             # Example env vars for v2
   └── alembic/
      ├── env.py               # Alembic env (imports app.backend.*)
      ├── versions/
      │   └── 95e1a31eab38_initial_migration_with_models.py
      └── ../alembic.ini       # Alembic configuration (repo-scoped for v2)
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- API keys for LLM providers (OpenAI and/or Gemini)
- Notification service credentials (Slack webhook, BrevoMail API)

### Local Development Setup (v1)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd SCM-API
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Configure environment variables** in `.env`:
   ```bash
   # Database Configuration
   POSTGRES_USER=moderator
   POSTGRES_PASSWORD=moderator
   POSTGRES_DB=moderator
   DATABASE_URL=postgresql://moderator:moderator@db:5432/moderator
   USE_SQLITE=false

   # LLM Providers (at least one required)
   OPENAI_API_KEY=your_openai_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here

   # Notification Services (optional)
   SLACK_WEBHOOK_URL=your_slack_webhook_url
   SLACK_CHANNEL=#general
   BREVO_API_KEY=your_brevo_api_key
   SENDER_EMAIL=noreply@yourdomain.com
   ```

4. **Start the services**:
   ```bash
   docker-compose up -d
   ```

5. **Run database migrations** (first time only):
   ```bash
   docker-compose exec api alembic upgrade head
   ```

6. **Verify the setup**:
   ```bash
   # Check if all containers are running
   docker-compose ps
   
   # Check API health
   curl http://localhost:8000/health
   ```

7. **Access the API**:
   - **API Base URL**: http://localhost:8000
   - **Interactive Docs**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

### Local Development Workflow (v1)

1. **Start development environment**:
   ```bash
   docker-compose up -d
   ```

2. **View logs**:
   ```bash
   docker-compose logs -f api
   ```

3. **Stop services**:
   ```bash
   docker-compose down
   ```

4. **Rebuild after changes**:
   ```bash
   docker-compose up -d --build
   ```

## 🧪 Testing the API

### 1. Health Check
```bash
curl http://localhost:8000/health
```
**Expected Response**:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 2. Text Moderation
```bash
curl -X POST "http://localhost:8000/api/v1/moderate/text" \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "test@example.com",
    "text_content": "This is a test message to moderate"
  }'
```

**Expected Response**:
```json
{
  "request_id": 1,
  "user_email": "test@example.com",
  "content_type": "text",
  "status": "completed",
  "created_at": "2024-01-01T12:00:00"
}
```

### 3. Image Moderation
```bash
# First, encode your image to base64
# For testing, you can use a simple test image
curl -X POST "http://localhost:8000/api/v1/moderate/image" \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "test@example.com",
    "image_data": "base64_encoded_image_data_here"
  }'
```

### 4. Get Moderation Result
```bash
curl "http://localhost:8000/api/v1/moderate/results/1"
```

**Expected Response**:
```json
{
  "request_id": 1,
  "classification": "safe",
  "confidence": 0.95,
  "reasoning": "This content appears to be appropriate and safe.",
  "llm_provider": "openai",
  "created_at": "2024-01-01T12:00:00"
}
```

### 5. Analytics Summary
```bash
curl "http://localhost:8000/api/v1/analytics/summary?user=test@example.com"
```

**Expected Response**:
```json
{
  "user_email": "test@example.com",
  "total_requests": 2,
  "completed_requests": 2,
  "failed_requests": 0,
  "classification_breakdown": {
    "safe": 2
  },
  "recent_activity": [
    {
      "request_id": 2,
      "content_type": "image",
      "status": "completed",
      "created_at": "2024-01-01T12:05:00",
      "classification": "safe",
      "confidence": 0.92,
      "llm_provider": "openai"
    }
  ],
  "last_request_date": "2024-01-01T12:05:00"
}
```

### 6. Test with Swagger UI
1. Open http://localhost:8000/docs in your browser
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the required parameters
5. Click "Execute"

## 🌐 Hugging Face Spaces Deployment (v2)

### Prerequisites
- Hugging Face account
- API keys for LLM providers
- Notification service credentials

### Deployment Steps

1. **Create a new Space**:
   - Go to [Hugging Face Spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Choose "Docker" as the SDK
   - Set Space name and visibility

2. **Upload required files** (from `app/deployment` or the v2 tag):
   ```
   Dockerfile                      # Production Dockerfile (repo-scoped)
   docker-compose.hf.yml           # Optional local check of deployment image
   app/                            # Application code
   requirements.txt                # Python dependencies
   alembic/                        # Database migrations (copy from app/deployment/alembic)
   alembic.ini                     # Alembic configuration (copy from app/deployment/alembic.ini)
   ```

3. **Configure environment variables** in HF Spaces settings:
   ```bash
   # Database (SQLite on Spaces)
   DATABASE_URL=sqlite:////data/scm_api.db
   SKIP_MIGRATIONS=true
   OPENAI_API_KEY=your_openai_api_key
   GEMINI_API_KEY=your_gemini_api_key
   SLACK_WEBHOOK_URL=your_slack_webhook
   BREVO_API_KEY=your_brevo_api_key
   SENDER_EMAIL=noreply@yourdomain.com
   ```

4. **Deploy**:
   - HF Spaces will automatically build and deploy your application
   - Monitor the build logs for any issues

5. **Access your deployed API**:
   - **API Base URL**: `https://your-space-name.hf.space`
   - **Interactive Docs**: `https://your-space-name.hf.space/docs`
   - **Health Check**: `https://your-space-name.hf.space/health`
   - Note: Spaces expects apps to listen on `$PORT` (typically 7860). The deployment Dockerfile uses `${PORT:-7860}`.

6. **v1 vs v2 behavior**
   - v1 uses Postgres + Alembic migrations (run via compose task/CLI).
   - v2 uses SQLite for portability on Spaces, with a startup fallback to create_all (when SKIP_MIGRATIONS=true). Data is ephemeral across rebuilds.

7. **Endpoints (v2)**
    - Same as v1 but mounted under `/api/v2`:
       - `POST /api/v2/moderate/text`
       - `POST /api/v2/moderate/image`
       - `GET /api/v2/analytics/summary?user=test@example.com`

### Testing Deployed API

1. **Health Check**:
   ```bash
   curl https://your-space-name.hf.space/health
   ```

2. **Text Moderation**:
   ```bash
   curl -X POST "https://your-space-name.hf.space/api/v1/moderate/text" \
     -H "Content-Type: application/json" \
     -d '{
       "user_email": "test@example.com",
       "text_content": "This is a test message"
     }'
   ```

3. **Analytics**:
   ```bash
   curl "https://your-space-name.hf.space/api/v1/analytics/summary?user=test@example.com"
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | Database connection string | Yes | v1: `postgresql://moderator:moderator@db:5432/moderator` · v2: `sqlite:////data/scm_api.db` |
| `SKIP_MIGRATIONS` | Skip Alembic and use SQLAlchemy create_all at startup (v2) | No | `false` |
| `USE_SQLITE` | Local flag to enable SQLite create_all in v1 app | No | `false` |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | No* | - |
| `GEMINI_API_KEY` | Google Gemini API key | No* | - |
| `SLACK_WEBHOOK_URL` | Slack webhook URL | No | - |
| `SLACK_CHANNEL` | Slack channel for notifications | No | `#general` |
| `BREVO_API_KEY` | BrevoMail API key | No | - |
| `SENDER_EMAIL` | Sender email for notifications | No | - |
| `POSTGRES_USER` | PostgreSQL username | No | `moderator` |
| `POSTGRES_PASSWORD` | PostgreSQL password | No | `moderator` |
| `POSTGRES_DB` | PostgreSQL database name | No | `moderator` |

*At least one LLM provider (OpenAI or Gemini) is required.

### API Keys Setup

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Add to your `.env` file: `OPENAI_API_KEY=sk-...`

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Add to your `.env` file: `GEMINI_API_KEY=...`

#### Slack Webhook
1. Go to [Slack Apps](https://api.slack.com/apps)
2. Create a new app
3. Enable Incoming Webhooks
4. Create a webhook for your channel
5. Add to your `.env` file: `SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...`

#### BrevoMail API Key
1. Go to [Brevo](https://www.brevo.com/)
2. Create an account
3. Navigate to API Keys section
4. Generate a new API key
5. Add to your `.env` file: `BREVO_API_KEY=xkeysib-...`

## 🗄️ Database Schema

### Tables

1. **moderation_requests**
   - `id` (Primary Key)
   - `user_email` (Indexed)
   - `content_type` (text/image)
   - `content_hash` (Unique, indexed)
   - `status` (pending/completed/failed)
   - `created_at`

2. **moderation_results**
   - `id` (Primary Key)
   - `request_id` (Foreign Key)
   - `classification` (toxic/spam/harassment/safe)
   - `confidence` (Float)
   - `reasoning` (Text)
   - `llm_provider` (openai/gemini)
   - `llm_response` (JSONB/Text)

3. **notification_logs**
   - `id` (Primary Key)
   - `request_id` (Foreign Key)
   - `channel` (slack/email)
   - `status` (success/failed)
   - `sent_at`

## 🔄 Docker Configuration

### Development (`Dockerfile.dev`)
- Uses volume mounts for hot reload
- Includes entrypoint script for migrations
- Runs with `--reload` flag

### Production (`app/deployment/Dockerfile`)
- Optimized for Spaces (uses repo layout)
- Non-root user and correct PORT binding
- Copies `app/deployment/alembic*` into image

### Docker Compose Files

- `docker-compose.yml` - Local development with PostgreSQL
- `docker-compose.hf.yml` - Hugging Face Spaces style local test with SQLite (optional)

## 📊 Features

### Content Classification
- **Toxic** - Harmful or offensive content
- **Spam** - Unwanted promotional content
- **Harassment** - Bullying or threatening content
- **Safe** - Appropriate content

### LLM Integration
- **OpenAI GPT-4** - Text and image analysis
- **Google Gemini** - Text and image analysis
- **Automatic fallback** - Uses first available provider

### Notifications
- **Slack** - Real-time alerts to channels
- **Email** - BrevoMail integration
- **Automatic triggering** - For flagged content

### Analytics
- **User summaries** - Per-user statistics
- **Classification breakdown** - Content type analysis
- **Recent activity** - Latest requests

## 🚨 Limitations

### Hugging Face Spaces
- **No persistent storage** - SQLite database is ephemeral
- **No background processing** - All operations are synchronous
- **Limited resources** - Subject to HF Spaces constraints

### Production Considerations
- **External database** - Use PostgreSQL for production
- **Authentication** - Implement proper auth
- **Rate limiting** - Add request throttling
- **Monitoring** - Add logging and metrics

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   ```bash
   # Check if database is running
   docker-compose ps
   
   # Check database logs
   docker-compose logs db
   
   # Restart database
   docker-compose restart db
   ```

2. **API Key Issues**:
   ```bash
   # Verify environment variables
   docker-compose exec api env | grep API_KEY
   
   # Check API key format
   # OpenAI: sk-... (starts with sk-)
   # Gemini: ... (no specific prefix)
   ```

3. **Migration Errors**:
   ```bash
   # Reset database
   docker-compose down -v
   docker-compose up -d
   docker-compose exec api alembic upgrade head
   ```

4. **Port Already in Use**:
   ```bash
   # Check what's using port 8000
   netstat -tulpn | grep 8000
   
   # Stop conflicting services
   # Or change port in docker-compose.yml
   ```

5. **Build Failures**:
   ```bash
   # Clean build
   docker-compose down
   docker system prune -f
   docker-compose up -d --build
   ```

### Logs and Debugging

1. **View API logs**:
   ```bash
   docker-compose logs -f api
   ```

2. **View database logs**:
   ```bash
   docker-compose logs -f db
   ```

3. **Access database directly**:
   ```bash
   docker-compose exec db psql -U moderator -d moderator
   ```

4. **Check API health**:
   ```bash
   curl http://localhost:8000/health
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
