# EmbedLead

**Embeddable Widget & Lead-Capture Platform**

EmbedLead is a multi-tenant backend platform that lets customers create embeddable
lead-capture widgets and install them on external websites with a single
`<script>` tag.

A visitor can submit a lead from a website that EmbedLead does not control. The
backend validates the request, applies abuse protection, enriches the submission
with IP/geolocation metadata, persists it under the correct tenant, and performs
non-critical notification work without allowing secondary failures to break the
main submission path.

Built as the FlyRank Internship Backend Track Capstone.

---

## What EmbedLead Demonstrates

The project focuses on production-oriented backend engineering concerns:

- Multi-tenant architecture
- Authentication and authorization
- Tenant isolation
- Widget CRUD
- Public widget keys
- Embeddable JavaScript
- Cross-origin browser requests
- CORS
- Request validation
- Oversized payload protection
- Rate limiting
- Honeypot spam protection
- Redis caching/infrastructure
- IP metadata collection
- Geo-provider fallback
- Safe background side effects
- PostgreSQL persistence
- Alembic migrations
- Pagination
- Tenant-scoped analytics
- Automated unit and integration testing
- Ruff linting
- Strict mypy type checking
- Docker-based local infrastructure

The core design principle is:

> Public traffic is untrusted. Validate it at the boundary, protect the service,
> degrade gracefully when dependencies fail, and never allow a non-critical
> dependency to destroy the primary business operation.

---

## Architecture

```text
                         ┌─────────────────────────┐
                         │      Widget Owner        │
                         │   Authenticated Client   │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │   Widget Management API  │
                         │       FastAPI            │
                         └────────────┬────────────┘
                                      │
                         ┌────────────▼────────────┐
                         │     Tenant Isolation     │
                         │  Services / Repositories │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      PostgreSQL 17       │
                         │ widgets / leads / data  │
                         └─────────────────────────┘


 ┌───────────────────────┐
 │ External Customer     │
 │ Website               │
 │                       │
 │ second-origin demo    │
 └───────────┬───────────┘
             │
             │ <script src=".../widget.v1.js?key=...">
             ▼
 ┌───────────────────────┐
 │ Versioned JS Widget   │
 │ widget.v1.js          │
 └───────────┬───────────┘
             │
             ├──── GET public widget config
             │
             └──── POST public lead
                         │
                         ▼
              ┌───────────────────────┐
              │ Public Submission API │
              └───────────┬───────────┘
                          │
              ┌───────────▼───────────┐
              │ Boundary Validation   │
              │ Pydantic              │
              └───────────┬───────────┘
                          │
              ┌───────────▼───────────┐
              │ Abuse Protection      │
              │ Rate Limit + Honeypot  │
              └───────────┬───────────┘
                          │
              ┌───────────▼───────────┐
              │ Geo Enrichment        │
              │ Provider A → B        │
              └───────────┬───────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ PostgreSQL      │
                 │ Persist Lead    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Notification    │
                 │ Side Effect     │
                 │ Failure-safe    │
                 └─────────────────┘
```

---

## Request Flows

### 1. Widget Owner Flow

```text
Authenticated owner
       │
       ▼
Create widget
       │
       ▼
Widget stored under tenant
       │
       ▼
Generate public widget key
       │
       ▼
Generate embed snippet
       │
       ▼
Customer copies one-line <script>
```

### 2. Visitor Flow

```text
External website
       │
       ▼
widget.v1.js
       │
       ├── GET public configuration
       │
       ▼
Render form
       │
       ▼
Visitor submits
       │
       ▼
CORS + validation
       │
       ▼
Rate limit + honeypot
       │
       ▼
Geo Provider A
       │
       ├── failure ──► Provider B
       │
       └── failure ──► continue without geo
       │
       ▼
Persist lead
       │
       ▼
Notification
       │
       └── failure ──► ignored for primary request
```

### 3. Dashboard Flow

```text
Authenticated owner
       │
       ▼
Tenant-scoped dashboard API
       │
       ├── Lead list
       ├── Pagination
       ├── Widget statistics
       └── Geo analytics
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| API | FastAPI |
| Validation | Pydantic |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Database | PostgreSQL 17 |
| Cache / infrastructure | Redis 8 |
| Background jobs | Celery |
| HTTP server | Uvicorn |
| Testing | pytest |
| Linting | Ruff |
| Type checking | mypy |
| Infrastructure | Docker Compose |
| Browser widget | Vanilla JavaScript |
| Demo customer site | Plain HTML |
| Version control | Git / GitHub |

---

## Project Structure

```text
EmbedLead/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── public.py
│   │       ├── widget.py
│   │       └── ...
│   │
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── workers/
│   └── main.py
│
├── alembic/
│   └── versions/
│
├── demo/
│   └── second-origin/
│       └── index.html
│
├── widget/
│   └── widget.v1.js
│
├── tests/
│   ├── integration/
│   └── unit/
│
├── EVIDENCE.md
├── BUILDLOG.md
├── capstone.yaml
├── .env.example
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## Local Setup

