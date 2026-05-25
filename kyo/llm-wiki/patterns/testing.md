---
id: kyo-pattern-testing
title: "Testing Patterns"
category: pattern
layer: core
tags: [testing, zio-test, mocking, time-control, env]
source_files: []
source_commit: 9bab8d00
api_surface: [KyoSpecDefault, Clock.withTimeControl, Env.run]
related: [kyo-effect-env, kyo-effect-clock]
see_also: [kyo-recipe-effect-testing]
platforms: [jvm, js, native]
when_to_use: "Testing effectful Kyo code"
when_not_to_use: "Pure function tests (just use normal assertions)"
---

## Problem

How to test effectful code deterministically.

## Solution

### Test Framework Setup

```scala
// build.sbt
libraryDependencies ++= Seq(
  "dev.zio" %% "zio-test-sbt" % zioVersion % Test,
  "io.getkyo" %% "kyo-zio-test" % kyoVersion % Test
)
Test / testFrameworks += new TestFramework("zio.test.sbt.ZTestFramework")
```

### Basic Test

```scala
import kyo.*
import kyo.test.*
import zio.test.{Result as _, *}

object MyTest extends KyoSpecDefault:
    def spec = suite("my suite")(
        test("simple") {
            for
                result <- Abort.run(myFunction(input))
            yield assertTrue(result == Result.succeed(expected))
        }
    )
```

### Mocking with Env

```scala
test("with mock") {
    val mockRepo = new UserRepo:
        def find(id: Int) = Maybe(User(id, "test"))

    for
        result <- Env.run(mockRepo)(myService(1))
    yield assertTrue(result.name == "test")
}
```

### Time Control

```scala
test("timeout behavior") {
    Clock.withTimeControl { control =>
        for
            fiber  <- Async.run(Clock.sleep(1.hour).andThen("done"))
            _      <- control.advance(1.hour)
            result <- fiber.get
        yield assertTrue(result == "done")
    }
}
```

## Trade-offs

- KyoSpecDefault handles most effects automatically
- Use `Env.run` for mock injection (no framework needed)
- `Clock.withTimeControl` makes time tests deterministic
- Kyo uses internal `Test` base class for module tests (not for app tests)

## Related

- [dependency-injection](dependency-injection.md) — mock injection patterns
