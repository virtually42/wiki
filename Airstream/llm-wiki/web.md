---
id: airstream-web
title: "Web Integration"
category: concept
tags: [ajax, fetch, dom-events, webstorage, localstorage, browser]
source_files:
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/web/AjaxStream.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/web/FetchStream.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/web/DomEventStream.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/web/WebStorageVar.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/web/WebStorageBuilder.scala
source_commit: 781abe8
related: [airstream-streams, airstream-state, airstream-custom-sources]
see_also: [airstream-patterns]
---

# Web Integration

Browser APIs exposed as reactive Airstream primitives: HTTP requests as
streams, DOM events as streams, and web storage as reactive Vars.

## FetchStream

Modern HTTP via the Fetch API. Default codec decodes responses to `String`.

### Basic Usage

```scala
// GET returning EventStream[String]
FetchStream.get("/api/data")

// POST with body and headers
FetchStream.post(
  "/api/items",
  _.body("{ \"name\": \"x\" }"),
  _.headers("Content-Type" -> "application/json")
)

// PUT, generic apply
FetchStream(_.PUT, "/api/items/1",
  _.body(payload),
  _.headers("Authorization" -> s"Bearer $token")
)
```

### Raw and Custom Codecs

```scala
// Get raw dom.Response (no decoding)
FetchStream.raw.get("/api/binary")

// Custom encoder + decoder
FetchStream.withCodec[MyRequest, MyResponse](
  encodeRequest = req => JSON.stringify(req.toJs),
  decodeResponse = resp => EventStream.fromJsPromise(resp.json()).map(fromJs)
).post("/api/rpc")

// Encoder only (response still decoded to String)
FetchStream.withEncoder[MyRequest](req => JSON.stringify(req.toJs))

// Decoder only (request body stays dom.BodyInit)
FetchStream.withDecoder[MyResponse](resp =>
  EventStream.fromJsPromise(resp.json()).map(fromJs)
)
```

### FetchOptions

Options are set via mutation callbacks passed as varargs:

