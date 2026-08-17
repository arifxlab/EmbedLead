# EmbedLead

Multi-tenant embeddable lead-capture infrastructure built with FastAPI, PostgreSQL, Redis, and Celery.

EmbedLead provides a secure backend for websites and applications that need to embed lead-capture widgets without exposing tenant data or internal APIs. Each tenant can manage its own widgets and leads while public clients interact through scoped widget public keys.

## Overview

EmbedLead is designed as a backend-first SaaS-style platform with a clear separation between:

- authenticated tenant management APIs
- public widget APIs
- application services
- repository/data-access layers
- PostgreSQL persistence
- Redis caching
- Celery background processing

The system focuses on production-oriented backend concerns such as tenant isolation, authentication, rate limiting, payload protection, caching, asynchronous processing, database migrations, and automated testing.

## Core Features

### Multi-Tenant Architecture

Every tenant owns its widgets and leads.

Tenant-scoped queries enforce ownership at the repository layer so that authenticated users cannot access resources belonging to another tenant.

### Authentication

EmbedLead provides authenticated tenant APIs using:

- JWT access tokens
- password hashing with Argon2
- protected management endpoints
- tenant-aware authorization

### Embeddable Public Widgets

Widgets receive generated public keys using the format:

```text
pk_live_<secure-random-key>
```

Public clients can submit leads using the widget's public key without requiring a user JWT.

Example:

```text
POST /api/v1/public/widgets/{public_key}/leads
```

### Lead Capture

Leads support:

- name
- email
- message
- IP address
- user agent
- country
- region
- city
- latitude
- longitude

Lead creation is persisted transactionally before notification work is dispatched.

### Geolocation

Public lead submissions can resolve geographic metadata from the request IP.

The geolocation service supports:

- primary provider lookup
- fallback provider behavior
- graceful failure handling

### Redis Caching

Public widget configuration is cached through Redis.

The cache uses a widget-specific key:

```text
widget:public-config:{public_key}
```

Cached configuration reduces repeated database queries for frequently accessed public widget endpoints.

### Background Processing

Celery is configured with Redis as its broker and result backend.

Lead notification work is dispatched asynchronously so the public submission request does not need to perform background notification processing synchronously.

Tasks also support automatic retry behavior.

### Rate Limiting

Public endpoints are protected using SlowAPI-based rate limiting to reduce abuse and excessive request volume.

### Payload Protection

Incoming request bodies are checked against a configurable maximum payload size.

Oversized requests receive:

```text
413 Request Entity Too Large
```

### CORS

CORS behavior is configurable through application settings and restricted to configured origins.

### Database Migrations

Database schema changes are managed through Alembic.

The migration history currently includes:

- tenant and user tables
- password hash support
- widgets
- leads
- lead metadata

## Architecture

```text
                         ┌──────────────────────┐
                         │      Client / Web    │
                         │   Embedded Widget    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         │                      │
                         │ Authenticated APIs   │
                         │ Public Widget APIs   │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
              ┌──────────┐   ┌────────────┐   ┌────────────┐
              │ Services │   │ Repositories│   │   Redis    │
              │          │   │            │   │   Cache    │
              └────┬─────┘   └─────┬──────┘   └────────────┘
                   │               │
                   │               ▼
                   │        ┌──────────────┐
                   │        │  PostgreSQL  │
                   │        └──────────────┘
                   │
                   ▼
            ┌──────────────┐
            │    Celery    │
            │  Background  │
            │    Tasks     │
            └──────┬───────┘
                   │
                   ▼
                Redis
```

## Request Flow

### Public Lead Submission

```text
Client
  │
  │ POST /public/widgets/{public_key}/leads
  ▼
FastAPI
  │
  ├── Validate payload
  ├── Apply rate limit
  ├── Validate widget public key
  ├── Verify widget is active
  ├── Resolve request metadata
  ├── Resolve geolocation
  │
  ▼
LeadService
  │
  ▼
LeadRepository
  │
  ▼
PostgreSQL
  │
  ├── Commit lead
  │
  ▼
Celery
  │
  ▼
Background notification
```

## Technology Stack

### Backend

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- Pydantic Settings
- SQLAlchemy 2.x
- asyncpg

### Database

- PostgreSQL
- Alembic

### Caching and Background Processing

- Redis
- Celery

### Security

- JWT
- PyJWT
- Argon2 password hashing
- SlowAPI rate limiting
- Configurable CORS
- Request payload size protection
- Tenant isolation

### Networking and Serialization

- HTTPX
- orjson
- python-multipart

### Observability

- structlog

### Development and Quality

- pytest
- pytest-asyncio
- pytest-cov
- Ruff
- mypy

## Project Structure

