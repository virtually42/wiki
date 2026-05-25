---
id: python-module
title: PythonModule
section: modules
source_files:
  - libs/pythonlib/src/mill/pythonlib/PythonModule.scala
source_commit: 41ce6c977c4
related: []
---

# PythonModule

Module for Python projects with virtualenv management.

## Import

```scala
import mill._, pythonlib._
```

## Minimal Example

```scala
object myapp extends PythonModule {
  def hostPythonCommand = "python3"
  def pythonDeps = Seq("requests==2.31.0")
}
```

## Key Tasks

| Task | Type | Description |
|------|------|-------------|
| `hostPythonCommand` | `T[String]` | Python binary on host |
| `pythonDeps` | `T[Seq[String]]` | pip dependencies |
| `sources` | `T[Seq[PathRef]]` | Python source directories |
| `moduleDeps` | `Seq[PythonModule]` | Module dependencies |
| `venv` | `T[PathRef]` | Virtual environment path |
| `pythonExe` | `T[PathRef]` | Python interpreter in venv |

## Testing

```scala
object tests extends PythonTests {
  def pythonDeps = Seq("pytest==7.4.0")
}
```
