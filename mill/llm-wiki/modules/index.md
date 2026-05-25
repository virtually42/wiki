---
section: modules
title: Language & Build Modules
---

# Language & Build Modules

One page per module trait that users extend.

| Page | Trait | Language |
|------|-------|----------|
| [java-module](java-module.md) | `JavaModule` | Java |
| [scala-module](scala-module.md) | `ScalaModule` | Scala 2/3 |
| [scalajs-module](scalajs-module.md) | `ScalaJSModule` | Scala.js |
| [scala-native-module](scala-native-module.md) | `ScalaNativeModule` | Scala Native |
| [kotlin-module](kotlin-module.md) | `KotlinModule` | Kotlin |
| [python-module](python-module.md) | `PythonModule` | Python |
| [typescript-module](typescript-module.md) | `TypeScriptModule` | TypeScript/JS |
| [test-module](test-module.md) | `TestModule` | All (testing) |
| [publish-module](publish-module.md) | `PublishModule` | All (publishing) |

## Inheritance Hierarchy

```
Module
  +-- JavaModule
  |     +-- ScalaModule
  |     |     +-- ScalaJSModule
  |     |     +-- ScalaNativeModule
  |     |     +-- CrossScalaModule
  |     +-- KotlinModule
  |     +-- TestModule (mixin)
  |     +-- PublishModule (mixin)
  +-- PythonModule
  +-- TypeScriptModule
```
