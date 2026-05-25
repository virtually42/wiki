---
id: kyo-module-kyo-case-app
title: "kyo-case-app — CLI Parsing"
category: module
layer: integration
tags: [cli, parsing, command-line, case-app]
source_files:
  - kyo-case-app/shared/src/main/scala/kyo/
source_commit: 9bab8d00
api_surface: [KyoCaseApp, KyoCommand]
related: []
see_also: [kyo-recipe-cli-app]
platforms: [jvm, js, native]
module_name: "kyo-case-app"
dependencies: [kyo-core]
---

## Purpose

CLI argument parsing via case-app integration with Kyo's `run` blocks.

## Setup

```scala
libraryDependencies += "io.getkyo" %% "kyo-case-app" % kyoVersion
```

## Key APIs

- `KyoCaseApp` — base trait for CLI applications with parsed options
- `KyoCommand` — sub-command support

## Common Pattern

```scala
import kyo.*

case class Options(
    @ExtraName("n") name: String,
    @ExtraName("c") count: Int = 1
)

object MyApp extends KyoCaseApp[Options]:
    def run(options: Options, remainingArgs: RemainingArgs) =
        Console.printLine(t"Hello ${options.name}! (x${options.count})")
```

## Integration Notes

- Automatic help text generation from case class fields
- Supports subcommands via `KyoCommand`
- Cross-platform (JVM, JS, Native)
