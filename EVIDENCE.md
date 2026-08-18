# EmbedLead — Capstone Evidence

## FlyRank Backend Track — Embeddable Widget & Lead-Capture Platform

This document maps the FlyRank Capstone Definition of Done to concrete implementation evidence.

The project was verified locally using PostgreSQL, Redis, FastAPI, automated tests, Ruff, mypy, and a second-origin HTML customer-site demonstration.

---

# 1. Evidence Summary

| Evidence              | What it proves                                                                     |
| --------------------- | ---------------------------------------------------------------------------------- |
| `screenshots/SS1.png` | Infrastructure health, readiness, Docker services, migrations, and database schema |
| `screenshots/SS2.png` | Public widget configuration endpoint and HTTP caching                              |
| `screenshots/SS3.png` | Versioned JavaScript widget bundle and long-lived cache headers                    |
| `screenshots/SS4.png` | Actual widget rendering and submission from a second origin                        |
| `screenshots/SS5.png` | Cross-origin lead persisted in PostgreSQL                                          |
| `screenshots/SS6.png` | Ruff, strict mypy, and complete automated test suite                               |
| `screenshots/SS7.png` | Clean Git working tree and final committed widget-delivery fix                     |

---

# 2. Widget Management

## Authenticated CRUD endpoints

**Requirement:** Authenticated CRUD endpoints for widgets; requests without valid authentication are rejected.

**Evidence:**

Automated integration coverage includes:

* `test_get_lead_requires_authentication`
* authenticated widget management endpoints
* widget creation and public-key generation

The API separates authenticated owner operations from public widget endpoints.

**Result:** PASS

---

## Multi-tenant isolation

**Requirement:** Tenant A cannot read or modify Tenant B's widgets or submissions.

**Evidence:**

Automated integration tests:

* `test_tenant_isolation_for_widgets`
* `test_widget_embed_snippet_is_versioned_and_tenant_safe`
* `test_lead_listing_pagination_and_tenant_isolation`
* `test_analytics_overview_is_tenant_isolated`

The service and repository layers scope widget and lead queries by tenant.

**Result:** PASS

---

## Embed snippet generated per widget

**Requirement:** The authenticated owner can obtain an embed snippet for a widget.

**Evidence:**

Automated integration test:

* `test_widget_embed_snippet_is_versioned_and_tenant_safe`

The widget delivery system generates a versioned script reference containing the public widget key.

**Result:** PASS

---

# 3. Widget Delivery

## Public widget configuration endpoint

**Requirement:** Public configuration endpoint serves a small payload with correct HTTP cache headers.

**Evidence:**

`screenshots/SS2.png`

The screenshot shows:

* successful `GET /api/v1/public/widgets/{public_key}/config`
* HTTP `200`
* widget configuration JSON
* `Cache-Control: public, max-age=300`

The configuration endpoint is public and tenant-safe because it resolves configuration through the widget's public key.

**Result:** PASS

---

## Versioned JavaScript bundle

**Requirement:** Widget JavaScript is served as a versioned bundle.

**Evidence:**

`screenshots/SS3.png`

The screenshot shows:

* `GET /api/v1/widget.v1.js`
* HTTP `200`
* `Content-Type: application/javascript`
* `Cache-Control: public, max-age=31536000, immutable`
* actual JavaScript widget source

The bundle is explicitly versioned as `widget.v1.js`.

**Result:** PASS

---

## Actual second-origin rendering

**Requirement:** Widget renders on a page served from a different origin than the API.

**Evidence:**

`screenshots/SS4.png`

The customer demonstration page is served separately using:

```text
python -m http.server 5500
```

The API runs on:

```text
http://127.0.0.1:8000
```

Therefore the customer page and API use different origins.

The screenshot shows the actual EmbedLead widget rendered on the second-origin page and displaying:

```text
Lead submitted successfully
```

**Result:** PASS

---

# 4. Public Submission API

## Cross-origin submission

**Requirement:** Cross-origin submissions work with correct CORS behavior and preflight handling.

**Evidence:**

The second-origin browser demonstration in `screenshots/SS4.png` successfully submits to the API.

The automated integration suite also exercises the public submission path and CORS configuration.

**Result:** PASS

---

## Boundary validation

**Requirement:** All incoming input is validated and malformed payloads return clean 4xx responses rather than 500 errors.

**Evidence:**

Automated test:

* `test_public_lead_rejects_invalid_email`

Pydantic `LeadCreate` validates:

* email format
* name length
* message length
* website/honeypot field length

**Result:** PASS

---

## Oversized payload protection

**Requirement:** Oversized payloads are rejected with an appropriate 4xx response.

**Evidence:**

Automated test:

* `test_public_lead_rejects_oversized_payload`

The application also has a configured submission payload limit.

**Result:** PASS

---

## Valid submissions are persisted

**Requirement:** Valid submissions are safely stored and linked to the correct widget and tenant.

**Evidence:**

`screenshots/SS5.png`

The PostgreSQL query returns the cross-origin evidence submission:

```text
email:     evidence@example.com
name:      EmbedLead Evidence User
message:   Cross-origin widget submission evidence
widget_id: 1830371b-34d4-479e-9981-e114b883c93d
```

