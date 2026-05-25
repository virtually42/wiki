---
id: kyo-module-kyo-actor
title: "kyo-actor — Type-Safe Actor System"
category: module
layer: application
tags: [actors, supervision, messaging, concurrency]
source_files:
  - kyo-actor/shared/src/main/scala/kyo/
source_commit: 9bab8d00
api_surface: [Actor, ActorRef, Supervisor]
related: [kyo-effect-async, kyo-effect-channel]
see_also: [kyo-pattern-concurrency]
platforms: [jvm, js, native]
module_name: "kyo-actor"
dependencies: [kyo-core]
---

## Purpose

Type-safe actor system with supervision and typed messaging. Lightweight alternative to Akka/Pekko.

## Setup

```scala
libraryDependencies += "io.getkyo" %% "kyo-actor" % kyoVersion
```

## Key Concepts

- **Actor[A]** — receives messages of type A, processes sequentially
- **ActorRef[A]** — handle to send messages to an actor
- **Supervisor** — manages actor lifecycle and failure recovery

## Common Patterns

### Define and use an actor

```scala
val counter: ActorRef[Int] < (Async & Scope) =
    Actor.init[Int] { self =>
        var count = 0
        msg =>
            count += msg
            Console.printLine(t"count: $count")
    }
```

## Integration Notes

- Built on Kyo's fiber system (not a separate runtime)
- Actors are scoped resources (cleaned up when scope closes)
- Type-safe messaging (can't send wrong message type)
- Supervision strategies for failure handling
