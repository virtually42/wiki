---
id: scala-project
title: Set Up a Scala 3 Project
section: recipes
source_commit: 41ce6c977c4
related:
  - modules/scala-module.md
  - configuration/dependencies.md
  - modules/test-module.md
---

# Set Up a Scala 3 Project

## Step 1: Create build.mill

```scala
// build.mill
import mill._, scalalib._

object myapp extends ScalaModule {
  def scalaVersion = "3.6.4"

  def scalacOptions = Seq(
    "-deprecation",
    "-unchecked",
    "-Wunused:all"
  )

  def mvnDeps = Seq(
    mvn"com.lihaoyi::os-lib:0.11.4",
    mvn"com.lihaoyi::upickle:4.1.0"
  )

  object tests extends ScalaTests with TestModule.Munit {
    def mvnDeps = Seq(
      mvn"org.scalameta::munit:1.0.0"
    )
  }
}
```

## Step 2: Create directory structure

```
myproject/
  build.mill
  myapp/
    src/
      Main.scala
    tests/
      src/
        MainTest.scala
```

## Step 3: Write source files

```scala
// myapp/src/Main.scala
package myapp

@main def run(): Unit =
  println("Hello from Mill!")
```

```scala
// myapp/tests/src/MainTest.scala
package myapp

class MainTest extends munit.FunSuite:
  test("hello"):
    assertEquals(1 + 1, 2)
```

## Step 4: Run

```bash
mill myapp.compile       # compile
mill myapp.run           # run main class
mill myapp.tests.test    # run tests
mill myapp.assembly      # create fat JAR
```

## Mill Wrapper

Generate the `mill` wrapper script for the project:

```bash
# Download mill wrapper
curl -L https://raw.githubusercontent.com/lefou/millw/0.4.12/millw > mill
chmod +x mill
```

Or use `mill init` to scaffold a project interactively.
