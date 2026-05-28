---
id: typescript-module
title: TypeScriptModule
section: modules
source_files:
  - /p/gh/mill/libs/javascriptlib/src/mill/javascriptlib/TypeScriptModule.scala
source_commit: 41ce6c977c4
related: []
---

# TypeScriptModule

Module for TypeScript/JavaScript projects with npm integration.

## Import

```scala
import mill._, javascriptlib._
```

## Minimal Example

```scala
object frontend extends TypeScriptModule {
  def npmDeps = Seq("express@4.18.2")
}
```

## Key Tasks

| Task | Type | Description |
|------|------|-------------|
| `npmDeps` | `T[Seq[String]]` | npm dependencies |
| `npmDevDeps` | `T[Seq[String]]` | npm dev dependencies |
| `tsDeps` | `T[Seq[String]]` | TypeScript tooling deps |
| `enableEsm` | `T[Boolean]` | ESM output format |
| `sources` | `T[Seq[PathRef]]` | Source directories |
| `moduleDeps` | `Seq[TypeScriptModule]` | Module dependencies |
| `bundle` | `T[PathRef]` | Bundled output |

## Testing

```scala
object tests extends TypeScriptTests {
  def npmDeps = Seq("jest@29.7.0")
}
```
