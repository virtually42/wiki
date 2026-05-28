---
id: test-module
title: TestModule
section: modules
source_files:
  - /p/gh/mill/libs/javalib/src/mill/javalib/TestModule.scala
source_commit: 41ce6c977c4
related:
  - modules/java-module.md
  - modules/scala-module.md
---

# TestModule

Mixin trait for test execution. Combined with a language module to create
test suites.

## Framework Variants

Mill provides pre-configured variants for common test frameworks:

### Java

| Variant | Framework | Dependency |
|---------|-----------|------------|
| `TestModule.Junit4` | JUnit 4 | `junit:junit:4.13.2` |
| `TestModule.Junit5` | JUnit 5 | `org.junit.jupiter:junit-jupiter:5.x` |
| `TestModule.TestNg` | TestNG | `org.testng:testng:7.x` |

### Scala

| Variant | Framework | Dependency |
|---------|-----------|------------|
| `TestModule.Munit` | MUnit | `org.scalameta::munit:1.x` |
| `TestModule.ScalaTest` | ScalaTest | `org.scalatest::scalatest:3.x` |
| `TestModule.Utest` | uTest | `com.lihaoyi::utest:0.8.x` |
| `TestModule.Specs2` | Specs2 | `org.specs2::specs2-core:5.x` |
| `TestModule.Weaver` | Weaver | `com.disneystreaming::weaver-cats:0.8.x` |
| `TestModule.ZioTest` | ZIO Test | `dev.zio::zio-test:2.x` |

### Kotlin

| Variant | Framework | Dependency |
|---------|-----------|------------|
| `TestModule.Junit5` | JUnit 5 | `org.junit.jupiter:junit-jupiter:5.x` |
| `TestModule.Spock` | Spock | Groovy-based |

## Usage Pattern

```scala
object myapp extends ScalaModule {
  def scalaVersion = "3.6.4"

  // Nested test module
  object tests extends ScalaTests with TestModule.Munit {
    def mvnDeps = Seq(
      mvn"org.scalameta::munit:1.0.0"
    )
  }
}
```

## Key Tasks

| Task | Type | Description |
|------|------|-------------|
| `testFramework` | `T[String]` | Framework runner class name |
| `test(args: String*)` | `Command` | Run tests |
| `testOnly(args: String*)` | `Command` | Run specific test classes |
| `discoveredTestClasses` | `T[Seq[String]]` | Auto-discovered test classes |
| `testClasspath` | `T[Seq[PathRef]]` | Test classpath |
| `testForkGrouping` | `T[Seq[Seq[String]]]` | Group tests for parallel forking |

## Running Tests

```bash
mill myapp.tests.test                          # run all tests
mill myapp.tests.testOnly "com.example.FooTest" # run specific test
mill myapp.tests.test -- -t "test name"        # pass args to framework
```

## Custom Test Framework

```scala
object tests extends ScalaTests {
  def testFramework = "my.custom.Framework"
  def mvnDeps = Seq(mvn"my.custom::framework:1.0.0")
}
```

## Forked Testing

Tests run in a forked JVM by default. Configure with:

```scala
object tests extends ScalaTests with TestModule.Munit {
  def forkArgs = Seq("-Xmx2g", "-Dmy.prop=value")
  def forkEnv = Map("MY_VAR" -> "value")
}
```
