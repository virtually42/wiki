---
id: build-graph
title: Build Graph
section: concepts
source_commit: 41ce6c977c4
related:
  - concepts/module-system.md
  - concepts/task-system.md
  - concepts/evaluation.md
---

# Build Graph

Mill builds form a two-level hierarchy: a tree of modules containing
a DAG of tasks.

## Structure

```
RootModule (build.mill)
  |
  +-- object foo extends ScalaModule
  |     |-- def scalaVersion = ...
  |     |-- def sources = Task.Sources(...)
  |     |-- def compile = Task { ... }
  |     |-- def run = Task.Command { ... }
  |     +-- object tests extends ScalaTests
  |           |-- def test = Task.Command { ... }
  |
  +-- object bar extends ScalaModule
        |-- def moduleDeps = Seq(foo)
        |-- def compile = Task { ... }  // depends on foo.compile
```

**Module tree**: static hierarchy defined by object nesting.
**Task DAG**: dynamic dependency graph defined by task references.

## Dependency Types

### Module Dependencies

```scala
object bar extends ScalaModule {
  def moduleDeps = Seq(foo)         // compile + runtime dependency
  def compileModuleDeps = Seq(baz)  // compile-only dependency
  def runModuleDeps = Seq(qux)      // runtime-only dependency
}
```

### Task Dependencies

Implicit — any `task()` call inside another task body creates an edge:

```scala
def jar = Task {
  val compiled = compile()   // edge: jar -> compile
  val res = resources()      // edge: jar -> resources
  createJar(compiled, res)
}
```

## Visualization

```bash
mill visualize myapp.compile     # generate DOT graph
mill visualize myapp._           # all tasks in module
```

Outputs a Graphviz DOT file showing the task dependency graph.

## No Circular Dependencies

Mill enforces acyclicity. If task A depends on B and B depends on A,
you get a compile-time error (for same-module) or runtime error
(for cross-module cycles).
