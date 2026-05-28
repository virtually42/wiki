---
id: kyo-module-kyo-flow
title: "kyo-flow — Durable Workflow Engine"
category: module
layer: application
tags: [workflow, durable, saga, compensation, persistence]
source_files:
  - /p/gh/kyo/kyo-flow/shared/src/main/scala/kyo/
source_commit: 9bab8d00
api_surface: [Workflow, Execution, Step]
related: [kyo-effect-async]
see_also: []
platforms: [jvm]
module_name: "kyo-flow"
dependencies: [kyo-core]
---

## Purpose

Durable workflow engine with persistence, compensation (saga pattern), and monitoring.

## Setup

```scala
libraryDependencies += "io.getkyo" %% "kyo-flow" % kyoVersion
```

## Key Concepts

- **Workflow** — definition of steps with inputs/outputs
- **Execution** — running instance of a workflow
- **Step** — individual unit of work (persisted)
- **Compensation** — saga-style rollback on failure

## Workflow Primitives

| Primitive | Purpose |
|-----------|---------|
| `outputs` | Produce results |
| `inputs` | Wait for external input |
| `steps` | Sequential work units |
| `sleep` | Durable timer (survives restart) |
| `dispatch` | Branching (fork workflow) |
| `foreach` | Iterate over collection |

## Composition

| Method | Purpose |
|--------|---------|
| `andThen` | Sequential composition |
| `zip` / `gather` | Parallel composition |
| `race` | First-to-complete wins |
| `retry` | Automatic retry on failure |
| `timeout` | Fail if too slow |

## Monitoring

- Status tracking per execution
- Event history
- Diagram rendering (Mermaid, Dot, BPMN, ELK, JSON)
- REST API: `/api/v1/workflows`, `/api/v1/executions`

## Integration Notes

- JVM-only (requires persistence backend)
- Steps are persisted — workflow resumes after restart
- Saga pattern via compensation for rollback
