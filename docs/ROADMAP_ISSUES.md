# Docu Meter API Roadmap Issues

Use these as GitHub issues to make the project easier to evaluate, contribute to, and discuss.

## Good first issues

### 1. Add dashboard screenshots to README

**Label:** `good first issue`, `documentation`

Add screenshots for:

- Project dashboard
- API key creation flow
- Masked key display / revoke action
- API docs page

Acceptance criteria:

- Images live under `docs/assets/`
- README includes a short "Screenshots" section
- Image alt text explains what each screenshot shows

---

### 2. Add curl examples for protected API calls

**Label:** `good first issue`, `documentation`, `api`

Add copy-paste examples for calling:

- `POST /v1/documents/process`
- `GET /health`
- API key creation endpoint for local admin/dev flow

Acceptance criteria:

- Examples use placeholder tokens only
- README has a short "API examples" section
- Examples work against `docker compose up --build`

---

### 3. Improve error response examples

**Label:** `good first issue`, `api`, `documentation`

Document common failure responses:

- Invalid API key
- Revoked API key
- Rate limit exceeded
- Monthly quota exceeded
- Payload too large

Acceptance criteria:

- README or docs include sample status codes and response bodies
- No real secrets or project IDs are included

---

## Core roadmap

### 4. Add Stripe billing plan integration

**Label:** `enhancement`, `billing`, `platform`

Connect project quotas to Stripe subscription plans.

Acceptance criteria:

- Plan model maps to quota limits
- Webhook handler updates organization/project entitlement state
- Tests cover subscription create/update/cancel events

---

### 5. Add OpenAPI examples and response schemas

**Label:** `enhancement`, `api`, `documentation`

Improve FastAPI/OpenAPI docs with richer examples for request and response bodies.

Acceptance criteria:

- Protected endpoints include example payloads
- Common errors include documented response models
- `/docs` becomes useful for first-time evaluators

---

### 6. Add usage analytics charts

**Label:** `enhancement`, `frontend`, `analytics`

Extend the dashboard with usage charts by day, endpoint, and status code.

Acceptance criteria:

- Dashboard shows usage over time
- Failed vs successful requests are visible
- Empty states are clean and recruiter-friendly

---

### 7. Add CI workflow

**Label:** `enhancement`, `ci`, `quality`

Add GitHub Actions for backend and frontend checks.

Acceptance criteria:

- Backend runs ruff and pytest
- Frontend runs lint and build
- Workflow is documented in README badge or docs

---

### 8. Add SDK/client example

**Label:** `enhancement`, `developer-experience`

Create a small Python or TypeScript client example for the protected API.

Acceptance criteria:

- Example accepts an API key from env var
- Example calls document processing endpoint
- README links to the example

---

## Launch assets

### 9. Add architecture diagram image

**Label:** `documentation`, `architecture`

Create a visual architecture diagram for:

`Client → API key auth → Redis rate limit → quota check → service → usage metering → dashboard`

Acceptance criteria:

- Diagram lives under `docs/assets/`
- README includes the image
- Text version remains accessible for screen readers

---

### 10. Record a 60-second demo GIF/video

**Label:** `documentation`, `demo`

Record the project flow:

1. Start stack
2. Open dashboard
3. Create API key
4. Call protected document endpoint
5. See usage update

Acceptance criteria:

- Demo is short and clear
- README links to it
- No real secrets are visible
