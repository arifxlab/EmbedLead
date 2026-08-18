# BUILDLOG - EmbedLead

## Project

**EmbedLead Embeddable Widget & Lead-Capture Platform**
FlyRank Internship · Backend Track · Capstone

---

## Development Approach

EmbedLead was developed incrementally around the capstone's production-oriented
requirements rather than building the entire application in one step.

The implementation was validated continuously with:

- automated tests
- Ruff
- strict mypy
- PostgreSQL verification
- Redis health checks
- HTTP endpoint checks
- browser-based second-origin testing
- direct database verification

The project was developed locally using Python, FastAPI, PostgreSQL, Redis,
Alembic, SQLAlchemy, Celery, and a plain JavaScript browser widget.

---

## AI Assistance

AI tools were used as an engineering assistant throughout development.

AI assistance was used for:

- architecture discussion
- API design review
- implementation suggestions
- debugging
- test design
- error analysis
- documentation structure
- command sequencing
- reviewing edge cases
- identifying missing capstone evidence
- preparing verification procedures

AI-generated suggestions were not treated as automatically correct.

Implementation was repeatedly checked against the actual repository, runtime
behavior, tests, database state, and capstone requirements.

---

## Important AI-Assisted Debugging

### Widget Delivery Path Issue

During final integration testing, the widget endpoint initially calculated the
widget directory using an incorrect filesystem parent:

```python
#WIDGET_DIR = Path(__file__).resolve().parents[2] / "widget"
```

The actual repository layout required:

```python
#WIDGET_DIR = Path(__file__).resolve().parents[3] / "widget"
```

The problem was discovered through actual runtime verification rather than being
assumed correct from the implementation.

The repository was inspected and the expected widget directory was initially
missing.

The final implementation restored the correct path and added the actual:

```
widget/widget.v1.js
```

bundle.

The result was then verified through the real embed endpoint and the
second-origin browser demo.

This was an important example of why generated code must be tested against the
real project structure.

---

## Widget Implementation

The final widget bundle was implemented as a self-contained browser script.

The script:

- Detects the current `<script>` element.
- Reads the public widget key from the script URL.
- Determines the API origin from the script URL.
- Loads public widget configuration.
- Creates the widget UI.
- Renders the form.
- Submits lead data using `fetch`.
- Includes the honeypot field.
- Displays submission status.
- Handles API failures without crashing the host page.

The widget is delivered as:

```
/api/v1/widget.v1.js
```

and is embedded using a one-line script tag containing the widget's public key.

---

## Cross-Origin Debugging

The capstone specifically requires the widget to work on a website hosted from
a different origin.

The final verification used:

```
API:
http://127.0.0.1:8000

Customer website:
http://127.0.0.1:5500
```

The different ports make these different browser origins.

The customer page loads the EmbedLead widget from the API origin.

The browser was used to verify that the widget renders and that a lead can be
submitted successfully across origins.

---

## Security / Abuse Testing

The public submission path was deliberately tested against failure cases.

Verified cases include:

- invalid email
- oversized payload
- inactive widget
- rate-limit burst
- honeypot submission
- unauthorized dashboard access
- cross-tenant access
- invalid public widget state

The objective was not simply to make the happy path work, but to verify that
untrusted public traffic is rejected safely.

---

## Tenant Isolation

Tenant isolation was treated as a security boundary rather than a UI feature.

The implementation scopes owner-facing operations to the authenticated tenant.

Integration tests verify that:

- Tenant A cannot access Tenant B's widgets.
- Tenant A cannot access Tenant B's submissions.
- Analytics remain tenant-scoped.
- Public widget keys resolve only to their associated widget.

---

## Geo Enrichment

The lead pipeline supports IP-based geographic enrichment.

The design uses a provider fallback chain:

```text
Provider A
    â†“ failure
Provider B
    â†“ failure
Store submission without geo data
```

Automated tests mock the providers so the fallback behavior is deterministic.

This avoids depending on real internet services during tests.

The important behavior is graceful degradation:

Geo enrichment is useful, but it is not allowed to become a reason for losing
a valid lead.

