# API & Ingestion Layer
Handles endpoint routing configuration and validation schemas:
- routes.py: Explicit network routing entries for multipart audio payloads and video handoffs.
- schemas.py: Pydantic models acting as strict input/output verification contracts.
- dependencies.py: Global rate-limiting injectors and environment protectors.