Automated test:

* `test_public_lead_submission`

**Result:** PASS

---

# 5. Abuse Protection

## Rate limiting

**Requirement:** Rapid bursts return HTTP 429 while legitimate traffic remains available.

**Evidence:**

Automated integration test:

* `test_public_lead_rate_limit`

Redis-backed rate limiting is applied to the public submission endpoint.

**Result:** PASS

---

## Spam protection

**Requirement:** At least one spam-prevention mechanism demonstrably blocks spam.

**Evidence:**

EmbedLead uses a hidden `website` honeypot field.

The widget contains the hidden honeypot field, and the public API checks:

```text
payload.website
```

Automated integration test:

* `test_public_lead_honeypot_rejects_spam_without_persistence`

The spam submission is accepted at the HTTP contract level without creating a lead record.

**Result:** PASS

---

# 6. Enrichment & Safe Side Effects

## Geo provider fallback

**Requirement:** Provider A failure causes Provider B to be used.

**Evidence:**

Automated unit test:

* `test_geo_lookup_falls_back_when_primary_fails`

The geo service separates provider access from the submission workflow and supports fallback behavior.

The test uses mocked providers so the failure scenario is deterministic.

**Result:** PASS

---

## Geo failure does not break submission

**Requirement:** If all geo providers fail, the submission still succeeds without geo data.

**Evidence:**

The public submission route treats geo enrichment as non-critical:

```text
try:
    geo_metadata = await geo_service.lookup(ip_address)
except Exception:
    geo_metadata = None
```

Therefore a geo provider failure does not prevent lead persistence.

The integration suite exercises the resilient submission path.

**Result:** PASS

---

## Safe side-effect failure

**Requirement:** A failing confirmation email/notification/webhook must not prevent the lead from being stored.

**Evidence:**

Automated integration test:

* `test_public_lead_persists_when_notification_side_effect_fails`

The test verifies that lead persistence succeeds even when the notification side effect fails.

The application also provides Celery notification infrastructure for background processing.

**Result:** PASS

---

# 7. Tests & Quality

## Automated tests

**Requirement:** Automated tests cover the scary cases.

**Evidence:**

`screenshots/SS6.png`

Final test run:

```text
21 passed in 8.25s
```

Covered scenarios include:

* public lead submission
* cached widget configuration
* authentication
* inactive widgets
* invalid email
* oversized payload
* rate limiting
* tenant isolation
* widget embed snippet
* widget creation/public key
* pagination
* honeypot spam protection
* notification side-effect failure
* analytics
* analytics tenant isolation
* analytics authentication
* configuration
* geo provider fallback

**Result:** PASS

---

## Ruff

**Requirement:** Code passes Ruff.

**Evidence:**

`screenshots/SS6.png`

```text
ruff check .
All checks passed!
```

**Result:** PASS

---

## Strict mypy

**Requirement:** Type checking passes.

**Evidence:**

`screenshots/SS6.png`

```text
mypy app
Success: no issues found in 50 source files
```

**Result:** PASS

---

# 8. Database & Infrastructure

## PostgreSQL persistence

**Evidence:**

`screenshots/SS1.png`

PostgreSQL container:

```text
embedlead-postgres
```

was healthy.

Database verification showed the expected tables:

```text
alembic_version
leads
tenants
users
widgets
```

**Result:** PASS

---

## Redis infrastructure

**Evidence:**

`screenshots/SS1.png`

Redis container:

```text
embedlead-redis
```

was healthy.

The readiness endpoint returned:

```text
ready  ok  ok
```

for application, database, and Redis readiness.

**Result:** PASS

---

## Alembic migrations

**Evidence:**

`screenshots/SS1.png`

Alembic was at the current head revision:

```text
60d6c21d0ea4
```

The database schema was confirmed directly through PostgreSQL.

**Result:** PASS

---

# 9. Caching

## Widget configuration caching

**Evidence:**

`screenshots/SS2.png`

The public widget configuration endpoint returned:

```text
Cache-Control: public, max-age=300
```

The integration test:

* `test_public_widget_config_is_cached_and_tenant_safe`

also verifies the configuration caching and tenant-safety behavior.

**Result:** PASS

---

## Versioned bundle caching

**Evidence:**

`screenshots/SS3.png`

The widget bundle returned:

```text
Cache-Control: public, max-age=31536000, immutable
```

This is appropriate for a versioned asset such as:

```text
widget.v1.js
```

**Result:** PASS

---

# 10. Background Jobs

## Celery notification infrastructure

**Requirement:** At least one background job exists for slow/non-critical work.

**Evidence:**

The project contains Celery notification infrastructure.

The integration suite specifically verifies resilience when the notification side effect fails:

* `test_public_lead_persists_when_notification_side_effect_fails`

The main lead persistence path remains successful when the notification worker/side effect fails.

**Result:** PASS

---

# 11. Documentation & Submission Pack

## README.md

The repository README documents:

* project purpose
* architecture
* setup
* API usage
* development workflow
* limitations

**Result:** PASS

---

