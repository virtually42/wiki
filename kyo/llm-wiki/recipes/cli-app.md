---
id: kyo-recipe-cli-app
title: "Build a CLI App"
category: recipe
layer: application
tags: [cli, command-line, case-app, kyoapp]
source_files: []
source_commit: 9bab8d00
api_surface: [KyoApp, KyoCaseApp, Console.printLine, System.property]
related: [kyo-module-kyo-case-app]
see_also: []
platforms: [jvm, js, native]
modules_needed: [kyo-core, kyo-case-app]
complexity: simple
---

## Goal

Build a command-line application with argument parsing.

## Prerequisites

```scala
libraryDependencies ++= Seq(
  "io.getkyo" %% "kyo-core" % kyoVersion,
  "io.getkyo" %% "kyo-case-app" % kyoVersion
)
```

## Steps

### Simple (no arg parsing)

```scala
import kyo.*

object MyApp extends KyoApp:
    run {
        for
            _    <- Console.printLine(s"Args: $args")
            time <- Clock.now
            _    <- Console.printLine(t"Time: $time")
        yield "done"
    }
```

### With argument parsing

```scala
import kyo.*
import caseapp.*

case class Options(
    @ExtraName("n") name: String,
    @ExtraName("v") verbose: Boolean = false,
    count: Int = 1
)

object MyApp extends KyoCaseApp[Options]:
    def run(opts: Options, remaining: RemainingArgs) =
        for
            _ <- Console.printLine(t"Hello ${opts.name}")
            _ <- if opts.verbose then Console.printLine("verbose mode") else ()
        yield ()
```

## Variations

- **Subcommands:** Use `KyoCommand` for git-style subcommands
- **Environment:** Use `System.property` or `System.env` for config
- **Exit codes:** Return non-zero from `run` block on error
