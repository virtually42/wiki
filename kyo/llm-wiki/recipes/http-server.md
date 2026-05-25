---
id: kyo-recipe-http-server
title: "Build an HTTP Server"
category: recipe
layer: application
tags: [http, server, routes, rest-api]
source_files:
  - kyo-examples/jvm/src/main/scala/examples/ledger/api/
source_commit: 9bab8d00
api_surface: [HttpServer.init, HttpRoute.get, HttpRoute.post, HttpHandler, HttpFilter, KyoApp]
related: [kyo-module-kyo-http]
see_also: [kyo-pattern-error-handling, kyo-pattern-dependency-injection]
platforms: [jvm, js, native]
modules_needed: [kyo-core, kyo-http]
complexity: moderate
---

## Goal

Build a REST API server with routes, JSON handling, and middleware.

## Prerequisites

```scala
libraryDependencies ++= Seq(
  "io.getkyo" %% "kyo-core" % kyoVersion,
  "io.getkyo" %% "kyo-http" % kyoVersion
)
```

## Steps

### 1. Define routes

```scala
import kyo.*

val routes = Seq(
    HttpRoute.get("/health") { _ =>
        HttpResponse.ok("healthy")
    },
    HttpRoute.get("/users/:id") { req =>
        val id = req.pathParam("id").toInt
        findUser(id).map {
            case Present(user) => HttpResponse.json(user)
            case Absent        => HttpResponse.notFound("user not found")
        }
    },
    HttpRoute.post("/users") { req =>
        req.bodyAs[CreateUser].map { body =>
            createUser(body).map(HttpResponse.json(_))
        }
    }
)
```

### 2. Add middleware

```scala
val withLogging = HttpFilter { (req, next) =>
    Console.printLine(t"${req.method} ${req.path}").andThen(next(req))
}

val withCors = HttpFilter.cors(
    allowOrigin = "*",
    allowMethods = Seq("GET", "POST")
)

val filtered = withLogging.andThen(withCors)(routes)
```

### 3. Start server

```scala
object MyServer extends KyoApp:
    run {
        direct {
            val port = System.property[Int]("PORT", 8080).now
            Console.printLine(t"Starting on port $port").now
            HttpServer.init(port, "0.0.0.0")(filtered*).now
            Async.never.now  // keep alive
        }
    }
```

## Complete Example

See `kyo-examples/jvm/src/main/scala/examples/ledger/` for a full REST API with database.

## Variations

- **With DI:** Inject services via `Env.get[UserService]` in handlers
- **With error handling:** Use `Abort[DomainError]` and map to HTTP status codes
- **With streaming:** SSE endpoints via `HttpResponse.sse(stream)`
