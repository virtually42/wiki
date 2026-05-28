---
id: kyo-data-record
title: "Record — Structural Subtyping"
category: data
layer: foundation
tags: [structural-typing, record, intersection-types, dynamic]
source_files:
  - /p/gh/kyo/kyo-data/shared/src/main/scala/kyo/Record.scala
source_commit: 9bab8d00
api_surface: [Record, Record.empty, Field, Fields, ~]
related: [kyo-data-tag]
see_also: []
platforms: [jvm, js, native]
opaque: false
replaces: ""
---

## What It Is

Type-safe heterogeneous record with structural subtyping via intersection types.

## Key APIs

```scala
// Define type
type Person = Record["name" ~ String & "age" ~ Int]

// Create
val person = Record("name" ~ "Alice" & "age" ~ 30)

// Access
person("name")  // "Alice"

// Extend
val extended = person & ("email" ~ "alice@ex.com")
```

| Method | Purpose |
|--------|---------|
| `Record(fields)` | Create from field intersections |
| `record("key")` | Get field value |
| `record & ("k" ~ v)` | Add/update field |
| `record.update("k")(f)` | Transform field |
| `record.fields` / `.values` | Introspect |

## Performance

- Flat representation for ≤8 fields
- HashMap for >8 fields
- Less common than case classes — use for dynamic schemas

## Gotchas

- Uses `selectDynamic` — IDE support may be limited
- Field names are string literals at type level
