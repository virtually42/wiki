---
id: kyo-convention-naming
title: "Naming Conventions"
category: convention
layer: foundation
tags: [naming, api-design, verbs, operators]
source_files:
  - /p/gh/kyo/CONTRIBUTING.md
source_commit: 9bab8d00
api_surface: []
related: [kyo-convention-types]
see_also: []
platforms: [jvm, js, native]
---

## Rule

Use action verbs, not category theory terms. No symbolic operators in core modules.

## Rationale

Names should describe what the method does, not what algebraic structure it belongs to.

## Examples

### Do

| Method | Why |
|--------|-----|
| `foreach` | Describes the action |
| `collectAll` | Says what it does |
| `get` | Clear extraction |
| `run` | Handles the effect |
| `init` | Creates an instance |

### Don't

| Method | Why not |
|--------|---------|
| `traverse` | Category theory term |
| `sequence` | Vague |
| `pure` | Algebraic concept |
| `>>=` | Symbolic, obscure |
| `*>` | Only in kyo-combinators (not core) |

## Effect Operation Prefixes

| Prefix | Purpose | Example |
|--------|---------|---------|
| `init*` | Create instance | `Fiber.init`, `Channel.init` |
| `get*` | Extract value, introducing effect | `Abort.get(either)`, `Env.get[R]` |
| `run*` | Handle effect, removing it | `Abort.run(comp)`, `Var.run(init)(comp)` |

## Exceptions

- `kyo-combinators` module provides ZIO-style symbolic operators (`*>`, `<*>`, `<&>`, etc.)
- These are opt-in via separate import, not part of core
