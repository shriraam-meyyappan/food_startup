# Project documentation

Current Python backend documentation is in [database setup](../backend/docs/database-setup.md)
and [progress](../backend/PROGRESS.md). The original notes below describe the
legacy NestJS/Prisma scaffold retained in services/api.

This repository currently contains development scaffolding only. There are no
business models, authentication flows, payments, ordering, or subscription logic.

- Each app owns its dependencies and runs independently.
- The web and mobile entry points intentionally render nothing.
- `GET /api/v1/health` is a process liveness endpoint. It does not check PostgreSQL.
- Prisma is configured for PostgreSQL, with no business models or migrations yet.
  Generate the client after schema changes; add a PostgreSQL driver adapter when
  wiring Prisma Client into backend features.
- The `com.example` Android application ID is a development placeholder. Select
  an owned application ID before distributing the mobile app.

See `../README.md` for local development instructions.
