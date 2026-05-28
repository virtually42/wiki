---
id: kyo-module-kyo-http
title: "kyo-http — HTTP Client & Server"
category: module
layer: application
tags: [http, server, client, routes, streaming, sse]
source_files:
  - /p/gh/kyo/kyo-http/shared/src/main/scala/kyo/
source_commit: 9bab8d00
api_surface: [HttpClient, HttpServer, HttpRoute, HttpHandler, HttpFilter]
related: [kyo-module-kyo-caliban]
see_also: [kyo-recipe-http-server]
platforms: [jvm, js, native]
module_name: "kyo-http"
dependencies: [kyo-core]
---

## Purpose

Unified HTTP client/server API across JVM, JS, and Native platforms.

## Setup

```scala
libraryDependencies += "io.getkyo" %% "kyo-http" % kyoVersion
```

## Key APIs

### Client

| Method | Purpose |
|--------|---------|
| `HttpClient.getText(url)` | GET returning text |
| `HttpClient.getJson[A](url)` | GET with JSON deserialization |
| `HttpClient.postJson[A](url, body)` | POST with JSON body |
| `HttpClient.request(req)` | Full control over request |

### Server

| Method | Purpose |
|--------|---------|
| `HttpServer.init(port, host)(routes*)` | Start server with routes |
| `HttpRoute.get(path)(handler)` | GET route |
| `HttpRoute.post(path)(handler)` | POST route |
| `HttpHandler` | Request → Response function |
| `HttpFilter` | Middleware (logging, auth, CORS) |

### Streaming

- SSE (Server-Sent Events) support
- NDJSON streaming
- Request/response body streaming

## Common Patterns

### Simple server

```scala
object MyServer extends KyoApp:
    run {
        val routes = Seq(
            HttpRoute.get("/health")(_ => HttpResponse.ok("healthy")),
            HttpRoute.get("/users/:id") { req =>
                val id = req.pathParam("id")
                getUser(id).map(HttpResponse.json(_))
            }
        )
        HttpServer.init(8080, "0.0.0.0")(routes*).andThen(Async.never)
    }
```

### With middleware

```scala
val withLogging = HttpFilter { (req, next) =>
    Console.printLine(t"${req.method} ${req.path}").andThen(next(req))
}
val routes = withLogging(innerRoutes)
```

## Integration Notes

- OpenAPI generation and parsing supported
- Domain errors can map to HTTP status codes
- CORS filter available built-in
