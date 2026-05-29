---
id: safetensors-synthesis-library-extraction-via-type-alias-adapter
title: Library extraction without caller churn — top-level type aliases as the adapter spine
kind: descriptive
status: accepted
scope: project:safetensors-scala
confidence: medium
created: 2026-05-29
updated: 2026-05-29
sources:
  - /p/hg/safetensors-scala/safetensors/src/SafeTensors.scala
  - /p/v42/paladium/paladium/src/paladium/ein/safetensors/WeightsLoader.scala
  - projects/safetensors-scala/designs/extract-from-paladium.md
  - projects/safetensors-scala/plans/extract-from-paladium.md
  - tech/guides/mill-cross-platform.md
tags: [library-extraction, adapter, scala3-type-alias, scala3-export, monorepo-decoupling, partial-evidence]
---

## Observation

When a generic library is carved out of a domain-specific monorepo, the
*useful* upstream API often differs in shape from the in-tree API. The
extracted library should not carry the monorepo's domain types; the
monorepo callers should not have to rewrite their imports.

`safetensors-scala` made this concrete:

- **Upstream raw API** at `no.virtual_architect.safetensors.SafeTensors`
  returns `(List[Int], Array[A])` — no `Dim`, no `TensorData`, no `Ein`.
- **Palladium in-tree API** at `paladium.ein.safetensors.SafeTensors`
  returns `TensorData[A]` with named dims and a `loadWeights[A](expr,
  weights)` that walks an `Ein[A]` tree.
- After extraction, **every existing palladium caller compiles
  unchanged** — including code that imports
  `paladium.ein.safetensors.{DType, TensorMeta, SafeTensorsHeader}` as
  types and code that calls `SafeTensors.readFloat(bytes, header, name,
  dimNames)` with the four-argument palladium signature.

The mechanical glue is a single 90-line adapter file:
`paladium/src/paladium/ein/safetensors/WeightsLoader.scala`.

## Evidence

The adapter has four moving parts. Each one solves a specific shape of
upstream/downstream impedance:

### 1. Top-level type aliases re-export upstream types under the legacy path

```scala
package paladium.ein.safetensors

import no.virtual_architect.safetensors as ns

type DType            = ns.DType
val  DType            = ns.DType
type TensorMeta       = ns.TensorMeta
val  TensorMeta       = ns.TensorMeta
type SafeTensorsHeader = ns.SafeTensorsHeader
val  SafeTensorsHeader = ns.SafeTensorsHeader
```

The `type X = ns.X; val X = ns.X` pair re-exports both the type *and* the
companion (so `DType.F32`, `DType.fromString(_)`, and `TensorMeta(...)`
all resolve transparently). Scala 3 supports these at the top level of a
package — no wrapper object required.

This is what makes
`import paladium.ein.safetensors.SafeTensorsHeader` and
`import paladium.ein.safetensors.DType` keep working without any caller
change. A `package object` would work too, but top-level declarations
are the more modern shape.

### 2. `export` for pure delegations

```scala
object SafeTensors:
  export ns.SafeTensors.parseHeader
```

For methods whose signature is identical between upstream and
downstream, `export` is shorter than a hand-written forwarder and
preserves implicit / contextual parameters.

### 3. Wrap-and-rebind for methods that add domain semantics

```scala
def readFloat(
    bytes: Array[Byte], header: SafeTensorsHeader,
    name: String, dimNames: List[String]
): TensorData[Float] =
  val (shape, data) = ns.SafeTensors.readFloat(bytes, header, name)
  require(dimNames.length == shape.length, …)
  val dims = dimNames.zip(shape).map((n, s) => Dim(n, s))
  TensorData.fromArray(dims, data)
```

The domain-specific concerns the upstream library deliberately *does
not* know about (named dimensions, arity-vs-shape check) live in the
adapter. The upstream signature is forced to be minimal; the downstream
signature is preserved verbatim.

### 4. Domain-only operations stay inline

`loadWeights[A: NumberLike: ClassTag](expr: Ein[A], …): Ein[A]` is a
structural recursion over palladium's `Ein` ADT. It belongs in
palladium, not in `safetensors-scala`. The adapter inlines its body
unchanged from the original in-tree file.

The principle: anything that only mentions upstream types travels
upstream; anything that mentions a downstream domain type stays in the
adapter.

## Analysis

### Why "zero caller churn" is the right success metric

Library extraction has two failure modes:

1. **Pull the API surface unchanged** → the new library inherits the
   monorepo's domain types and is unusable from any other consumer.
2. **Redesign the API for genericity** → every caller in the monorepo
   has to be touched, which inflates the diff and breaks `git blame`.

