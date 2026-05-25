---
id: yaml-builds
title: YAML Build Files
section: patterns
source_commit: 41ce6c977c4
related:
  - patterns/build-file-structure.md
  - modules/java-module.md
---

# YAML Build Files

Mill supports `build.mill.yaml` as a simpler alternative to `build.mill`
for straightforward projects.

## Basic Example

```yaml
# build.mill.yaml
extends: JavaModule
mvnDeps:
  - org.thymeleaf:thymeleaf:3.1.1.RELEASE
  - org.slf4j:slf4j-nop:2.0.7
```

## Scala Project

```yaml
extends: ScalaModule
scalaVersion: "3.6.4"
mvnDeps:
  - com.lihaoyi::os-lib:0.11.4
  - com.lihaoyi::upickle:4.1.0
```

## With Tests

```yaml
extends: ScalaModule
scalaVersion: "3.6.4"
mvnDeps:
  - com.lihaoyi::os-lib:0.11.4
test:
  extends: TestModule.Munit
  mvnDeps:
    - org.scalameta::munit:1.0.0
```

## When to Use YAML vs Scala

**YAML**: Single-module projects with standard configuration. No custom
tasks, no plugins, no cross-building.

**Scala (build.mill)**: Multi-module projects, custom tasks, plugins,
cross-building, programmatic configuration.
