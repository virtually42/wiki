---
id: safetensors-extract-from-paladium
title: Extract paladium.ein.safetensors into a self-contained safetensors-scala library
kind: descriptive
status: accepted
project: safetensors-scala
created: 2026-05-29
updated: 2026-05-29
related_adrs: []
related_plans:
  - projects/safetensors-scala/plans/extract-from-paladium.md
sources:
  - /p/v42/paladium/paladium/src/paladium/ein/safetensors/SafeTensors.scala
  - /p/v42/paladium/paladium/src/paladium/ein/safetensors/HeaderParser.scala
  - /p/v42/paladium/paladium/test/src/paladium/ein/safetensors/SafeTensorsSuite.scala
  - /p/hg/sourceline-manager/build.mill
  - tech/guides/mill-cross-platform.md
  - tech/decisions/deps-single-file.md
---

## Problem

The SafeTensors binary format is a HuggingFace-standard format for storing
tensor weights. Scala has no published reader. The paladium ML framework
contains a working cross-platform reader at `paladium.ein.safetensors`
(two files: `SafeTensors.scala`, `HeaderParser.scala`) coupled to
paladium's domain types (`Dim`, `TensorData`, `Ein`, `NumberLike`).

Goal: extract a self-contained `safetensors-scala` library that any Scala
3 JVM/JS/Native project can depend on, with zero references to paladium,
while preserving paladium's current call sites via a thin adapter.

## Constraints

- **Cross-platform**: JVM + Scala.js + Scala Native, matching paladium's matrix.
- **Single runtime dependency**: `scodec-core` (already used; vetted on all
  three platforms).
- **Mill build conforming to wiki conventions**: see [[tech/guides/mill-cross-platform]]
  Pattern B, [[tech/decisions/deps-single-file]], and the gold-standard
  reference at `/p/hg/sourceline-manager/build.mill`.
- **Mill 1.1.2** (matches sourceline-manager and paladium).
- **No paladium concepts leak into the public API**: no `Dim`, no `TensorData`,
  no `Ein`, no `NumberLike`. The library returns primitives (`Array`, `List[Int]`).
- **Paladium re-integration must be additive**: paladium swaps its in-tree
  files for a `mvnDeps` entry plus a thin adapter file; existing callers of
  `readFloat` / `readDouble` / `loadAll` / `loadWeights` see no signature
  change.
- **Personal repo policy**: target `/p/hg/safetensors-scala`, unsigned commits,
  author `tigidar`, no `Co-Authored-By` (per user memory).

## Options Explored

### Option A: Pure raw API — return `(List[Int], Array[A])`

The library exposes only shape (as `List[Int]`) and contiguous data
(as `Array[Float]` or `Array[Double]`). Callers who want named-dim ergonomics
zip the shape with their own names.

**Public surface:**

```scala
package no.virtual_architect.safetensors

enum DType(val byteSize: Int):
  case F16, BF16 extends DType(2)
  case F32       extends DType(4)
  case F64       extends DType(8)
  case I8, U8, BOOL extends DType(1)
  case I16       extends DType(2)
  case I32       extends DType(4)
  case I64       extends DType(8)

case class TensorMeta(dtype: DType, shape: List[Int], dataOffsets: (Long, Long))
case class SafeTensorsHeader(tensors: Map[String, TensorMeta], metadata: Map[String, String])

object SafeTensors:
  def parseHeader(bytes: Array[Byte]): SafeTensorsHeader

  def readFloat(bytes: Array[Byte], header: SafeTensorsHeader, name: String):
    (List[Int], Array[Float])

  def readDouble(bytes: Array[Byte], header: SafeTensorsHeader, name: String):
    (List[Int], Array[Double])

  def loadAllFloat(bytes: Array[Byte]):  Map[String, (List[Int], Array[Float])]
  def loadAllDouble(bytes: Array[Byte]): Map[String, (List[Int], Array[Double])]
```

Pros:
- Smallest possible API surface; nothing to learn beyond Scala primitives.
- No competing tensor abstraction polluting the broader ecosystem.
- Paladium's adapter does a trivial `.zip(shape).map(Dim(name, _))` and
  `TensorData.fromArray`.

Cons:
- A `(List[Int], Array[A])` tuple is awkward to pass around — every caller
  invents its own `case class Tensor[A]`.
- Slight redundancy in `Map[String, (List[Int], Array[A])]`.