### Prerequisites

Install:

- Python 3.11+
- Docker Desktop
- Git

No paid services or credit card are required.

### 1. Clone the repository

```bash
git clone <YOUR_PUBLIC_GITHUB_REPOSITORY>
cd EmbedLead
```

### 2. Create the virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If the project is installed through the project's configured package manager,
use the dependency installation command documented by the repository.

### 4. Configure environment

Copy:

```
.env.example
```

to:

```
.env
```

Then provide local development values.

Never commit `.env`.

### 5. Start infrastructure

```bash
docker compose up -d
```

Expected services:

```
embedlead-postgres
embedlead-redis
```

Verify:

```bash
docker ps
```

PostgreSQL and Redis should report healthy.

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the API

```bash
uvicorn app.main:app --reload
```

API:

```
http://127.0.0.1:8000
```

Health endpoint:

```
http://127.0.0.1:8000/api/v1/health
```

Readiness endpoint:

```
http://127.0.0.1:8000/api/v1/ready
```

---

## Running the Tests

Run the complete test suite:

```bash
pytest -v
```

Final verification:

```text
21 passed
```

Static checks:

```bash
ruff check .
```

Expected:

```text
All checks passed!
```

Type checking:

```bash
mypy app
```

Expected:

```text
Success: no issues found in 50 source files
```

---

## Embeddable Widget

The widget is served as a versioned JavaScript bundle:

```
GET /api/v1/widget.v1.js
```

A generated customer snippet follows this pattern:

```html
<script src="http://127.0.0.1:8000/api/v1/widget.v1.js?key=PUBLIC_WIDGET_KEY"></script>
```

The actual generated snippet is returned by the widget embed endpoint.

The JavaScript bundle automatically:

- Reads its own script URL.
- Extracts the public widget key.
- Determines the API origin.
- Loads widget configuration.
- Renders the form.
- Submits visitor data.
- Displays success or failure feedback.

---

## Second-Origin Demo

The repository contains:

```
demo/second-origin/index.html
```

Run a second local HTTP server from the project root:

```bash
python -m http.server 5500
```

Then open:

```
http://127.0.0.1:5500/demo/second-origin/
```

The API runs on:

```
http://127.0.0.1:8000
```

Because the ports differ, these are different browser origins.

This demonstrates the real cross-origin embedding scenario required by the capstone.

---

## Public API

### Health

```
GET /api/v1/health
```

Returns:

```json
{
  "status": "ok"
}
```

### Readiness

```
GET /api/v1/ready
```

Returns the health state of the application dependencies.

### Public Widget Configuration

```
GET /api/v1/public/widgets/{public_key}/config
```

Returns public configuration for an active widget.

The response is cacheable using the configured widget cache TTL.

### Public Lead Submission

```
POST /api/v1/public/widgets/{public_key}/leads
```

Example:

```json
{
  "name": "Example User",
  "email": "example@example.com",
  "message": "Hello from an external website.",
  "website": null
}
```

Successful submissions return a success response.

Invalid requests are rejected at the API boundary.

### Widget JavaScript

```
GET /api/v1/widget.v1.js
```

Returns the versioned JavaScript widget bundle.

The bundle is served with a long-lived immutable cache policy.

### Widget Embed Information

```
GET /api/v1/widgets/{widget_id}/embed
```

Returns:

- widget ID
- public key
- generated embed snippet

---

## Security Model

### Tenant Isolation

Every owner-facing query is scoped to the authenticated tenant.

A tenant cannot use its credentials to access another tenant's widgets or leads.

This is covered by automated integration tests.

### Public Keys

Public widget keys are intentionally safe for browser embedding.

They identify the widget but do not grant owner-level administrative access.

### Validation

Pydantic validates public payloads before business logic executes.

The API rejects:

- invalid email addresses
- oversized fields
- malformed input
- inactive widgets

### Rate Limiting

Public lead submission is rate-limited to prevent a single source from flooding
the service.

Burst traffic is rejected with HTTP 429.

### Honeypot

The widget contains a hidden `website` field.

Normal visitors leave it empty.

A populated value is treated as spam and is not persisted.

### CORS

The public browser-facing API is configured for cross-origin requests.

The second-origin demo verifies the actual browser integration rather than relying
only on server-side requests.

---

## Resilience

### Geo Fallback

Geo enrichment follows:

```text
Provider A
    │
    ├── success → use result
    │
    └── failure
            │
            ▼
        Provider B
            │
            ├── success → use result
            │
            └── failure → continue without geo
```

Geo enrichment is deliberately non-critical.

A geo provider outage must not prevent lead persistence.

Automated tests mock providers so fallback behavior remains deterministic.

### Notification Failure

Notification is a secondary side effect.

The sequence is:

```text
Receive request
      ↓
Validate
      ↓
Protect
      ↓
Enrich
      ↓
Persist lead
      ↓
Notify
```

If notification fails, the lead remains persisted and the primary operation remains
successful.

This behavior is explicitly covered by integration tests.

### Background Processing

Celery infrastructure is included for notification/background work.

The design keeps slow or non-critical operations away from the critical persistence
path.

The Windows development environment can encounter multiprocessing permission
limitations when running a Celery worker with the default process pool. The core API
and deterministic automated tests remain unaffected, and notification failure
is explicitly tested at the application boundary.

### Caching

Two separate caching strategies are used:

**Widget JavaScript**

The versioned bundle uses a long-lived immutable cache policy:

```
Cache-Control: public, max-age=31536000, immutable
```

Because the filename contains the version, a future bundle can be released under
a new URL.

**Widget Configuration**

Configuration uses a shorter configurable cache lifetime so widget configuration can
change without requiring a new JavaScript bundle.

---

## Testing Strategy

The test suite focuses on failure modes rather than only happy paths.

Coverage includes:

- public lead submission
- authentication
- inactive widgets
- invalid email
- oversized payloads
- rate limiting
- tenant isolation
- widget delivery
- widget public-key submission
- pagination
- honeypot spam protection
- notification failure
- analytics
- analytics authorization
- configuration parsing
- CORS configuration
- payload limits
- geo provider success
- geo provider fallback

Final result:

```text
21 passed in 8.25s
```

---

## Quality Gates

The final repository passes:

```bash
ruff check .
```
```text
All checks passed!
```

and:

```bash
mypy app
```
```text
Success: no issues found in 50 source files
```

and:

```bash
pytest -v
```
```text
21 passed
```

---

## Evidence

Detailed Definition-of-Done proof is maintained in:

```
EVIDENCE.md
```

It contains concrete test names, command output, database verification, widget
delivery evidence, cross-origin evidence, and the final verification summary.

Screenshots captured during final verification provide additional visual evidence.

---

## AI-Assisted Development

AI assistance was used during development.

The AI was treated as an engineering assistant rather than an authority.

Generated or suggested implementation was:

- inspected,
- executed locally,
- tested,
- corrected when necessary,
- verified through static analysis and integration tests.

The complete development and AI-usage record is maintained in:

```
BUILDLOG.md
```

---

## Required Submission Pack

The repository contains the five required capstone submission files:

- `README.md`
- `capstone.yaml`
- `EVIDENCE.md`
- `BUILDLOG.md`
- `.env.example`

These files are intentionally kept in the repository root so an evaluator can find
them immediately.

---

## Definition of Done

The core capstone requirements are implemented and verified:

- [x] Authenticated widget management
- [x] Multi-tenant authorization
- [x] Tenant isolation
- [x] Widget embed snippet
- [x] Public widget configuration
- [x] Versioned JavaScript bundle
- [x] Second-origin rendering
- [x] Cross-origin submissions
- [x] Boundary validation
- [x] Oversized payload protection
- [x] Rate limiting
- [x] Honeypot spam protection
- [x] IP metadata
- [x] Geo provider fallback
- [x] Graceful geo failure
- [x] Safe notification failure
- [x] Lead persistence
- [x] Pagination
- [x] Tenant-scoped analytics
- [x] Alembic migrations
- [x] Automated tests
- [x] Ruff
- [x] Strict mypy
- [x] Docker PostgreSQL
- [x] Redis infrastructure
- [x] Required submission-pack files

---

## Limitations

This is intentionally a local capstone implementation rather than a production
internet deployment.

Current limitations include:

- No real CDN.
- No production domain.
- No production hosting requirement.
- The customer site is represented by a local second-origin HTML server.
- The widget bundle is plain JavaScript rather than a minified production build.
- Notification infrastructure is demonstrated locally and tested for failure safety.
- Geo providers are mocked in automated tests to keep fallback behavior deterministic.
- The dashboard is primarily an API/backend capability rather than a full frontend
  analytics application.
- Celery's Windows process-pool behavior can require a Linux/WSL/containerized
  worker environment for production-style multiprocessing.

These limitations do not change the core capstone acceptance requirements.

---

## Demo Flow

The intended six-minute demonstration is:

1. Create a widget through the authenticated API.
2. Show the generated public key and one-line script.
3. Open the second-origin customer website.
4. Show the widget rendering.
5. Submit a lead.
6. Show the lead persisted in PostgreSQL/dashboard API.
7. Demonstrate invalid input rejection.
8. Demonstrate rate limiting.
9. Demonstrate honeypot spam protection.
10. Demonstrate geo-provider fallback.
11. Demonstrate notification failure without losing the lead.
12. Close with analytics and tenant isolation.

The project is designed so the most important story is not the form itself:

> EmbedLead safely accepts untrusted data from websites it does not control.

---

## License

MIT