```text
EmbedLead/
│
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── health.py
│   │       ├── leads.py
│   │       ├── public.py
│   │       ├── router.py
│   │       └── widgets.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── limiter.py
│   │   ├── redis.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── middleware/
│   │
│   ├── models/
│   │   ├── lead.py
│   │   ├── mixins.py
│   │   ├── tenant.py
│   │   ├── user.py
│   │   └── widget.py
│   │
│   ├── repositories/
│   │   ├── lead.py
│   │   ├── user.py
│   │   └── widget.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── lead.py
│   │   └── widget.py
│   │
│   ├── services/
│   │   ├── auth.py
│   │   ├── geo.py
│   │   ├── lead.py
│   │   └── widget.py
│   │
│   ├── workers/
│   │   ├── celery_app.py
│   │   └── tasks.py
│   │
│   └── main.py
│
├── alembic/
│   └── versions/
│
├── tests/
│   ├── integration/
│   │   └── test_public_leads.py
│   ├── security/
│   ├── unit/
│   │   ├── test_config.py
│   │   └── test_geo.py
│   └── conftest.py
│
├── pyproject.toml
└── README.md
```

## API Overview

### Health

```text
GET /api/v1/health
```

Used to verify application availability.

### Authentication

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
```

### Widget Management

Authenticated widget management endpoints allow tenants to create and manage their widgets.

Example:

```text
POST /api/v1/widgets
```

### Public Widget Configuration

```text
GET /api/v1/public/widgets/{public_key}
```

Public widget configuration can be served through the Redis cache.

### Public Lead Submission

```text
POST /api/v1/public/widgets/{public_key}/leads
```

This endpoint is intended to be called by embedded websites.

### Lead Management

Authenticated tenants can retrieve their leads and individual lead records.

Example:

```text
GET /api/v1/leads
GET /api/v1/leads/{lead_id}
```

## Environment Configuration

EmbedLead uses Pydantic Settings for configuration.

Create an environment file containing the required application configuration.

Typical configuration includes:

```text
APP_NAME
APP_VERSION
API_PREFIX
DATABASE_URL
REDIS_URL
JWT_SECRET_KEY
JWT_ALGORITHM
JWT_ACCESS_TOKEN_EXPIRE_MINUTES
CORS_ORIGINS
MAX_SUBMISSION_PAYLOAD_BYTES
WIDGET_CACHE_TTL_SECONDS
```

Never commit production secrets to Git.

## Local Development

### 1. Clone the repository

```bash
git clone <repository-url>
cd EmbedLead
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

### 4. Configure environment variables

Create your local environment configuration and provide the PostgreSQL, Redis, JWT, CORS, and application settings.

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

### 7. Start the Celery worker

```bash
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

## Development Commands

Run the complete test suite:

```bash
pytest -v
```

Run Ruff:

```bash
ruff check .
```

Format the project:

```bash
ruff format .
```

Run static type checking:

```bash
mypy app
```

Compile Python sources:

```bash
python -m compileall app tests
```

Run migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

## Testing

EmbedLead currently includes integration and unit tests covering:

- public lead submission
- public widget configuration caching
- tenant isolation
- authentication requirements
- inactive widget rejection
- invalid email rejection
- oversized payload rejection
- public API rate limiting
- generated widget public key behavior
- lead listing pagination
- configuration parsing
- payload limits
- geolocation provider fallback

Current test status:

```text
15 passed
```

The test suite is designed to verify both normal behavior and important security boundaries.

## Security Model

EmbedLead treats tenant isolation as a core backend invariant.

Important security controls include:

### Tenant-Scoped Queries

Authenticated resources are queried using both resource identifiers and tenant identifiers.

This prevents a tenant from directly retrieving another tenant's resources by guessing or obtaining an object ID.

### Public Key Isolation

Public widget endpoints operate through generated widget public keys rather than exposing internal database identifiers as authorization credentials.

### Password Security

Passwords are never stored directly. Password hashing uses Argon2 through pwdlib.

### JWT Authentication

Management APIs use signed JWT access tokens.

### Rate Limiting

Public lead submission endpoints are rate limited to reduce abuse.

### Request Size Limits

Large request bodies are rejected before application processing.

### CORS Restrictions

Allowed origins are controlled through configuration rather than allowing arbitrary origins.

## Design Principles

EmbedLead follows several backend engineering principles:

- Keep API routes thin.
- Put business logic in services.
- Keep database access inside repositories.
- Enforce tenant boundaries at the data-access layer.
- Keep public and authenticated API concerns separated.
- Use asynchronous database access.
- Cache frequently accessed public configuration.
- Move background work to Celery.
- Validate external input at the API boundary.
- Fail safely when optional geolocation services are unavailable.
- Keep configuration environment-driven.
- Test security boundaries rather than only happy paths.

## Current Status

EmbedLead has a working backend foundation with:

- multi-tenant data model
- authentication
- widget management
- public widget APIs
- lead capture
- lead metadata
- geolocation lookup with fallback
- Redis caching
- Celery task infrastructure
- rate limiting
- payload protection
- PostgreSQL persistence
- Alembic migrations
- integration tests
- unit tests
- Ruff linting and formatting
- strict mypy type checking

The project is structured as a foundation for further SaaS-oriented development rather than as a simple CRUD demonstration.

## Future Improvements

Potential next-stage improvements include:

- production email/webhook notification providers
- tenant-level API keys
- webhook delivery with retry and dead-letter handling
- structured audit logging
- advanced lead filtering and search
- configurable widget schemas
- frontend embeddable widget package
- API documentation examples
- observability metrics
- distributed tracing
- deployment manifests
- CI/CD pipelines
- production containerization
- horizontal scaling strategies

## License

This project is currently intended as a portfolio and engineering project.