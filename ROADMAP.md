# Project Roadmap

This document outlines planned technical milestones and architecture enhancements for `stock-fetcher`. Milestones reflect active engineering priorities.

---

## Table of Contents

- [v0.3.0: Performance and Async Architecture](#v030-performance-and-async-architecture)
- [v0.4.0: Provider Coverage and Resiliency](#v040-provider-coverage-and-resiliency)
- [v1.0.0: Production Hardening](#v100-production-hardening)

---

## v0.3.0: Performance and Async Architecture

- **Asynchronous Client Support**: Implement non-blocking HTTP fetching across all clients using `httpx` to enable concurrent multi-provider queries.
- **Configurable Response Caching**: Add an optional in-memory and disk cache layer respecting upstream `Cache-Control` headers and TTL settings.
- **Structured Pydantic Response Models**: Migrate raw dictionary returns to validated Pydantic models for explicit schema guarantees and editor autocomplete.

---

## v0.4.0: Provider Coverage and Resiliency

- **Extended Provider Ecosystem**: Add client integrations for Wikimedia Commons and Openverse.
- **Deterministic Pagination Cursors**: Normalize page and offset cursors across heterogeneous provider interfaces.
- **Adaptive Rate Limit Handling**: Implement exponential backoff and rate limit header parsing (`X-Ratelimit-Remaining`) to prevent burst throttling.

---

## v1.0.0: Production Hardening

- **Full Type Completeness**: Enforce strict `mypy` typing across all internal and public modules.
- **End-to-End Test Suite**: Complete unit and integration test coverage using VCR.py for recorded network fixtures.
- **Stable Public API**: Freeze core fetcher interfaces and deprecate legacy dictionary response shapes.
