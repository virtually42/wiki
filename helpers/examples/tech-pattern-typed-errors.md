---
id: typed-error-boundaries
title: Typed error boundaries at module edges
kind: normative
status: accepted
scope: global
created: 2026-04-01
updated: 2026-05-15
applies_to:
  languages: [scala]
  domains: [any]
promoted_from:
  - projects/compositor/syntheses/error-handling.md
  - projects/webapp/adr/003-typed-errors.md
promotion_reason: Consistent successful use across 3 projects
promoted_at: 2026-04-15
sources:
  - sources/summaries/error-handling-research.md
---

# Pattern: Typed Error Boundaries at Module Edges

## Problem

Without explicit error boundaries, errors propagate unpredictably across module boundaries. Callers don't know what can fail. Error handling becomes ad-hoc — some modules throw exceptions, others return Option, others use Either with unstructured messages.

## Solution

Define a sealed error ADT at each module boundary. Use Kyo's `Abort` effect to make errors part of the type signature. Convert infrastructure exceptions to domain errors at the boundary.

## Structure

```
Module boundary (public API)
  |
  +-- Domain error ADT (sealed trait)
  |     +-- NotFound
  |     +-- InvalidInput
  |     +-- Conflict
  |
  +-- Public methods return: Result < (Abort[DomainError] & ...)
  |
  +-- Internal implementation may use different error types
  |     (infrastructure exceptions, library errors)
  |
  +-- Boundary converts internal errors to domain errors
```

## Code Example

```scala
import kyo.*

// Domain error ADT at module boundary
enum UserError:
  case NotFound(id: UserId)
  case InvalidEmail(email: String)
  case AlreadyExists(email: String)

// Public module API — errors are typed
trait UserService:
  def find(id: UserId): User < (Abort[UserError] & IO)
  def create(cmd: CreateUser): User < (Abort[UserError] & IO)

// Implementation converts infrastructure errors at boundary
class UserServiceImpl(repo: UserRepo) extends UserService:
  def find(id: UserId): User < (Abort[UserError] & IO) =
    repo.findById(id).map:
      case Some(user) => user
      case None       => Abort.fail(UserError.NotFound(id))

  def create(cmd: CreateUser): User < (Abort[UserError] & IO) =
    for
      _    <- validateEmail(cmd.email)
      existing <- repo.findByEmail(cmd.email)
      _    <- existing match
        case Some(_) => Abort.fail(UserError.AlreadyExists(cmd.email))
        case None    => ()
      user <- repo.insert(User.from(cmd))
    yield user
```

## When To Use

- At every module boundary (service, repository, adapter)
- When a module is consumed by other modules or external callers
- When error types should be part of the API contract

## When Not To Use

- Inside a module's private implementation (use whatever is convenient)
- For truly exceptional conditions that indicate bugs (use exceptions/panics)
- For trivial functions where Option suffices

## Related Patterns

- [[tech/patterns/functional-core-imperative-shell]] — errors flow outward from pure core
- [[tech/decisions/effects-kyo]] — the effect system providing Abort
- [[tech/patterns/anti/stringly-typed-errors]] — what NOT to do
