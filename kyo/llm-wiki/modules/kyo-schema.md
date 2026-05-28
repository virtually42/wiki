---
id: kyo-module-kyo-schema
title: "kyo-schema — Serialization, Lenses, Diffs"
category: module
layer: application
tags: [schema, json, protobuf, lenses, diffs, derivation]
source_files:
  - /p/gh/kyo/kyo-schema/shared/src/main/scala/kyo/
source_commit: 9bab8d00
api_surface: [Schema, Focus, Changeset, Validation]
related: []
see_also: []
platforms: [jvm, js, native]
module_name: "kyo-schema"
dependencies: []
---

## Purpose

JSON/Protobuf serialization without boilerplate. Also provides type-safe lenses (Focus), structural diffs (Changeset), and field validation. Works standalone (no Kyo runtime dependency).

## Setup

```scala
libraryDependencies += "io.getkyo" %% "kyo-schema" % kyoVersion
```

## Key APIs

### Schema Derivation

```scala
case class User(name: String, age: Int) derives Schema
// Auto-derives JSON encoding/decoding, protobuf, lenses, diffs
```

### Focus (Lenses)

```scala
val user = User("Alice", 30)
val updated = Focus[User].name.set("Bob")(user)
val nested = Focus[Company].ceo.name.get(company)
```

### Changeset (Diffs)

```scala
val old = User("Alice", 30)
val new_ = User("Alice", 31)
val diff: Changeset = Changeset.diff(old, new_)
```

### Validation

Compile-time field validation via Schema constraints.

## Integration Notes

- Standalone module — no dependency on kyo-core
- Works with kyo-http for automatic JSON request/response handling
- Schema[A] is the single derivation point for all features
