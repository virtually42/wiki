---
id: kyo-recipe-effect-testing
title: "Test Effectful Code"
category: recipe
layer: application
tags: [testing, mocking, time-control, zio-test]
source_files: []
source_commit: 9bab8d00
api_surface: [KyoSpecDefault, Env.run, Clock.withTimeControl, Abort.run]
related: [kyo-pattern-testing]
see_also: [kyo-pattern-dependency-injection]
platforms: [jvm, js, native]
modules_needed: [kyo-core, kyo-zio-test]
complexity: simple
---

## Goal

Test effectful Kyo code with dependency injection and time control.

## Prerequisites

```scala
libraryDependencies ++= Seq(
  "io.getkyo"  %% "kyo-zio-test" % kyoVersion % Test,
  "dev.zio"    %% "zio-test-sbt" % zioVersion % Test
)
Test / testFrameworks += new TestFramework("zio.test.sbt.ZTestFramework")
```

## Steps

### Basic effect test

```scala
import kyo.*
import kyo.test.*
import zio.test.{Result as _, *}

object MyTest extends KyoSpecDefault:
    def spec = suite("my service")(
        test("handles valid input") {
            for
                result <- Abort.run(validate("hello"))
            yield assertTrue(result == Result.succeed(Valid("hello")))
        },
        test("rejects empty input") {
            for
                result <- Abort.run(validate(""))
            yield assertTrue(result.isFailure)
        }
    )
```

### Mock dependencies with Env

```scala
test("uses mock repo") {
    val mockRepo = new UserRepo:
        def find(id: Int) = Maybe(User(id, "test@test.com"))
    val mockEmail = new EmailService:
        def send(to: String, body: String) = ()

    for
        result <- Env.run(mockRepo)(Env.run(mockEmail)(notifyUser(1)))
    yield assertTrue(result == ())
}
```

### Control time

```scala
test("timeout fires after delay") {
    Clock.withTimeControl { control =>
        for
            fiber  <- Async.run(Clock.sleep(5.minutes).andThen("done"))
            _      <- control.advance(5.minutes)
            result <- fiber.get
        yield assertTrue(result == "done")
    }
}
```

### Test error paths

```scala
test("handles database failure") {
    val failingRepo = new UserRepo:
        def find(id: Int) = Abort.fail(DbError("connection lost"))

    for
        result <- Abort.run(Env.run(failingRepo)(getUser(1)))
    yield assertTrue(result == Result.fail(DbError("connection lost")))
}
```

## Variations

- **Property-based:** Combine with ZIO Test generators
- **Concurrent:** Test race conditions with `Async.parallel`
- **Integration:** Use real dependencies with test containers (kyo-pod)
