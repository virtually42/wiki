---
id: build-file-structure
title: Build File Structure
section: patterns
source_commit: 41ce6c977c4
related:
  - concepts/module-system.md
  - patterns/multi-module.md
---

# Build File Structure

How to organize Mill build definitions.

## Single File (Small Projects)

```
myproject/
  build.mill          <- entire build definition
  src/
  tests/src/
```

## Package Files (Large Projects)

For large multi-module builds, split into `package.mill` files:

```
myproject/
  build.mill          <- root module, imports
  core/
    package.mill      <- core module definition
    src/
  app/
    package.mill      <- app module definition
    src/
  common/
    package.mill      <- shared traits
```

### build.mill (root)

```scala
package build

import mill._, scalalib._

// Root-level settings, shared traits
trait MyModule extends ScalaModule {
  def scalaVersion = "3.6.4"
}
```

### core/package.mill

```scala
package build.core

import mill._, scalalib._

object `package` extends MyModule {
  def mvnDeps = Seq(mvn"com.lihaoyi::os-lib:0.11.4")
}
```

### app/package.mill

```scala
package build.app

import mill._, scalalib._

object `package` extends MyModule {
  def moduleDeps = Seq(build.core)
}
```

## Mill Build Dependencies

For importing external build plugins or helper libraries:

```scala
// mill-build/build.mill or at the top of build.mill
import $ivy.`com.lihaoyi::mill-contrib-jmh:$MILL_VERSION`
```

## Workspace Files

| File | Purpose |
|------|---------|
| `build.mill` | Main build definition |
| `build.mill.yaml` | YAML-based build (alternative) |
| `package.mill` | Sub-module build definition |
| `.mill-jvm-version` | JVM version for Mill itself |
| `.mill-opts` | Mill CLI options |
| `mill-jvm-opts` | JVM options for Mill |
| `mill-repositories` | Custom Maven repositories |
