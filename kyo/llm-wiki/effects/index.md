# Effects

One page per effect, grouped by layer.

## Prelude Effects (pure, no side effects)

| Page | Pending Type | Summary |
|------|-------------|---------|
| [abort](abort.md) | `Abort[E]` | Typed error handling, short-circuiting |
| [env](env.md) | `Env[R]` | Dependency injection via TypeMap |
| [var](var.md) | `Var[V]` | Functional mutable state |
| [emit](emit.md) | `Emit[V]` | Value emission (writer-like) |
| [choice](choice.md) | `Choice` | Non-deterministic branching |
| [local](local.md) | `Local[V]` | Scoped values (ThreadLocal-like) |
| [stream](stream.md) | `Stream[V, S]` | Composable data processing |
| [batch](batch.md) | `Batch` | Automatic N+1 optimization |

## Core Effects (side-effectful, concurrency)

| Page | Pending Type | Summary |
|------|-------------|---------|
| [sync](sync.md) | `Sync` | Side-effect suspension |
| [async](async.md) | `Async` | Green threads, fibers |
| [scope](scope.md) | `Scope` | Resource lifecycle management |
| [channel](channel.md) | — | Bounded async communication |
| [queue](queue.md) | — | Concurrent FIFO queue |
| [hub](hub.md) | — | Broadcast with backpressure |
| [retry](retry.md) | — | Automatic retry with backoff |
| [clock](clock.md) | — | Time operations, testing |
