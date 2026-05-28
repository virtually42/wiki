---
id: kyo-module-kyo-caliban
title: "kyo-caliban — GraphQL Server"
category: module
layer: integration
tags: [graphql, caliban, schema-derivation, server]
source_files:
  - /p/gh/kyo/kyo-caliban/jvm/src/main/scala/kyo/
source_commit: 9bab8d00
api_surface: [CalibanKyo, KyoInterpreter]
related: [kyo-module-kyo-http]
see_also: []
platforms: [jvm]
module_name: "kyo-caliban"
dependencies: [kyo-core]
---

## Purpose

GraphQL server using Caliban with Kyo effect integration and automatic schema derivation.

## Setup

```scala
libraryDependencies += "io.getkyo" %% "kyo-caliban" % kyoVersion
```

## Key Concepts

- Caliban derives GraphQL schema from Scala case classes
- Kyo effects integrate with resolver functions
- Schema served via kyo-http server

## Integration Notes

- JVM-only (Caliban dependency)
- Schema derivation via Caliban's macro-based approach
- Resolvers return `A < S` (Kyo computations)
- WebSocket subscriptions supported
