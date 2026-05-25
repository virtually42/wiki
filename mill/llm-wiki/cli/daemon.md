---
id: daemon
title: Daemon Mode
section: cli
source_files:
  - runner/launcher/src/mill/launcher/MillLauncherMain.scala
source_commit: 41ce6c977c4
related:
  - cli/commands.md
  - patterns/workers.md
---

# Daemon Mode

Mill runs as a background daemon by default for fast subsequent invocations.

## How It Works

1. First `mill` invocation starts a daemon JVM process
2. Subsequent invocations connect to the running daemon via RPC
3. The daemon keeps classloaders, workers, and caches in memory
4. Daemon shuts down after inactivity timeout

## Benefits

- Fast startup for subsequent runs (no JVM startup cost)
- Workers persist across runs (compilation caches, etc.)
- Parallel client support (multiple `mill` commands simultaneously)

## No-Server Mode

Disable the daemon for debugging or CI:

```bash
mill --no-server myapp.compile
```

## BSP (Build Server Protocol)

Mill supports BSP for IDE integration:

```bash
mill --bsp-install          # install BSP connection file
```

This creates `.bsp/mill-bsp.json` for IntelliJ IDEA or Metals.

## JVM Configuration

Control the daemon JVM:

```
# .mill-jvm-version — JVM version for Mill
21

# mill-jvm-opts — JVM options for Mill
-XX:NonProfiledCodeHeapSize=250m
-XX:ReservedCodeCacheSize=500m
-Xmx2g
```

## Daemon Management

```bash
mill shutdown               # stop the daemon
mill --no-server compile    # run without daemon
```
