---
id: kyo-pattern-dependency-injection
title: "Dependency Injection Patterns"
category: pattern
layer: core
tags: [dependency-injection, env, layer, testing, wiring]
source_files: []
source_commit: 9bab8d00
api_surface: [Env.get, Env.run, Env.runLayer, Layer, Layer.init, Layer.from]
related: [kyo-effect-env]
see_also: [kyo-pattern-testing]
platforms: [jvm, js, native]
when_to_use: "Services with dependencies, testable code, configuration injection"
when_not_to_use: "Simple values that don't change (use constants or Local)"
---

## Problem

How to wire dependencies without hardcoding implementations.

## Solution

### Interface + Env.get

```scala
trait UserRepo:
    def find(id: Int): Maybe[User] < Sync

trait EmailService:
    def send(to: String, body: String): Unit < Sync

def notifyUser(id: Int): Unit < (Env[UserRepo] & Env[EmailService] & Sync) =
    for
        repo  <- Env.get[UserRepo]
        email <- Env.get[EmailService]
        user  <- repo.find(id)
        _     <- user.map(u => email.send(u.email, "Hello!")).getOrElse(())
    yield ()
```

### Layer composition

```scala
val repoLayer: Layer[UserRepo, Sync] = Layer {
    new UserRepo:
        def find(id: Int) = Sync.defer(db.query(id))
}

val emailLayer: Layer[EmailService, Any] = Layer {
    new EmailService:
        def send(to: String, body: String) = Sync.defer(smtp.send(to, body))
}

// Compose
val appLayer = Layer.init[UserRepo & EmailService](repoLayer, emailLayer)

// Wire
val result: Unit < (Sync & Memo) = Env.runLayer(appLayer)(notifyUser(42))
val final_result: Unit < Sync = Memo.run(result)
```

### Layer with dependencies (Layer.from)

```scala
val serviceLayer: Layer[UserService, Env[UserRepo] & Sync] =
    Layer.from { (repo: UserRepo) =>
        new UserService:
            def getUser(id: Int) = repo.find(id)
    }

// Chain: repo provides input to service
val wired: Layer[UserService, Sync] = repoLayer.to(serviceLayer)
```

### Testing with Env

```scala
// In tests: provide mock directly
val mockRepo = new UserRepo:
    def find(id: Int) = Maybe(User(id, "test@test.com"))

val testResult = Env.run(mockRepo)(Env.run(mockEmail)(notifyUser(1)))
```

## Trade-offs

- `Env.runLayer` adds `Memo` effect (single-init guarantee) — needs `Memo.run`
- Layer composition is type-checked at compile time
- `Env.run` for simple cases, `Env.runLayer` for complex graphs

## Related Patterns

- [testing](testing.md) — mock injection for tests
