---
id: task-resolution
title: Task Resolution
section: cli
source_files:
  - core/resolve/src/mill/resolve/ResolveCore.scala
source_commit: 41ce6c977c4
related:
  - cli/commands.md
  - concepts/module-system.md
---

# Task Resolution

How Mill maps CLI strings to tasks.

## Path Syntax

```
module.submodule.task
```

Each `.`-separated segment is either a module name or a task name.
The last segment is always the task.

## Wildcards

### `_` — Single Level

Matches any single segment at that level:

```bash
mill _.compile          # all top-level modules' compile
mill myapp._.compile    # all of myapp's direct children's compile
```

### `__` — Recursive

Matches any number of segments (recursive descent):

```bash
mill __.compile         # compile in ALL modules at any depth
mill __.test            # test ALL modules at any depth
mill myapp.__.test      # test all modules under myapp
```

## Cross-Module Syntax

```bash
mill mylib[3.6.4].compile           # specific cross value
mill mylib[_].compile               # all cross values
mill mylib[2.13.16].tests.test      # nested in cross module
```

## Resolution Order

1. Parse string into segments
2. Walk module tree matching segments
3. For each matched module, look up the task name
4. Return all matching `Task.Named` instances

## Inspect

```bash
mill inspect myapp.compile
# Shows: task type, inputs, source location
```

## Resolve

```bash
mill resolve _                # list all top-level modules
mill resolve myapp._          # list all tasks in myapp
mill resolve __.compile       # list all compile tasks
mill resolve myapp.tests._    # list all test tasks
```
