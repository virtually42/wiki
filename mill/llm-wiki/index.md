# Mill LLM-Wiki

Query-optimized knowledge base for the Mill build tool (v1.1.5+).

## Quick Lookup

| I want to... | Start here |
|---|---|
| Set up a Scala 3 project | [recipes/scala-project](recipes/scala-project.md) |
| Set up a ScalaJS project | [recipes/scalajs-project](recipes/scalajs-project.md) |
| Set up a Scala Native project | [recipes/scala-native-project](recipes/scala-native-project.md) |
| Add dependencies | [configuration/dependencies](configuration/dependencies.md) |
| Configure compiler options | [configuration/compiler-options](configuration/compiler-options.md) |
| Cross-build across versions | [configuration/cross-building](configuration/cross-building.md) |
| Write tests | [modules/test-module](modules/test-module.md) |
| Publish to Maven Central | [configuration/publishing](configuration/publishing.md) |
| Build a multi-module project | [patterns/multi-module](patterns/multi-module.md) |
| Build a multi-platform project | [recipes/multi-platform](recipes/multi-platform.md) |
| Understand the task system | [concepts/task-system](concepts/task-system.md) |
| Understand modules | [concepts/module-system](concepts/module-system.md) |
| Write a plugin | [patterns/plugins](patterns/plugins.md) |
| Use the CLI | [cli/commands](cli/commands.md) |
| Use YAML build files | [patterns/yaml-builds](patterns/yaml-builds.md) |

## Sections

- [concepts/](concepts/index.md) — core abstractions: Module, Task, evaluation, caching, build graph
- [modules/](modules/index.md) — language modules: JavaModule, ScalaModule, ScalaJSModule, etc.
- [configuration/](configuration/index.md) — dependencies, sources, compiler options, cross-building, publishing
- [patterns/](patterns/index.md) — multi-module builds, workers, plugins, YAML builds
- [recipes/](recipes/index.md) — task-oriented: set up projects, publish, create plugins
- [cli/](cli/index.md) — commands, task resolution, daemon mode

## Architecture Overview

```
CLI (mill command)
  -> Runner/Launcher (daemon or single-process)
    -> Evaluator (resolve tasks, plan, execute)
      -> Build Graph (Module tree with Task DAG)
        -> Task execution (caching, invalidation, parallel)
```

## Module Layers

```
Core:           core/api (Module, Task, Evaluator APIs)
                core/eval, core/exec, core/resolve (implementation)
Language:       libs/javalib (JavaModule, TestModule, PublishModule)
                libs/scalalib (ScalaModule, CrossScalaModule)
                libs/scalajslib (ScalaJSModule)
                libs/scalanativelib (ScalaNativeModule)
                libs/kotlinlib (KotlinModule)
                libs/pythonlib (PythonModule)
                libs/javascriptlib (TypeScriptModule)
Contrib:        contrib/* (jmh, docker, flyway, scalapb, scoverage, etc.)
Runner:         runner/ (CLI entry point, daemon, BSP)
```
