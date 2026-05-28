---
id: evaluation
title: Evaluation Model
section: concepts
source_files:
  - /p/gh/mill/core/api/src/mill/api/Evaluator.scala
  - /p/gh/mill/core/exec/src/mill/exec/Execution.scala
source_commit: 41ce6c977c4
related:
  - concepts/task-system.md
  - concepts/caching.md
  - cli/task-resolution.md
---

# Evaluation Model

How Mill resolves, plans, and executes tasks.

## Pipeline

```
CLI args ("myapp.compile")
  -> Resolve: convert to Segments, find matching Task.Named
  -> Plan: compute transitive dependencies, topological sort
  -> Execute: parallel execution with caching
  -> Result: success/failure per task
```

## Resolution

The evaluator converts CLI strings to task references:

```scala
// Evaluator API
def resolveSegments(scriptArgs: Seq[String], selectMode: SelectMode): Seq[Segments]
def resolveTasks(scriptArgs: Seq[String], selectMode: SelectMode): Seq[Task.Named[?]]
```

**SelectMode**:
- `SelectMode.Single` — exactly one task must match
- `SelectMode.Multi` — multiple tasks may match (wildcards)

**Wildcards**: `_` matches any single segment:
```bash
mill _.compile        # compile all top-level modules
mill __.test          # test all modules recursively
mill foo._.compile    # compile all of foo's direct children
```

## Planning

```scala
def plan(tasks: Seq[Task.Named[?]]): (Seq[Task[?]], Seq[Task[?]])
def transitiveTasks(sourceTasks: Seq[Task[?]]): Seq[Task[?]]
def topoSorted(tasks: Seq[Task[?]]): Seq[Task[?]]
```

1. Collect all transitive dependencies
2. Topological sort (detect cycles)
3. Group into parallel execution batches

## Execution

Tasks execute in parallel up to `--jobs` limit. Each task:

1. Check cache: if inputs unchanged and code signature unchanged, return cached
2. Prepare `Task.dest` directory (clear unless persistent)
3. Run task body with `TaskCtx`
4. Serialize result to JSON in `out/`
5. Report success/failure

## Selective Execution

Mill tracks which source files affect which tasks. On re-run, only
tasks whose transitive inputs changed are re-evaluated.

```bash
mill --watch myapp.compile   # re-run on source changes
```

## Parallel Execution

Tasks with no dependency relationship execute in parallel. The
`--jobs` flag controls parallelism:

```bash
mill --jobs 4 __.compile     # 4 parallel compilation tasks
mill --jobs 0.5C __.compile  # half of available cores
```
