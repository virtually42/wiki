---
id: multi-platform
title: Multi-Platform Project
section: recipes
source_commit: 41ce6c977c4
related:
  - configuration/cross-building.md
  - modules/scalajs-module.md
  - modules/scala-native-module.md
---

# Multi-Platform Project

Build the same code for JVM, JS, and Native.

## build.mill

```scala
import mill._, scalalib._, scalajslib._, scalanativelib._

trait SharedModule extends ScalaModule {
  def scalaVersion = "3.6.4"
  def mvnDeps = Seq(
    mvn"com.lihaoyi::upickle::4.1.0"  // :: works cross-platform
  )
}

object mylib extends Module {
  object jvm extends SharedModule

  object js extends SharedModule with ScalaJSModule {
    def scalaJSVersion = "1.18.2"
  }

  object native extends SharedModule with ScalaNativeModule {
    def scalaNativeVersion = "0.5.7"
  }
}
```

## Source Layout

```
mylib/
  jvm/src/           <- JVM-only sources
  js/src/            <- JS-only sources
  native/src/        <- Native-only sources
```

For shared sources, create a shared directory and reference it:

```scala
trait SharedModule extends ScalaModule {
  def scalaVersion = "3.6.4"
  def sources = super.sources() ++ Seq(
    PathRef(millSourcePath / os.up / "shared" / "src")
  )
}
```

```
mylib/
  shared/src/        <- shared across all platforms
  jvm/src/
  js/src/
  native/src/
```

## Build Commands

```bash
mill mylib.jvm.compile         # compile JVM
mill mylib.js.fastLinkJS       # compile JS
mill mylib.native.nativeLink   # compile Native
mill mylib.__.compile          # compile all platforms
mill mylib.__.test             # test all platforms
```

## Cross-Version + Cross-Platform

```scala
val scalaVersions = Seq("2.13.16", "3.6.4")

object mylib extends Module {
  object jvm extends Cross[JvmModule](scalaVersions)
  trait JvmModule extends CrossScalaModule

  object js extends Cross[JsModule](scalaVersions)
  trait JsModule extends CrossScalaModule with ScalaJSModule {
    def scalaJSVersion = "1.18.2"
  }
}
```
