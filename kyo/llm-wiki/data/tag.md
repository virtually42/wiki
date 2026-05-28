---
id: kyo-data-tag
title: "Tag — Runtime Type Information"
category: data
layer: foundation
tags: [type-info, runtime, reification, generic]
source_files:
  - /p/gh/kyo/kyo-data/shared/src/main/scala/kyo/Tag.scala
source_commit: 9bab8d00
api_surface: [Tag, ConcreteTag, Frame]
related: [kyo-effect-env]
see_also: []
platforms: [jvm, js, native]
opaque: false
replaces: "ClassTag/TypeTag"
---

## What It Is

Runtime type info used by Kyo's effect system for handler dispatch. Usually auto-derived.

## When You Encounter It

As `using Tag[A]` in method signatures — rarely created manually.

## Key Types

| Type | Purpose |
|------|---------|
| `Tag[A]` | Runtime type representation |
| `Frame` | Source location (file, line, method) |

## `using` Clause Ordering

```scala
// Inline: Tag before Frame
inline def myEffect[A](using Tag[A], Frame): A < MyEffect = ...

// Non-inline: Frame before evidence
def handle[A](comp: A < MyEffect)(using Frame, Tag[A]): A < Any = ...

// AllowUnsafe always last
def unsafe[A](comp: A < Sync)(using AllowUnsafe): A = ...
```

## Gotchas

- Auto-derived — you rarely need to pass explicitly
- "no given instance of Tag[X]" → ensure type is concrete at call site
- Ordering: `Tag` → `Frame` → evidence → `AllowUnsafe`