### Option B: Pure raw API + thin `TensorView[A]` value class

Same as Option A, but wrap the return into a minimal record with no
methods beyond `shape`, `data`, and convenience `numElements`.

```scala
final case class TensorView[A](shape: List[Int], data: Array[A]):
  def numElements: Int = if shape.isEmpty then 1 else shape.product
```

Pros:
- Nameable type for type signatures and Maps (`Map[String, TensorView[Float]]`).
- Still zero ML semantics — no dims-by-name, no strides, no NumberLike.

Cons:
- One more type to maintain; users still want their own tensor type, so they
  end up unwrapping `.shape` and `.data` anyway.
- `equals`/`hashCode` semantics around `Array` are a footgun (the same hazard
  paladium's `TensorData` handles via custom overrides).

### Option C: Mirror paladium's `Dim` + `TensorData` in the new library

Move `Dim` and a minimal `TensorData` clone into `safetensors-scala`, give
the reader signatures that look like today's paladium code.

Pros:
- Paladium adapter is a one-line `import` alias.

Cons (decisive):
- Drags ML/autodiff semantics (named dims, strides, `equals` over `Array`)
  into a file-format library that knows nothing about either.
- Other downstream consumers (a different ML framework, an inference engine,
  a model converter) inherit naming choices they did not ask for.
- Forces `safetensors-scala` to track paladium's `TensorData` evolution —
  exactly the coupling we are trying to eliminate.

Rejected.

## Proposed Approach

Adopt **Option A** (raw API). Justified by: the package's only intrinsic
data is shape + bytes; `Dim` / `TensorData` / `Ein` were never load-bearing
inside the reader (they appear only at the API edge, not in the decoding
logic). A thin `case class` wrapper (Option B) can be added later without
breaking Option A — start minimal.

### Public API

```scala
package no.virtual_architect.safetensors

import scodec.*, scodec.bits.*, scodec.codecs.*

enum DType(val byteSize: Int):
  case F16  extends DType(2)
  case BF16 extends DType(2)
  case F32  extends DType(4)
  case F64  extends DType(8)
  case I8   extends DType(1)
  case I16  extends DType(2)
  case I32  extends DType(4)
  case I64  extends DType(8)
  case U8   extends DType(1)
  case BOOL extends DType(1)

object DType:
  def fromString(s: String): DType

final case class TensorMeta(
  dtype: DType,
  shape: List[Int],
  dataOffsets: (Long, Long)
)

final case class SafeTensorsHeader(
  tensors: Map[String, TensorMeta],
  metadata: Map[String, String]
)

object SafeTensors:
  /** Parse the 8-byte LE header-size prefix plus JSON header. */
  def parseHeader(bytes: Array[Byte]): SafeTensorsHeader

  /** Decode tensor `name` as Float32. Supports F32, BF16 (promoted to F32). */
  def readFloat(
    bytes: Array[Byte],
    header: SafeTensorsHeader,
    name: String
  ): (List[Int], Array[Float])

  /** Decode tensor `name` as Float64. Supports F64, plus F32/BF16 promoted. */
  def readDouble(
    bytes: Array[Byte],
    header: SafeTensorsHeader,
    name: String
  ): (List[Int], Array[Double])

  /** Decode every tensor in the file as Float32 in one pass. */
  def loadAllFloat(bytes: Array[Byte]): Map[String, (List[Int], Array[Float])]

  /** Decode every tensor in the file as Float64 in one pass. */
  def loadAllDouble(bytes: Array[Byte]): Map[String, (List[Int], Array[Double])]
```

Changes from the in-tree paladium API:

| In-tree paladium | safetensors-scala |
|------------------|-------------------|
| `readFloat(bytes, header, name, dimNames)` | `readFloat(bytes, header, name)` |
| `readDouble(bytes, header, name, dimNames)` | `readDouble(bytes, header, name)` |
| `loadAll[A: NumberLike: ClassTag](bytes, dimMapping)` | `loadAllFloat(bytes)` / `loadAllDouble(bytes)` |
| `loadWeights[A](expr: Ein[A], weights)` | *removed — paladium-only adapter* |
| Returns `TensorData[A]` | Returns `(List[Int], Array[A])` |

`HeaderParser` stays internal (`private[safetensors]`) — already pure, no
coupling, no changes needed.

### Target package

`no.virtual_architect.safetensors`. Rationale: the organization is the same
as sourceline-manager (`no.virtual-architect` Maven group, `no.virtual_architect`
package — Scala packages cannot contain hyphens). Same Apache-2.0 license,
same `tigidar` developer block, same `virtual-architect.no` URL.

### Target directory tree

```
/p/hg/safetensors-scala/
├── build.mill
├── flake.nix
├── .gitignore
├── README.md
├── LICENSE                       # Apache-2.0
├── docs/
│   └── adr/
│       └── 0001-inline-versions.md   # ADR for the deps-single-file deviation
└── safetensors/
    ├── src/
    │   ├── SafeTensors.scala          # public reader
    │   └── HeaderParser.scala         # private JSON parser
    ├── test/
    │   └── src/
    │       └── SafeTensorsSuite.scala
    ├── jvm/                           # Cross[] platform shell (no sources)
    ├── js/                            # Cross[] platform shell
    └── native/                        # Cross[] platform shell
```

Mirrors sourceline-manager exactly: `<module>/src/` for shared sources,
`<module>/test/src/` for shared tests, empty per-platform directories whose
`moduleDir` is one `os.up` hop from `src/`. No `src-jvm` / `src-js` /
`src-native` directories — the package is platform-agnostic (scodec covers
all three).

### Target `build.mill`

Mirrors `/p/hg/sourceline-manager/build.mill` exactly with three substitutions:
artifact name, description, and the scodec runtime dependency.

```scala
//| mill-version: 1.1.2
//| mill-jvm-version: system

package build

import mill._
import mill.scalalib._
import mill.scalalib.publish._
import mill.scalajslib._
import mill.scalanativelib._

object V {
  val scalaVersions = Seq("3.8.3")

  val scalaJS         = "1.20.1"
  val scalaNative     = "0.5.12"
  val munit           = "1.0.3"
  val munitScalaCheck = "1.0.0"
  val scodec          = "2.3.2"   // align with paladium's scodec-core

  val organization   = "no.virtual-architect"
  val artifact       = "safetensors-scala"
  val projectVersion = "0.1.0-SNAPSHOT"
}

trait SafeTensorsCommon extends CrossScalaModule with PublishModule {
  def artifactName = V.artifact
  def publishVersion = V.projectVersion

  def pomSettings = PomSettings(
    description    = "Cross-platform SafeTensors binary format reader for Scala 3.",
    organization   = V.organization,
    url            = "https://github.com/tigidar/safetensors-scala",
    licenses       = Seq(License.`Apache-2.0`),
    versionControl = VersionControl.github("tigidar", "safetensors-scala"),
    developers     = Seq(
      Developer(
        id              = "tigidar",
        name            = "tigidar",
        url             = "https://github.com/tigidar",
        organization    = Some("virtual-architect"),
        organizationUrl = Some("https://virtual-architect.no")
      )
    )
  )

  def scalacOptions = Seq(
    "-deprecation",
    "-feature",
    "-explain",
    "-Wunused:all"
  )

  override def mvnDeps = super.mvnDeps() ++ Seq(
    mvn"org.scodec::scodec-core::${V.scodec}"
  )

  // Shared sources live at safetensors/src/. moduleDir for a Cross variant
  // is safetensors/<platform>/, so one os.up hop lands on safetensors/.
  // See [[tech/guides/mill-cross-platform]] §Pitfalls.
  def sharedSrc = Task.Sources(moduleDir / os.up / "src")
  override def sources = Task { super.sources() ++ sharedSrc() }
}

trait SafeTensorsTestSources extends ScalaModule {
  // moduleDir for safetensors.<platform>[v].test is safetensors/<platform>/test/,
  // so two os.up hops land on safetensors/.
  def sharedTestSrc = Task.Sources(moduleDir / os.up / os.up / "test" / "src")
  override def sources = Task { super.sources() ++ sharedTestSrc() }
  def mvnDeps = Seq(
    mvn"org.scalameta::munit::${V.munit}",
    mvn"org.scalameta::munit-scalacheck::${V.munitScalaCheck}"
  )
}

object safetensors extends Module {

  trait JvmModule extends SafeTensorsCommon {
    object test extends ScalaTests with TestModule.Munit with SafeTensorsTestSources
  }
  object jvm extends Cross[JvmModule](V.scalaVersions)

  trait JsModule extends SafeTensorsCommon with ScalaJSModule {
    def scalaJSVersion = V.scalaJS
    object test extends ScalaJSTests with TestModule.Munit with SafeTensorsTestSources
  }
  object js extends Cross[JsModule](V.scalaVersions)

  trait NativeModule extends SafeTensorsCommon with ScalaNativeModule {
    def scalaNativeVersion = V.scalaNative

    // Filter -release (JVM-only) per [[tech/guides/mill-cross-platform]] §Platform Gotchas.
    override def scalacOptions = Task {
      super.scalacOptions().filterNot(opt =>
        opt.startsWith("-release") || opt.startsWith("--release")
      )
    }

    object test extends ScalaNativeTests with TestModule.Munit with SafeTensorsTestSources
  }
  object native extends Cross[NativeModule](V.scalaVersions)
}
```

### Paladium re-integration adapter

Paladium swaps the in-tree files for a `mvnDeps` entry on
`safetensors-scala`, then writes a single thin adapter file:

```scala
// /p/v42/paladium/paladium/src/paladium/ein/safetensors/WeightsLoader.scala
package paladium.ein.safetensors

import paladium.NumberLike
import paladium.ein.{Dim, Ein, TensorData}
import no.virtual_architect.safetensors.{SafeTensors as RawST, SafeTensorsHeader, DType}
import scala.reflect.ClassTag

// Re-export the raw types so existing paladium imports keep working.
export RawST.parseHeader
export no.virtual_architect.safetensors.{DType, TensorMeta, SafeTensorsHeader}

object SafeTensors:

  /** Read a tensor as TensorData[Float] with paladium named dims. */
  def readFloat(
      bytes: Array[Byte],
      header: SafeTensorsHeader,
      name: String,
      dimNames: List[String]
  ): TensorData[Float] =
    val (shape, data) = RawST.readFloat(bytes, header, name)
    require(dimNames.length == shape.length,
      s"dimNames length ${dimNames.length} != shape length ${shape.length} for tensor '$name'")
    TensorData.fromArray(dimNames.zip(shape).map(Dim.apply.tupled), data)

  /** Read a tensor as TensorData[Double] with paladium named dims. */
  def readDouble(
      bytes: Array[Byte],
      header: SafeTensorsHeader,
      name: String,
      dimNames: List[String]
  ): TensorData[Double] =
    val (shape, data) = RawST.readDouble(bytes, header, name)
    require(dimNames.length == shape.length,
      s"dimNames length ${dimNames.length} != shape length ${shape.length} for tensor '$name'")
    TensorData.fromArray(dimNames.zip(shape).map(Dim.apply.tupled), data)

  def loadAll[A: NumberLike: ClassTag](
      bytes: Array[Byte],
      dimMapping: String => List[String]
  ): Map[String, TensorData[A]] =
    val header = RawST.parseHeader(bytes)
    val cls = summon[ClassTag[A]].runtimeClass
    header.tensors.map { (name, _) =>
      val dimNames = dimMapping(name)
      val td =
        if cls == classOf[Float] then
          readFloat(bytes, header, name, dimNames).asInstanceOf[TensorData[A]]
        else if cls == classOf[Double] then
          readDouble(bytes, header, name, dimNames).asInstanceOf[TensorData[A]]
        else
          throw IllegalArgumentException(s"Unsupported type: $cls")
      name -> td
    }

  /** Replace Ein.Param data in an expression tree with loaded weights.
    * Unchanged from the in-tree version. */
  def loadWeights[A: NumberLike: ClassTag](
      expr: Ein[A],
      weights: Map[String, TensorData[A]]
  ): Ein[A] = /* unchanged structural recursion — see git history */ ???
```

Call sites in paladium see identical signatures, so no caller code changes.

## Trade-offs

### Inline `object V` vs. `deps/Dependencies.mill`

[[tech/decisions/deps-single-file]] is normative for monorepo / multi-dep
projects; it explicitly recognises sourceline-manager's deviation
(`projects/sourceline-manager/adr/0002-deviate-deps-single-file.md`) for
single-library single-dependency repos.

`safetensors-scala` has the same shape as sourceline-manager: one library,
one runtime dependency (scodec), one publish artifact. An inline `object V`
keeps `build.mill` self-contained and matches the reference template
verbatim. Recommendation: **inline `object V`**, record the deviation in
`docs/adr/0001-inline-versions.md` once the repo is created (mirrors
sourceline-manager ADR-0002).

### scodec as the only runtime dependency vs. hand-rolled binary read

The reader needs: u64-LE, f32-LE arrays, f64-LE arrays, u16-LE for BF16.
A hand-rolled `ByteBuffer` reader would save ~1 dep on JVM, but Scala Native
lacks `java.nio.ByteBuffer` semantics and Scala.js's emulation is partial.
scodec gives one set of codecs that work identically on all three platforms,
which is exactly the value being preserved. Keep scodec.

### Returning `Array[A]` vs. `IArray[A]` / `Vector[A]`

`Array[A]` is mutable. For an ML interop format, callers immediately feed
the array into a tensor library (BLAS, ONNX, paladium's `TensorData`) that
expects `Array`. `IArray[A]` would force a copy at the boundary; `Vector[A]`
would force boxing for `Vector[Float]` and `Vector[Double]`. Trade safety
for the only sensible interop shape: **return `Array[A]`**. Document that
the returned arrays are freshly allocated per call (no aliasing into the
input `bytes`).

### Removing the `NumberLike` constraint on `loadAll`

In the in-tree code, `NumberLike` was a phantom constraint — `loadAll`
inspected `ClassTag.runtimeClass` and dispatched to `readFloat` /
`readDouble`. No `NumberLike` method was ever called. Drop the constraint
entirely; expose two monomorphic methods (`loadAllFloat`, `loadAllDouble`).
This eliminates the only place `NumberLike` appeared in the package surface.

### Dropping the `dimNames` parameter from `read*`

`dimNames` only ever drove `TensorData.fromArray(dims, data)`. The shape is
already in the header; the caller knows the names. Pushing the zip to the
caller removes paladium's `Dim` from the API and removes a redundant
arity-check (the shape from the file is authoritative; the caller's names
are an annotation).

## Open Questions

- **Organization name**: `no.virtual-architect` (sourceline-manager precedent)
  vs. minting a new `no.virtual-architect.safetensors` sub-organization.
  Recommendation: reuse `no.virtual-architect`, same as sourceline-manager.
- **Maven artifact name vs. GitHub repo name**: artifact `safetensors-scala`,
  repo `safetensors-scala`. Both match. Confirmed.
- **License**: Apache-2.0 (matches sourceline-manager). Upstream HuggingFace
  safetensors crate is also Apache-2.0 / MIT dual-licensed, so Apache-2.0 is
  ecosystem-compatible.
- **Int/Long dtype support**: should `loadAllInt32` / `loadAllInt64` ship in
  the initial release? Defer to a follow-up — paladium does not use them and
  the failure mode is a clear `IllegalArgumentException`, not silent
  corruption.
- **Writer support**: out of scope for v0.1.0. The format spec is
  symmetric, but writing requires encoder counterparts to every codec; ship
  reader-only first, gather usage signal.
- **Streaming reads**: out of scope. Callers pass `Array[Byte]`. A future
  `parseHeaderStreaming(InputStream)` could land if/when a large-model use
  case appears.
- **scodec version pinning**: paladium currently uses `Scodec.core` resolved
  from `deps/Dependencies.mill`. The extracted library should pin
  `scodec-core 2.3.2` (or whichever matches paladium's pin at extraction
  time) to avoid evicting paladium's transitive resolution. See "Risks" in
  the plan.

## Decision Record

Accepted 2026-05-29. Plan
[[projects/safetensors-scala/plans/extract-from-paladium]] executed in
the same session.

- Option A (raw `(List[Int], Array[A])` return) adopted.
- Inline `object V` deviation recorded in
  `/p/hg/safetensors-scala/docs/adr/0001-inline-versions.md`.
- Package `no.virtual_architect.safetensors`.
- License Apache-2.0.
- scodec pinned to `2.3.3` (palladium's current resolution at extraction
  time, per `/p/v42/paladium/deps/Versions.mill`'s `Scodec.core`).

Outcome captured in
[[projects/safetensors-scala/syntheses/library-extraction-via-type-alias-adapter]] —
the re-export-via-top-level-type-alias trick lets palladium consume the
new library at `paladium.ein.safetensors.*` with **zero changes in caller
import paths**, despite the upstream API surface shifting from
`TensorData[A]` to `(List[Int], Array[A])`.
