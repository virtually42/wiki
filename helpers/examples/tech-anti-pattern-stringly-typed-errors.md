---
id: stringly-typed-errors
title: Do not use string-based error messages as error types
kind: normative
status: rejected
created: 2026-04-15
applies_to:
  languages: [scala]
  domains: [any]
reasons:
  - Callers cannot pattern match on string messages
  - Error messages are not stable API — they change without warning
  - No exhaustiveness checking by the compiler
  - Internationalization becomes impossible
  - Testing must rely on fragile string comparisons
alternatives:
  - tech/patterns/typed-errors.md
---

# Anti-Pattern: Stringly-Typed Errors

## What This Is

Using `String` or `Exception` with message strings as the primary error representation at module boundaries.

Examples of the anti-pattern:

```scala
// BAD: String-based errors
def findUser(id: UserId): Either[String, User]

// BAD: Generic exception with message
def findUser(id: UserId): User =
  throw new RuntimeException(s"User $id not found")

// BAD: Untyped Abort
def findUser(id: UserId): User < Abort[String]
```

## Why It Is Rejected

1. **No pattern matching.** Callers cannot reliably distinguish between "not found" and "invalid input" without parsing strings.
2. **No compiler help.** When a new error case is added, callers are not warned.
3. **Fragile tests.** Tests that assert on error messages break when messages are reworded.
4. **Breaks composition.** String errors from different modules cannot be meaningfully combined.

## What To Do Instead

Use sealed error ADTs with Kyo's `Abort` effect:

```scala
// GOOD: Typed error ADT
enum UserError:
  case NotFound(id: UserId)
  case InvalidEmail(email: String)
  case AlreadyExists(email: String)

def findUser(id: UserId): User < (Abort[UserError] & IO)
```

See [[tech/patterns/typed-errors]] for the full pattern.

## References

- [[tech/patterns/typed-errors]]
- [[tech/decisions/effects-kyo]]
