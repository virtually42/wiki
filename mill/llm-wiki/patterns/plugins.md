---
id: plugins
title: Writing Plugins
section: patterns
source_commit: 41ce6c977c4
related:
  - concepts/module-system.md
  - concepts/task-system.md
---

# Writing Plugins

How to create reusable Mill plugins.

## Plugin Structure

A Mill plugin is a trait that modules can mix in:

```scala
// MyPlugin.scala — published as a separate Mill module
package myorg.millplugins

import mill._
import mill.scalalib._

trait MyPlugin extends JavaModule {
  // New task
  def myPluginTask: T[PathRef] = Task {
    val result = processFiles(sources())
    PathRef(Task.dest / "output")
  }

  // Override existing task
  override def generatedSources = Task {
    super.generatedSources() ++ Seq(myPluginTask())
  }
}
```

## Using a Plugin

```scala
// build.mill
import $ivy.`myorg::mill-my-plugin:1.0.0`
import myorg.millplugins.MyPlugin

object myapp extends ScalaModule with MyPlugin {
  def scalaVersion = "3.6.4"
}
```

## Plugin with Worker

For plugins needing expensive state:

```scala
trait MyPlugin extends JavaModule {
  def myWorker = Task.Worker {
    new ExpensiveProcessor(compile())
  }

  def myProcess = Task {
    myWorker().process(sources())
  }
}
```

## Contrib Modules

Mill's built-in contrib plugins live in `contrib/`:

| Plugin | Import | Purpose |
|--------|--------|---------|
| `JmhModule` | `mill.contrib.jmh` | JMH benchmarks |
| `DockerModule` | `mill.contrib.docker` | Docker image building |
| `FlywayModule` | `mill.contrib.flyway` | Database migrations |
| `ScalaPBModule` | `mill.contrib.scalapblib` | Protocol buffers |
| `ScoverageModule` | `mill.contrib.scoverage` | Code coverage |
| `BuildInfo` | `mill.contrib.buildinfo` | Build info generation |
| `VersionFileModule` | `mill.contrib.versionfile` | Version file management |
| `ProguardModule` | `mill.contrib.proguard` | Code shrinking |

## Using Contrib Plugins

Contrib plugins are bundled with Mill — no `$ivy` import needed:

```scala
import mill.contrib.jmh.JmhModule

object bench extends ScalaModule with JmhModule {
  def scalaVersion = "3.6.4"
  def jmhCoreVersion = "1.37"
}
```
