---
id: scalajs-project
title: Set Up a Scala.js Project
section: recipes
source_commit: 41ce6c977c4
related:
  - modules/scalajs-module.md
  - modules/scala-module.md
---

# Set Up a Scala.js Project

## build.mill

```scala
import mill._, scalalib._, scalajslib._

object frontend extends ScalaJSModule {
  def scalaVersion = "3.6.4"
  def scalaJSVersion = "1.18.2"

  // ES modules for bundler integration
  def moduleKind = ModuleKind.ESModule

  def mvnDeps = Seq(
    mvn"com.raquo::laminar::17.2.0",
    mvn"com.raquo::waypoint::9.0.0"
  )

  object tests extends ScalaJSTests with TestModule.Munit {
    def mvnDeps = Seq(mvn"org.scalameta::munit::1.0.0")
  }
}
```

## Directory Structure

```
myproject/
  build.mill
  frontend/
    src/
      Main.scala
    tests/
      src/
        MainTest.scala
```

## Build and Run

```bash
mill frontend.fastLinkJS     # dev build (fast)
mill frontend.fullLinkJS     # production build (optimized)
mill frontend.run            # run with Node.js
mill frontend.tests.test     # run tests
```

## Output Location

The JS output is in:
```
out/frontend/fastLinkJS.dest/    # contains .js and .js.map files
out/frontend/fullLinkJS.dest/    # optimized output
```

## Integration with Vite

Point Vite at the Mill output directory for dev server integration.
The ES module output can be imported directly by a Vite `index.html`.
