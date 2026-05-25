---
id: scala-native-project
title: Set Up a Scala Native Project
section: recipes
source_commit: 41ce6c977c4
related:
  - modules/scala-native-module.md
  - modules/scala-module.md
---

# Set Up a Scala Native Project

## build.mill

```scala
import mill._, scalalib._, scalanativelib._

object myapp extends ScalaNativeModule {
  def scalaVersion = "3.6.4"
  def scalaNativeVersion = "0.5.7"
  def releaseMode = ReleaseMode.ReleaseFast

  def mvnDeps = Seq(
    mvn"com.lihaoyi::os-lib::0.11.4"
  )

  object tests extends ScalaNativeTests with TestModule.Munit {
    def mvnDeps = Seq(mvn"org.scalameta::munit::1.0.0")
  }
}
```

## Build and Run

```bash
mill myapp.nativeLink        # compile + link native binary
mill myapp.run               # link and run
mill myapp.tests.test        # run tests
```

## Output

The native binary is at:
```
out/myapp/nativeLink.dest/out    # native executable
```

## C Interop

For linking against C libraries:

```scala
def nativeLinkingOptions = Seq("-L/usr/local/lib", "-lmylib")
def nativeCompileOptions = Seq("-I/usr/local/include")
```
