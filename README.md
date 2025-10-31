# README.md - Deployment & Testing Guide

## Overview
This project is a scalable AI assistant for Achareh using FastAPI with WebSocket for chat, semantic matching with a Persian-optimized embedding model, and SQLite for storage. No paid APIs used. Mocks for pricing/orders; in production, integrate Achareh APIs via requests.

## Features
- Natural language service detection in Persian using semantic similarity.
- City-based availability check.
- Pricing display (mocked).
- Order tracking (mocked).
- Conversation storage in DB.
- Minimal RTL-supported HTML/JS UI.
- Error handling.

## Deployment
1. Build: `docker build -t achareh-ai .`
2. Run: `docker run -p 8000:8000 achareh-ai`
3. Access: http://localhost:8000

## Testing
- Browser to http://localhost:8000
- Enter city code (e.g., 333).
- Query service (e.g., "نظافت منزل").
- Track orders: "پیگیری سفارش"

## Scalability
- Async FastAPI for concurrency.
- SQLite for test; scale to PostgreSQL.
- Embedding model local and efficient.
- Avoided over-engineering: Simple WS state.

## Notes
- Pinned versions in requirements.txt to resolve compatibility issues with transformers and torch.
- Explicitly added transformers to requirements.
- For real APIs, inspect https://achareh.co for endpoints (e.g., /api/services).
- Add auth for user_id.
- If issues persist, check container logs for version conflicts.