# Docu Meter API Launch Kit

## One-line positioning

Open-source API auth, quota, rate limiting, and usage metering starter kit for AI/API SaaS products.

## Short description

Docu Meter API is a production-style FastAPI + Next.js platform layer for API products: HMAC-secured API keys, Redis rate limits, monthly project quotas, Postgres usage metering, and a developer dashboard for API key management and usage visibility.

## Who it is for

- Developers building AI/API SaaS products
- Backend engineers who need API key auth and usage tracking
- Founders prototyping metered APIs before billing integration
- Recruiters/evaluators looking for backend/platform engineering proof

## Key proof points

- API keys are shown once and stored only as HMAC-SHA-256 digests with a server-side pepper
- Redis rate limiting blocks abusive traffic before expensive LLM/service work
- Postgres stores durable projects, keys, usage events, and quota counters
- Next.js dashboard supports project visibility, API key creation, masked key display, and revocation
- Docker Compose boots the full stack with API, web, Postgres, and Redis

## GitHub repo blurb

I built Docu Meter API as an open-source starter for AI/API products that need the boring-but-critical platform layer: API keys, rate limits, quotas, usage metering, and dashboard visibility.

Repo: https://github.com/Oussamcsc/docu-meter-api

Feedback welcome — especially from anyone building metered APIs, AI tools, or SaaS infrastructure.

## LinkedIn post draft

I’ve been building a production-style API platform project: **Docu Meter API**.

The idea is simple: most API demos stop at “here is an endpoint,” but real API products need the platform layer around it:

- API key creation and revocation
- Secure secret storage
- Rate limits before expensive work runs
- Monthly project quotas
- Usage metering
- Dashboard visibility for developers

So I built a FastAPI + Next.js + Postgres + Redis stack that gives any service a reusable request ladder:

`API key identity → Redis rate limit → project quota → service execution → Postgres usage metrics`

The default protected service is an LLM-powered document analyzer, but the platform can support any backend service that needs auth + metering.

Repo: https://github.com/Oussamcsc/docu-meter-api

Would appreciate feedback from backend/API/SaaS builders.

## Reddit / community post draft

Title: I built an open-source API metering/auth starter kit for AI/API SaaS products

Body:

I built **Docu Meter API**, a FastAPI + Next.js starter for the API platform layer that most demos skip:

- API key auth
- HMAC-secured key storage
- Redis rate limiting
- monthly project quotas
- Postgres usage metering
- dashboard for API keys and usage
- Docker Compose full-stack setup

The default example service is an LLM document analyzer, but the auth/metering layer is generic and can wrap other services.

Repo: https://github.com/Oussamcsc/docu-meter-api

I’m looking for feedback on the architecture and what would make this more useful as a starter kit for API/SaaS builders.

## Show HN draft

Title: Show HN: Docu Meter API – auth, quotas, and metering starter for API SaaS

Body:

Hi HN — I built Docu Meter API, an open-source starter for the platform layer around API products.

It includes FastAPI, Next.js, Postgres, Redis, Docker Compose, HMAC-secured API keys, Redis rate limits, monthly project quotas, usage metering, and a developer dashboard for key management.

The default service is an LLM document analyzer, but the core pattern is generic: wrap any backend service with API key identity, safety checks, and usage tracking.

Repo: https://github.com/Oussamcsc/docu-meter-api

I’d appreciate feedback on the architecture and what would make it more useful for developers building metered APIs.

## X / Twitter thread draft

1/ I built Docu Meter API: an open-source starter for API auth, quotas, rate limits, and usage metering.

2/ Most API demos stop at an endpoint. Real API products need the platform layer: keys, quotas, metering, and a dashboard.

3/ Stack: FastAPI, Next.js, Postgres, Redis, Docker Compose.

4/ Request ladder: API key → Redis rate limit → project quota → service execution → Postgres usage metrics.

5/ API keys are shown once and stored as HMAC-SHA-256 digests with a server-side pepper — raw keys are never stored.

6/ The first protected service is an LLM document analyzer, but the platform can wrap any backend service.

7/ Repo: https://github.com/Oussamcsc/docu-meter-api

Feedback welcome from backend/API/SaaS builders.

## Outreach comment template

This is useful. I’ve been working on a related open-source API platform starter focused on API keys, Redis rate limits, quotas, and usage metering for AI/API products. If you’re open to it, I’d appreciate architecture feedback: https://github.com/Oussamcsc/docu-meter-api

## Next assets to create

- Dashboard screenshot
- API docs screenshot
- Architecture diagram image
- 60-second demo GIF/video
- GitHub issues labeled `good first issue`
