---
id: kyo-module-kyo-direct
title: "kyo-direct — Direct-Style Syntax"
category: module
layer: core
tags: [direct, syntax, now, later, macro, dotty-cps-async]
source_files:
  - kyo-direct/shared/src/main/scala/kyo/
source_commit: 9bab8d00
api_surface: [direct, .now, .later]
related: [kyo-concept-direct-syntax]
see_also: []
platforms: [jvm, js, native]
module_name: "kyo-direct"
dependencies: [kyo-core]
---

## Purpose

Imperative-looking syntax for effectful code via macro-based control flow virtualization.

## Setup

```scala
libraryDependencies += "io.getkyo" %% "kyo-direct" % kyoVersion
```

## Usage

See [concepts/direct-syntax](../concepts/direct-syntax.md) for full documentation.

```scala
import kyo.*

val result: String < (Sync & Abort[Exception]) =
    direct {
        val a = Sync.defer("hello").now
        val b = Abort.get(Right("world")).now
        s"$a $b"
    }
```

## Integration Notes

- Built on [dotty-cps-async](https://github.com/rssh/dotty-cps-async)
- Macro-based — compile errors can be cryptic
- `.now` only at top level of `direct`, not inside lambdas
- Enforces effectful hygiene — unused effects cause compile error