| Option | Description |
|--------|-------------|
| `_.body(content)` | Request body (encoded via builder's `encodeRequest`) |
| `_.headers(k -> v, ...)` | Set headers (overwrite per key) |
| `_.headersAppend(k -> v, ...)` | Append headers (multi-value keys) |
| `_.mode(_.cors)` | RequestMode |
| `_.credentials(_.include)` | RequestCredentials |
| `_.cache(_.`no-cache`)` | RequestCache |
| `_.redirect(_.follow)` | RequestRedirect |
| `_.referrer(url)` | Referrer URL |
| `_.referrerPolicy(_.origin)` | ReferrerPolicy |
| `_.integrity(hash)` | Subresource integrity hash |
| `_.keepAlive(true)` | Keep connection alive |
| `_.abortStream(stream)` | Abort when `stream` emits |
| `_.abortOnStop()` | Abort if FetchStream is stopped |
| `_.emitOnce(true)` | Only fire the request once (first start) |

### Lifecycle

- Request fires when the stream is started (via `onWillStart`).
- By default, restarting the stream fires a new request each time.
- `emitOnce(true)` suppresses re-requests after the first.
- `abortOnStop()` cancels the underlying fetch when observers stop.
- `abortStream(s)` cancels the fetch when `s` emits any value;
  errors from `s` are re-emitted by FetchStream.

## AjaxStream

XMLHttpRequest-based streams. Emits `dom.XMLHttpRequest` on success or
a typed `AjaxStreamError` subclass on failure.

### Methods

```scala
AjaxStream.get(url, data, timeoutMs, headers, ...)
AjaxStream.post(url, data, timeoutMs, headers, ...)
AjaxStream.put(url, data, timeoutMs, headers, ...)
AjaxStream.patch(url, data, timeoutMs, headers, ...)
AjaxStream.delete(url, data, timeoutMs, headers, ...)
```

All methods share the same parameter signature:

```scala
def get(
  url: String,
  data: InputData = null,          // String | ArrayBufferView | Blob | FormData
  timeoutMs: Int = 0,
  headers: Map[String, String] = Map.empty,
  withCredentials: Boolean = false,
  responseType: String = "",
  isStatusCodeSuccess: Int => Boolean = defaultIsStatusCodeSuccess,
  requestObserver: Observer[dom.XMLHttpRequest] = Observer.empty,
  progressObserver: Observer[(dom.XMLHttpRequest, dom.ProgressEvent)] = Observer.empty,
  uploadProgressObserver: Observer[(dom.XMLHttpRequest, dom.ProgressEvent)] = Observer.empty,
  readyStateChangeObserver: Observer[dom.XMLHttpRequest] = Observer.empty
): AjaxStream
```

### Error Types

```scala
sealed abstract class AjaxStreamError(val xhr: dom.XMLHttpRequest, message: String)
  extends Exception

case class AjaxStatusError(xhr, status: Int, message: String)  // non-2xx/304
case class AjaxNetworkError(xhr, message: String)               // DNS, CORS, etc.
case class AjaxTimeout(xhr)                                     // request timed out
case class AjaxAbort(xhr)                                       // request aborted
```

Default success: status 200-299 or 304.

### completeEvents

Recovers errors back into `XMLHttpRequest` values so you always get
exactly one event per request regardless of outcome:

```scala
val stream: AjaxStream = AjaxStream.get("/api/data")
stream.completeEvents // EventStream[dom.XMLHttpRequest] -- always fires
```

### Lifecycle

- Request is initiated in `onStart` (not `onWillStart`).
- Restarting fires a new request; the old request's response is ignored
  (not aborted).
- Progress, upload progress, and ready-state observers are optional
  side-channel hooks.

### Building Blocks

For custom XHR logic, use the low-level helpers:

```scala
AjaxStream.initRequest(timeoutMs, withCredentials, responseType)
AjaxStream.sendRequest(request, method, url, data, headers)
```

## DomEventStream

Wraps `addEventListener` / `removeEventListener` as a lazy stream.

```scala
DomEventStream[dom.MouseEvent](element, "click")
DomEventStream[dom.KeyboardEvent](dom.document, "keydown")
DomEventStream[dom.Event](dom.window, "resize", useCapture = true)
```

- Listener is added when the stream starts and removed when it stops.
- Type parameter `Ev` must match the actual event type for the given key.
- Uses `CustomStreamSource` internally.

## WebStorageVar

A `Var` backed by `localStorage` or `sessionStorage`. Reads the stored
value on creation and writes back on every update.

### Creating

```scala
// Text var with default
val name: WebStorageVar[String] =
  WebStorageVar.localStorage("user-name", syncOwner = Some(unsafeWindowOwner))
    .text(default = "anonymous")

// Typed var with codec
val prefs: WebStorageVar[Prefs] =
  WebStorageVar.localStorage("prefs", syncOwner = None)
    .withCodec[Prefs](
      encode = prefs => JSON.stringify(prefs.toJs),
      decode = str => Try(fromJson(str)),
      default = Success(Prefs.empty)
    )

// Built-in codecs
builder.text(default = "")      // String identity
builder.bool(default = false)   // toBoolean / toString
builder.int(default = 0)        // toInt / toString
```

### Session Storage

```scala
val token: WebStorageVar[String] =
  WebStorageVar.sessionStorage("auth-token", syncOwner = None)
    .text(default = "")
```

### Cross-Tab Syncing

Local storage is shared across tabs. Pass a `syncOwner` to listen for
`StorageEvent` updates from other tabs and sync into the Var:

```scala
WebStorageVar.localStorage("theme", syncOwner = Some(unsafeWindowOwner))
  .text(default = "light")
```

Without `syncOwner`, the Var works normally but won't pick up changes
made by other tabs. You can also call `syncFromExternalUpdates` later
or do a one-shot `pullOnce()`.

### Key APIs

| Method | Description |
|--------|-------------|
| `.signal` | Reactive signal of the current value |
| `.set(value)` | Update Var and persist to storage |
| `.pullOnce()` | One-shot read from storage into Var |
| `.syncFromExternalUpdates` | Start continuous cross-tab sync |
| `.externalUpdates` | Stream of `StorageEvent` from other tabs/frames |
| `.rawStorageValues` | Signal of the raw `Option[String]` in storage |

### Availability Checks

```scala
WebStorageVar.isLocalStorageAvailable()   // Boolean
WebStorageVar.isSessionStorageAvailable() // Boolean
WebStorageVar.localStorageError()         // Option[DOMException]
WebStorageVar.sessionStorageError()       // Option[DOMException]
```

Storage may be disabled by browser settings. In that case the Var still
works as an ephemeral in-memory Var but values are not persisted.

### Constraints

- Do not create multiple Vars for the same storage key in the same tab/frame.
  They will not stay in sync with each other.
- Error values pushed into the Var are NOT persisted to storage and NOT
  synced to other tabs.

## Deprecation Note

`AjaxEventStream` was renamed to `AjaxStream` in version 15.0.0-M1. The
old name exists as a deprecated type alias in `package.scala`.