The adapter-spine approach gets both wins: the upstream library has a
clean generic surface (Option A: raw `(List[Int], Array[A])`), and the
downstream caller surface is preserved by a thin file that the team
already owns. The cost is one file (~90 lines for ~four method
families).

### Why top-level type aliases — not `export` — for the types

Scala 3 allows `export` at top level, but `export
ns.{DType, TensorMeta, SafeTensorsHeader}` re-exports the *companion*
values, not the *types*. Callers who refer to `DType` in a type position
(`def f(d: DType)`) would still need an import alias. The
`type X = ns.X; val X = ns.X` pair re-exports both the type and the
term, and is the minimum shape that makes pure type-position references
also work.

### Why the version-pin discipline matters at the dep boundary

The extracted library's only runtime dep is `scodec-core`, but palladium
already had its own transitive resolution of `scodec-core`. If
safetensors-scala had pinned `2.3.2` while palladium had `2.3.3`,
Coursier would pick one and silently evict the other — potentially
yielding an `AbstractMethodError` at runtime. The plan's step-1
discipline ("read palladium's `Versions.mill`'s `Scodec.core` before
authoring V") fixes the version *at extraction time* to whatever the
consumer is already resolving. This is cheap to do once; the alternative
("upgrade both together later") is a noisy chase across two repos.

### Why JVM test runtime issues did not block the extraction

Palladium's JVM test classpath depends on an unrelated artifact
(`com.virtually42:shapesdsl_3:0.0.1`) that is not reachable from local
ivy or Maven Central. This was an *existing* condition independent of
this work. Verification still succeeded by:

1. Running `paladium.jvm[3.8.2].compile` — proves the adapter and the
   `mvnDep` resolution are sound.
2. Running `paladium.{js,native}[3.8.2].test` — these targets do not
   include the missing test artifact and exercise the adapter end-to-end
   (5 adapter tests + the `loadWeights` integration test, all green).

For library-extraction work, prefer `<consumer>.compile` to
`<consumer>.test` as the *first* gate, because compile failures usually
mean the adapter or `mvnDeps` is wrong, while test failures may mean
something else entirely.

## Recommendations

### When extracting a library from a monorepo

1. **Adopt the type-alias adapter spine** if (a) the upstream API
   shape needs to drop domain types and (b) downstream callers reference
   the in-tree types in their imports. Both conditions are common.

2. **Pin transitive dep versions to the consumer's current resolution**
   at extraction time. Bump together later.

3. **Verify adapter correctness with `<consumer>.compile` first**, then
   widen to `<consumer>.test`. Compile failures isolate the adapter;
   test failures can be noise from unrelated dependencies.

4. **Confirm zero caller churn empirically** by `grep`-ing the
   downstream code for `<package>.<TypeName>` references and *not*
   editing any of them. If a caller needs changes, the adapter is
   incomplete.

### When to *not* use this approach

- The new library is genuinely greenfield (no downstream callers yet) —
  skip the adapter, change the import paths.
- The downstream callers are minimal and well-bounded (e.g. one test
  file) — a search-and-replace is cheaper than maintaining an adapter.
- The downstream domain types would be a *better* upstream surface than
  the proposed generic types. (In this case, the extraction may not be
  worthwhile at all; the library *is* the domain.)

## Confidence Assessment

**Medium**. One worked example (this extraction). The pattern composes
the well-known Scala 3 mechanisms (`type` aliases, `val` companion
forwarders, `export`, top-level declarations) — the synthesis is in
*how* they combine for the extraction goal, not in any individual
mechanism. A second worked example (extracting another package from
palladium or any other monorepo) would raise confidence to high and
make this a candidate for promotion to
[[tech/patterns]] under a name like `library-extraction-adapter`.

## Minor pitfalls captured along the way

- **`*/` inside a Scaladoc block closes the comment.** Writing
  `loadAllFloat/loadAllDouble are covered by …` inside a `/** … */` doc
  string produced "Illegal start of toplevel definition" two lines down,
  not a comment-related error. The Scala 3 parser reports the *symptom*,
  not the cause. Workaround: avoid `*/` in Scaladoc text; use a hyphen
  or write `loadAllFloat / loadAllDouble` with surrounding space.
- **Mill `Cross[]` + manual `sharedSrc` — path math confirmed for the
  second time.** `safetensors-scala` is the second project (after
  sourceline-manager) where `moduleDir / os.up / "src"` on the
  `Cross[]` variant lands on the shared `src/` directory. This is
  the form documented in [[tech/guides/mill-cross-platform]] §Pitfalls.
  Both `mill show safetensors.jvm[3.8.3].sources` and the `jar tf` of
  the publishLocal jar confirmed non-empty class output.
