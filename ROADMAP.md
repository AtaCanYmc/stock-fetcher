# Project Roadmap

This document outlines planned technical milestones and architecture enhancements for `stock-fetcher`. Milestones reflect active engineering priorities.

---

## Table of Contents

- [v0.3.0: Performance and Async Architecture](#v030-performance-and-async-architecture)
- [v0.4.0: Provider Coverage and Resiliency](#v040-provider-coverage-and-resiliency)
- [v1.0.0: Production Hardening](#v100-production-hardening)

---

## v0.3.0: Performance and Async Architecture (Completed)

- [x] **Asynchronous Client Support**: Implemented non-blocking HTTP fetching across all clients using `httpx` and `ClientFactory.asearch_all` for concurrent multi-provider queries.
- [x] **Configurable Response Caching**: Added thread-safe `MemoryCache` and persistent `DiskCache` layers respecting upstream `Cache-Control` headers and TTL settings.
- [x] **Structured Pydantic Response Models**: Replaced raw dictionaries with validated `StockImage` Pydantic models supporting both attribute access and backwards-compatible subscript indexing.

---

## v0.4.0: Provider Coverage and Resiliency (Completed)

- [x] **Extended Provider Ecosystem**: Added client integrations for Wikimedia Commons (MediaWiki API) and Openverse (WordPress Openverse API) supporting async streaming, caching, and open-access queries.
- [x] **Deterministic Pagination Cursors**: Standardized page and offset cursor normalization (`encode_cursor`, `decode_cursor`, `PaginatedResult`) across Pexels, Pixabay, Unsplash, Openverse, Wikimedia (`gsroffset`), and Flickr.
- [x] **Adaptive Rate Limit Handling**: Added case-insensitive header parsing (`X-Ratelimit-Remaining`, `Retry-After`), proactive adaptive pacing before exhaustion, and exponential backoff retry on HTTP 429 status codes.

---

## v1.0.0: Production Hardening

- **Full Type Completeness**: Enforce strict `mypy` typing across all internal and public modules.
- **End-to-End Test Suite**: Complete unit and integration test coverage using VCR.py for recorded network fixtures.
- **Stable Public API**: Freeze core fetcher interfaces and deprecate legacy dictionary response shapes.
