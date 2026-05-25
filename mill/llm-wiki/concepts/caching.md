---
id: caching
title: Caching and Invalidation
section: concepts
source_commit: 41ce6c977c4
related:
  - concepts/task-system.md
  - concepts/evaluation.md
---

# Caching and Invalidation

Mill aggressively caches task results for fast incremental builds.

## The `out/` Directory

All cached data lives under `out/` in the project root:

```
out/
  myapp/
    compile.json          # cached result metadata
    compile.dest/         # scratch directory (compilation output)
    compile.log           # task log output
    sources.json
    tests/
      test.json
      test.dest/
      test.log
```

## Cache Keys

A task result is valid when ALL of these match:
1. **Input values** — all upstream task results unchanged
2. **Code signature** — the task's bytecode hasn't changed
3. **Worker state** — relevant workers haven't been invalidated

## Invalidation Triggers

| Trigger | What invalidates |
|---------|-----------------|
| Source file change | `Task.Sources` / `Task.Source` tasks |
| Upstream result change | Any task depending on changed task |
| Code change | Task whose definition bytecode changed |
| Worker restart | Tasks depending on that worker |
| `Task.Input` | Always re-evaluated (no caching) |

## Manual Cache Clearing

```bash
rm -rf out/myapp/compile.*   # clear specific task cache
rm -rf out/                   # clear all caches
mill clean                    # Mill's built-in clean
mill clean myapp.compile      # clean specific task
```

## Persistent vs Non-Persistent

- **Default**: `Task.dest` is cleared before each execution
- **Persistent**: `Task(persistent = true)` preserves `Task.dest` across runs
- Use persistent for incremental compilation, caches, generated indexes
