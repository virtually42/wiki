---
id: postgresql
title: PostgreSQL
kind: descriptive
status: active
scope: global
created: 2026-05-15
updated: 2026-05-15
capabilities: [persistence, relational-queries, transactions, full-text-search, jsonb]
used_by:
  - projects/webapp
  - projects/infra
version: "16"
---

# PostgreSQL

## Overview

PostgreSQL is the primary relational database for multi-user server applications in this workspace. It is used when the application requires concurrent access, complex queries, transactions, or full-text search.

## Capabilities Served

- **persistence** — durable storage with ACID guarantees
- **relational-queries** — complex joins, aggregations, window functions
- **transactions** — multi-statement atomicity and isolation
- **full-text-search** — built-in text search without external dependencies
- **jsonb** — semi-structured data alongside relational data

## When To Prefer Over Alternatives

Prefer PostgreSQL when:
- Multiple users or services access the same data
- Complex queries (joins, aggregations) are needed
- Transactions span multiple tables
- Full-text search is required
- Data integrity constraints are important

Prefer SQLite when:
- Single-user local application
- Embedded database with zero configuration
- Read-heavy with simple queries
- No network access to a database server

## NixOS Configuration Notes

PostgreSQL is deployed as a NixOS service. See `projects/infra/` for the NixOS module configuration.

Key considerations:
- Use `services.postgresql.enable = true`
- Configure `pg_hba.conf` for local and network access
- Set up automated backups with `pgBackRest` or `pg_dump`
- Use `services.postgresql.settings` for tuning

## Operational Notes

- **Backup**: automated daily via pgBackRest, retention 7 days
- **Monitoring**: VictoriaMetrics postgres_exporter
- **Tuning**: shared_buffers, effective_cache_size, work_mem adjusted per workload
- **Migrations**: versioned SQL files, applied in order

## Known Issues

None currently tracked.

## Links

- [[tech/capabilities/persistence]] — capability description
- [[tech/stack/sqlite]] — alternative for local persistence
- [[tech/guides/postgresql-backup]] — backup guide