## BUILDLOG.md

`BUILDLOG.md` documents the incremental development process, validation, AI-assisted development, corrections, and implementation decisions.

**Result:** PASS

---

## EVIDENCE.md

This document provides one or more concrete proofs for every Definition-of-Done requirement.

**Result:** PASS

---

## capstone.yaml

`capstone.yaml` provides the evaluator manifest:

```yaml
run: uvicorn app.main:app --reload
seed: python scripts/e2e_setup.py
test: pytest -v
base_url: http://127.0.0.1:8000
```

The seed command was verified successfully and produced:

```text
PUBLIC_KEY=pk_e2e_8cdd674a668a4be7b095
WIDGET_ID=6bfc01f0-0108-4b9e-8ee7-78c0145eb095
```

**Result:** PASS

---

## .env.example

The repository contains `.env.example` for environment configuration without committing real secrets.

**Result:** PASS

---

# 12. Final Definition-of-Done Matrix

| Definition of Done             | Status | Evidence                |
| ------------------------------ | -----: | ----------------------- |
| Authenticated widget CRUD      |   PASS | Tests / API             |
| Multi-tenant isolation         |   PASS | SS6 + integration tests |
| Embed snippet                  |   PASS | SS6                     |
| Public cached config           |   PASS | SS2                     |
| Versioned widget bundle        |   PASS | SS3                     |
| Second-origin rendering        |   PASS | SS4                     |
| CORS / cross-origin submission |   PASS | SS4 + tests             |
| Input validation               |   PASS | SS6                     |
| Oversized payload rejection    |   PASS | SS6                     |
| Valid lead persistence         |   PASS | SS5 + tests             |
| Rate limiting                  |   PASS | SS6                     |
| Honeypot spam protection       |   PASS | SS6                     |
| Geo provider fallback          |   PASS | SS6                     |
| Graceful geo failure           |   PASS | implementation/tests    |
| Safe notification failure      |   PASS | SS6                     |
| Dashboard analytics            |   PASS | SS6                     |
| Tenant-safe analytics          |   PASS | SS6                     |
| Automated tests                |   PASS | SS6                     |
| Ruff                           |   PASS | SS6                     |
| Strict mypy                    |   PASS | SS6                     |
| PostgreSQL migrations          |   PASS | SS1                     |
| Redis infrastructure           |   PASS | SS1                     |
| Celery infrastructure          |   PASS | tests / implementation  |
| README                         |   PASS | repository              |
| BUILDLOG.md                    |   PASS | repository              |
| EVIDENCE.md                    |   PASS | this document           |
| capstone.yaml                  |   PASS | repository              |
| .env.example                   |   PASS | repository              |
| Public GitHub repository       |   PASS | SS7                     |

---

# 13. Final Verification

Final repository verification:

```text
git status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

Final commit:

```text
abf9a28 (HEAD -> main, origin/main) fix: restore embeddable widget delivery
```

Quality gates:

```text
Ruff: PASS
mypy: PASS
pytest: 21 passed
```

Widget verification:

```text
Versioned JavaScript bundle: PASS
Public widget configuration: PASS
Second-origin rendering: PASS
Cross-origin submission: PASS
Database persistence: PASS
```

---

# 14. Screenshot Index

The submission repository contains:

```text
screenshots/
├── SS1.png
├── SS2.png
├── SS3.png
├── SS4.png
├── SS5.png
├── SS6.png
└── SS7.png
```

### SS1 — Infrastructure baseline

Health/readiness, Docker services, Alembic head, and PostgreSQL schema.

### SS2 — Cached widget configuration

Public configuration response with `Cache-Control: public, max-age=300`.

### SS3 — Versioned widget bundle

`widget.v1.js` served as real JavaScript with immutable long-lived caching.

### SS4 — Second-origin widget

Actual EmbedLead widget rendered and submitted from the separate customer-site origin.

### SS5 — Persistence proof

The cross-origin evidence submission is visible in PostgreSQL.

### SS6 — Quality and automated testing

Ruff, mypy, and the complete `21 passed` test suite.

### SS7 — Final repository state

Clean working tree and final widget-delivery fix committed and synchronized with `origin/main`.

---

# 15. Honest Limitations

This project intentionally remains within the realistic scope defined by the FlyRank capstone.

* The customer site is a local second-origin HTML page rather than a production domain.
* The JavaScript bundle is versioned but is not distributed through a real CDN.
* Notification delivery is represented through background infrastructure rather than a production email provider.
* Geo providers are used for development and mocked for deterministic fallback testing.
* The dashboard is intentionally backend/API-focused rather than a full production frontend.
* Production deployment, observability, and horizontal scaling are outside the core capstone scope.

These limitations do not prevent the core Definition of Done from being satisfied.

---

# Final Status

**EmbedLead Capstone — CORE COMPLETE**

The core Definition of Done has been implemented and verified through automated tests, direct database verification, HTTP responses, second-origin browser execution, static analysis, type checking, and repository evidence.

**Quality gates: GREEN**

**Automated tests: 21/21 PASS**

**Repository state: CLEAN**

**Submission pack: COMPLETE**
