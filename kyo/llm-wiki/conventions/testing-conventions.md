---
id: kyo-convention-testing-conventions
title: "Testing Conventions"
category: convention
layer: foundation
tags: [testing, test-base, assertions, platform-conditional]
source_files:
  - /p/gh/kyo/CONTRIBUTING.md
  - /p/gh/kyo/AGENTS.md
source_commit: 9bab8d00
api_surface: []
related: [kyo-pattern-testing]
see_also: [kyo-recipe-effect-testing]
platforms: [jvm, js, native]
---

## Rule

Use the module's `Test` base class. Assert on concrete values, not types or non-emptiness.

## Test Framework

- Kyo internal tests: module-specific `Test` base trait (extends zio-test)
- Application tests: `KyoSpecDefault` from `kyo-zio-test`
- Test runner: ZIO Test SBT framework

## Assertion Rules

### Do

```scala
assert(result == List(1, 2, 3))         // concrete values
assert(result == Result.succeed(42))    // specific outcome
assertTrue(count == 5)                  // exact check
```

### Don't

```scala
assert(result.nonEmpty)                 // too weak
assert(result.isInstanceOf[List[_]])    // type check only
assert(true)                            // asserts nothing
```

## Core Rules from AGENTS.md

1. **Fix the code, not the test** — diagnose root cause before changing anything
2. **Never weaken a test to make it pass** — no removing assertions or catching exceptions
3. **Test behavior, not implementation** — verify from caller's perspective
4. **Cover edge cases** — empty inputs, errors, boundaries, concurrency

## Building & Testing

```bash
export JAVA_OPTS="-Xms3G -Xmx4G -Xss10M -XX:MaxMetaspaceSize=512M -XX:ReservedCodeCacheSize=128M -Dfile.encoding=UTF-8"

# Test specific module
sbt 'kyo-core/test'

# Test specific class
sbt 'kyo-core/testOnly kyo.ChannelTest'
```

**Note:** Building auto-formats code. Re-read edited files after building.

## Platform-Conditional Tests

Tests can be conditionally run per platform (JVM/JS/Native) using the framework's built-in support.
