---
id: commands
title: CLI Commands
section: cli
source_commit: 41ce6c977c4
related:
  - cli/task-resolution.md
  - cli/daemon.md
---

# CLI Commands

## Basic Usage

```bash
mill <task-path> [args...]
```

## Common Tasks

### Build

```bash
mill myapp.compile                # compile module
mill myapp.run                    # compile + run main class
mill myapp.run --mainClass com.example.Main  # run specific main
mill myapp.assembly               # create fat JAR
mill myapp.jar                    # create thin JAR
```

### Test

```bash
mill myapp.tests.test             # run all tests
mill myapp.tests.testOnly "com.example.*"  # run matching tests
mill myapp.tests.test -- -t "name" # pass args to test framework
```

### Dependencies

```bash
mill myapp.mvnDeps                # list declared deps
mill myapp.resolvedMvnDeps        # list resolved deps
mill myapp.compileClasspath       # full compile classpath
```

### Publishing

```bash
mill myapp.publishLocal           # publish to local Ivy
mill myapp.publishM2Local         # publish to local Maven
```

### Utility

```bash
mill resolve _                    # list all top-level modules
mill resolve __.compile           # list all compile tasks
mill inspect myapp.compile        # show task details
mill visualize myapp.compile      # generate dependency graph
mill clean                        # clean all cached results
mill clean myapp.compile          # clean specific task
mill init                         # scaffold a new project
mill version                      # show Mill version
```

## Global Flags

| Flag | Description |
|------|-------------|
| `--jobs N` | Parallel job count (default: CPU cores) |
| `--jobs 0.5C` | Fraction of CPU cores |
| `--watch` / `-w` | Watch for changes and re-run |
| `--debug` | Enable debug logging |
| `--offline` | Disable network access |
| `--no-server` | Run without daemon |
| `--import ivy:group::artifact:version` | Import external plugin |

## Watch Mode

```bash
mill -w myapp.compile            # recompile on source changes
mill -w myapp.tests.test         # re-test on changes
mill -w myapp.run                # re-run on changes
```

## Multiple Tasks

```bash
mill myapp.compile myapp.tests.test   # run multiple tasks
mill '{myapp.compile,myapp.tests.test}'  # alternative syntax
```

## Passing Arguments

```bash
mill myapp.run arg1 arg2              # args to main class
mill myapp.deploy --env production    # named args to commands
```
