---
id: kyo-recipe-concurrent-service
title: "Build a Concurrent Service"
category: recipe
layer: application
tags: [concurrency, fibers, channels, retry, service]
source_files: []
source_commit: 9bab8d00
api_surface: [Async.run, Channel.init, Retry, Scope.run, Fiber.get, Clock.repeatAtInterval]
related: [kyo-effect-async, kyo-effect-channel]
see_also: [kyo-pattern-concurrency, kyo-pattern-fiber-coordination]
platforms: [jvm, js, native]
modules_needed: [kyo-core]
complexity: advanced
---

## Goal

Build a service with multiple worker fibers, channels for communication, and retry logic.

## Complete Example

```scala
import kyo.*

object WorkerService extends KyoApp:
    run {
        Scope.run {
            direct {
                // Work queue
                val tasks = Channel.init[Task](capacity = 128).now
                val results = Channel.init[Result](capacity = 128).now

                // Spawn worker pool
                val workers = (1 to 4).map { id =>
                    Async.run {
                        tasks.stream.foreach { task =>
                            val result = Retry[ProcessError](Retry.Policy(limit = 3)) {
                                processTask(task)
                            }
                            result.map(results.put)
                        }
                    }.now
                }

                // Spawn result collector
                val collector = Async.run {
                    results.stream.foreach(saveResult)
                }.now

                // Spawn heartbeat
                val heartbeat = Async.run {
                    Clock.repeatAtInterval(30.seconds) {
                        Console.printLine("alive")
                    }
                }.now

                // Feed tasks
                Async.run {
                    generateTasks().foreach(tasks.put).andThen(tasks.close)
                }.now

                // Wait for completion
                workers.foreach(_.get.now)
                results.close.now
                collector.get.now
            }
        }
    }
```

## Key Patterns Used

1. **Channel** for work distribution (bounded, backpressured)
2. **Scope.run** for structured concurrency (all fibers cleaned up)
3. **Retry** for fault tolerance on individual tasks
4. **Clock.repeatAtInterval** for periodic health checks
5. **Channel.close** signals completion to consumers
