---
id: effects-kyo
title: Use Kyo for effect management
kind: normative
status: accepted
scope: global
created: 2026-03-01
updated: 2026-05-15
applies_to:
  languages: [scala, scala-native]
  domains: [any]
  excludes: [shell-scripts, nix-modules]
used_by:
  - projects/compositor
  - projects/webapp
  - projects/cli-tool
sources:
  - sources/summaries/kyo-evaluation.md
supersedes: []
superseded_by: null
---

# Decision: Use Kyo for Effect Management

## Context

All Scala projects in this workspace need an effect management strategy. The options considered were:

- Direct style with no effect system
- Cats Effect / Typelevel stack
- ZIO
- Kyo

We need an approach that works across both Scala JVM and Scala Native targets, supports algebraic effects, integrates well with our functional programming style, and has manageable complexity.

## Decision

Use Kyo as the effect system for all Scala projects.

## Consequences

**Positive:**
- Algebraic effects provide composable, typed effect handling
- Works on both JVM and Native targets
- Lightweight compared to Cats Effect / ZIO
- Direct style syntax reduces ceremony
- Effect composition via `<` operator is expressive

**Negative:**
- Smaller ecosystem than Cats Effect or ZIO
- Fewer learning resources available
- Some library integrations require custom adapters
- Team must learn Kyo's approach to effects

## Alternatives Considered

### Cats Effect
Mature ecosystem, large community. Rejected because: heavy type-level encoding, monadic style adds syntactic overhead, weaker Scala Native story.

### ZIO
Full-featured, excellent documentation. Rejected because: opinionated runtime, heavy dependency tree, ZIO-specific ecosystem creates vendor lock-in feel.

### No effect system
Simpler code. Rejected because: makes error handling inconsistent across projects, loses composability, harder to test effectful code.

## Code Examples

Basic Kyo usage pattern:
```scala
import kyo.*

def fetchUser(id: UserId): User < (Abort[UserNotFound] & IO) =
  for
    row <- db.query(id)
    user <- row match
      case Some(r) => User.fromRow(r)
      case None    => Abort.fail(UserNotFound(id))
  yield user
```

## Links

- [[tech/stack/kyo]] — technology page
- [[tech/patterns/typed-errors]] — related pattern
- [[tech/capabilities/effects]] — capability description
