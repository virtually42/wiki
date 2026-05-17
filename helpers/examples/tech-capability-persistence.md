---
id: persistence
title: Data Persistence
kind: descriptive
status: active
scope: global
created: 2026-05-15
updated: 2026-05-15
implementations:
  - tech: postgresql
    projects: [webapp, infra]
  - tech: sqlite
    projects: [cli-tool]
---

# Capability: Data Persistence

## What This Capability Is

Durable storage of application data that survives process restarts. Covers structured data (relational), semi-structured (JSON/JSONB), and configuration state.

## Requirements

All persistence implementations must provide:

- **Durability** — data survives process restart and host reboot
- **Consistency** — reads after writes return the written data
- **Schema management** — versioned migrations or equivalent
- **Backup story** — documented backup and recovery procedure
- **Testability** — tests can run against a real or equivalent instance

## Implementations Across Projects

### PostgreSQL (webapp, infra)

Used for multi-user server applications where concurrent access, complex queries, and transactions are required.

- [[tech/stack/postgresql]] — technology page
- [[projects/webapp/adr/002-persistence-postgresql]] — project decision
- Backup: pgBackRest, daily automated
- Migrations: versioned SQL files in `db/migrations/`

### SQLite (cli-tool)

Used for single-user local applications with simple query needs and zero-configuration deployment.

- [[tech/stack/sqlite]] — technology page
- [[projects/cli-tool/adr/001-persistence-sqlite]] — project decision
- Backup: file copy (single-file database)
- Migrations: embedded in application startup

## Comparison

| Aspect           | PostgreSQL             | SQLite                    |
|------------------|------------------------|---------------------------|
| Concurrency      | Multi-user, MVCC       | Single-writer             |
| Deployment       | Separate service       | Embedded, zero-config     |
| Queries          | Full SQL, extensions   | Standard SQL              |
| NixOS            | `services.postgresql`  | Library dependency        |
| Operational cost | Medium (backups, tuning)| Low (file copy)          |

## Recommendations

- Default to **PostgreSQL** for server applications
- Default to **SQLite** for CLI tools and local-only applications
- Consider **DuckDB** for analytical workloads (not yet used)
- Document the choice as a project ADR with capability reference