---

## Safe Side Effects

Notification work is treated as non-critical side-effect processing.

The lead persistence path must remain successful even when notification work
fails.

An integration test explicitly verifies that a lead remains persisted when the
notification side effect raises an exception.

This follows the capstone requirement:

> Non-critical failures must never break the main path.

---

## Testing Milestone

Final automated test run:

```text
21 passed in 8.25s
```

The suite includes integration and unit tests covering:

- public lead submission
- cached widget configuration
- authentication
- inactive widgets
- invalid email
- oversized payloads
- rate limiting
- tenant isolation
- versioned widget delivery
- widget public keys
- pagination
- honeypot spam prevention
- notification failure
- analytics
- analytics tenant isolation
- configuration
- CORS configuration
- payload limits
- geo provider fallback

---

## Static Analysis Milestone

Ruff:

```bash
ruff check .
```
```text
All checks passed!
```

Mypy:

```bash
mypy app
```
```text
Success: no issues found in 50 source files
```

These checks were run after the final widget implementation was restored.

---

## Database Verification

The final lead persistence path was verified directly against PostgreSQL.

A real cross-origin evidence submission was stored with:

```
email:
evidence@example.com

name:
EmbedLead Evidence User

message:
Cross-origin widget submission evidence
```

The resulting database row confirmed that the submission was associated with
the expected widget.

This provided independent evidence that the browser submission reached the
backend and was persisted.

---

## Evidence Collection

Final evidence was collected after the implementation was stable.

Evidence includes screenshots covering the important behavioral paths rather
than relying only on source code claims.

The evidence document maps the Definition-of-Done requirements to concrete
proof.

The final evidence set was intentionally captured from clean successful runs
so the submission materials do not depend on screenshots containing unrelated
debugging failures.

---

## Documentation

The required submission-pack files were prepared in the repository root:

- `README.md`
- `capstone.yaml`
- `EVIDENCE.md`
- `BUILDLOG.md`
- `.env.example`

The README documents:

- project purpose
- architecture
- technology stack
- setup
- API surface
- widget integration
- testing
- security
- resilience
- limitations
- demo flow

---

## Lessons Learned

### 1. Public APIs are fundamentally different

An authenticated internal API can make stronger assumptions about its callers.

An embeddable public API cannot.

The browser and the visitor must be treated as untrusted inputs.

### 2. Runtime verification beats assumptions

The widget path issue demonstrated that code can look structurally correct
while still failing because the actual filesystem layout differs from the
assumption.

The fix was verified by running the real endpoint and browser integration.

### 3. Failure handling belongs at dependency boundaries

Geo providers and notification systems are secondary dependencies.

Their failure should be isolated so that the primary lead persistence path
continues to work.

### 4. Evidence is part of the engineering work

The capstone does not only ask whether features exist.

It asks for proof.

For that reason, final verification was performed separately from development
and evidence was captured from successful runs.

---

## Final State

The final repository has:

- working FastAPI backend
- PostgreSQL persistence
- Redis infrastructure
- Celery infrastructure
- authenticated tenant APIs
- tenant isolation
- public widget API
- versioned JavaScript widget
- second-origin demo page
- public lead submission
- CORS
- validation
- rate limiting
- honeypot protection
- geo fallback
- safe side effects
- analytics
- migrations
- automated tests
- Ruff validation
- strict mypy validation
- required documentation
- final evidence

Final automated verification:

```text
21 passed
ruff: All checks passed
mypy: Success: no issues found in 50 source files
```

---

## Final Reflection

The most important engineering lesson from EmbedLead was learning to treat
external browser traffic and third-party dependencies as unreliable by default.

The application therefore separates:

```text
request validation
        â†“
security / abuse protection
        â†“
enrichment
        â†“
persistence
        â†“
non-critical side effects
```

This keeps the primary business operation resilient even when individual
dependencies fail.

The project is intentionally scoped as a backend-focused capstone rather than
a production SaaS product. The goal was to demonstrate correctness, security,
resilience, testing, and engineering judgment.