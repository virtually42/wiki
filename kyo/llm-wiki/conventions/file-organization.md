---
id: kyo-convention-file-organization
title: "File Organization"
category: convention
layer: foundation
tags: [file-structure, ordering, documentation, code-style]
source_files:
  - /p/gh/kyo/CONTRIBUTING.md
source_commit: 9bab8d00
api_surface: []
related: [kyo-convention-naming]
see_also: []
platforms: [jvm, js, native]
---

## Rule

Source files are documentation — they should read top-to-bottom as a narrative.

## Ordering Rules

1. Most-used APIs first (factories before config, simple before complex)
2. Public before private
3. Companion object below class/trait
4. Imports at top, no wildcard imports from Kyo internals

## Code Style

| Do | Don't |
|----|-------|
| Composition over inheritance | `protected`, deep hierarchies |
| `private[kyo]` for cross-package | `@uncheckedVariance` |
| Overloads delegate to canonical | Duplicate logic across overloads |
| `Scope`-managed resources (`init`) | Unmanaged by default (`initUnscoped`) |
| Explicit return types on public APIs | Inferred public return types |
| Scaladoc (8-35 lines) on public types | Missing or excessive documentation |

## Module Source Layout

```
kyo-<module>/
  shared/src/main/scala/kyo/    # Cross-platform
  shared/src/test/scala/kyo/    # Shared tests
  jvm/src/main/scala/kyo/       # JVM-specific
  js/src/main/scala/kyo/        # JS-specific
  native/src/main/scala/kyo/    # Native-specific
```

## Exceptions

- Performance-critical inner code may deviate from top-to-bottom ordering
- Private utilities can be grouped by concern rather than visibility
