---
id: safetensors-plan-extract-from-paladium
title: Extract safetensors-scala from paladium
kind: project
status: completed
project: safetensors-scala
created: 2026-05-29
updated: 2026-05-29
design_doc: projects/safetensors-scala/designs/extract-from-paladium.md
related_adrs: []
tickets: []
estimated_sessions: 2
completed_in_sessions: 1
completion_refs:
  - /p/hg/safetensors-scala@f3df739
  - /p/v42/paladium@0c9a7ac
---

## Goal

Move `paladium.ein.safetensors` (two files plus its MUnit suite) out of
the paladium monorepo and into a standalone published library at
`/p/hg/safetensors-scala` with zero paladium references, while keeping
all paladium callers source-compatible via a thin in-tree adapter.

End state:
- `/p/hg/safetensors-scala` is a Mill 1.1.2 cross-platform repo with
  non-empty JVM/JS/Native publish jars and a passing MUnit suite on each.
- Paladium depends on `mvn"no.virtual-architect::safetensors-scala::0.1.0-SNAPSHOT"`
  (or the released version) and ships a `WeightsLoader.scala` adapter that
  preserves the existing `paladium.ein.safetensors.SafeTensors.*` API.
- All paladium tests pass on JVM/JS/Native after the swap.

See [[projects/safetensors-scala/designs/extract-from-paladium]] for the
target API surface, build template, and adapter sketch.

## Prerequisites

- Design doc accepted (`status: accepted`).
- Confirm the scodec version paladium currently resolves (check
  `paladium/deps/Dependencies.mill`'s `Scodec.core`) — the new library
  pins the same value to avoid eviction conflicts.
- Confirm Apache-2.0 license, `no.virtual-architect` Maven org, repo name
  `safetensors-scala` (per design Open Questions).
- `~/.ivy2/local` is writable (publishLocal target).
- User-memory policy applies: personal repos commit unsigned, author
  `tigidar`, no `Co-Authored-By`.

## Steps

1. **Scaffold the new repo.**
   - `mkdir /p/hg/safetensors-scala && cd /p/hg/safetensors-scala && git init`
   - Author `README.md`, `.gitignore` (Scala/Mill standard: `out/`, `.bsp/`,
     `.metals/`, `target/`, `.idea/`), `LICENSE` (Apache-2.0 text).
   - Author `flake.nix` mirroring `/p/hg/sourceline-manager/flake.nix`
     (devShell with Mill, JDK, optionally Node for JS tests).
   - Author `docs/adr/0001-inline-versions.md` recording the deviation from
     [[tech/decisions/deps-single-file]] (mirror sourceline-manager
     ADR-0002).

2. **Author `build.mill`.**
   - Copy the full `build.mill` skeleton from the design doc's "Target
     `build.mill`" section verbatim.
   - Verify path-math: `moduleDir / os.up / "src"` lands on
     `safetensors/src/`; `moduleDir / os.up / os.up / "test" / "src"` from a
     nested test lands on `safetensors/test/src/`. See
     [[tech/guides/mill-cross-platform]] §Pitfalls — this is the same
     footgun that shipped sourceline-manager 0.1.0 empty jars.

3. **Copy source files.**
   - `cp /p/v42/paladium/paladium/src/paladium/ein/safetensors/SafeTensors.scala
       /p/hg/safetensors-scala/safetensors/src/SafeTensors.scala`
   - `cp /p/v42/paladium/paladium/src/paladium/ein/safetensors/HeaderParser.scala
       /p/hg/safetensors-scala/safetensors/src/HeaderParser.scala`
   - Create empty directories `safetensors/jvm/`, `safetensors/js/`,
     `safetensors/native/` (Mill needs them to discover the Cross variants;
     a `.gitkeep` per directory).

4. **Decoupling refactor.** This is the substantive change. Edit
   `safetensors/src/SafeTensors.scala`:
   - Change `package paladium.ein.safetensors` to
     `package no.virtual_architect.safetensors`.
   - Delete imports: `import paladium.NumberLike`,
     `import paladium.ein.{Dim, Ein, TensorData}`.
   - Change `readFloat` signature to drop `dimNames: List[String]` and
     return `(List[Int], Array[Float])` instead of `TensorData[Float]`.
     Remove the `requireDimMatch` and `Dim` construction; the body becomes
     `(meta.shape, decoded)`.
   - Change `readDouble` the same way: drop `dimNames`, return
     `(List[Int], Array[Double])`.
   - Replace `loadAll[A: NumberLike: ClassTag](bytes, dimMapping)` with two
     monomorphic methods:
     ```scala
     def loadAllFloat(bytes: Array[Byte]): Map[String, (List[Int], Array[Float])]
     def loadAllDouble(bytes: Array[Byte]): Map[String, (List[Int], Array[Double])]
     ```
     Each iterates `parseHeader(bytes).tensors.map`, calling the
     corresponding `read*`.
   - Delete `loadWeights` entirely. It depends on `Ein` and stays in
     paladium.
   - Delete the internal helper `requireDimMatch` (no longer used).
   - Keep `parseHeader`, `lookupMeta`, `extractDataBits`, and the codec
     definitions verbatim — they are already free of paladium types.

   Edit `safetensors/src/HeaderParser.scala`:
   - Change package to `no.virtual_architect.safetensors`. No other change.

5. **Port the test suite.**
   - `cp /p/v42/paladium/paladium/test/src/paladium/ein/safetensors/SafeTensorsSuite.scala
       /p/hg/safetensors-scala/safetensors/test/src/SafeTensorsSuite.scala`
   - Change package to `no.virtual_architect.safetensors`.
   - Delete imports: `paladium.ein.{Dim, Ein, TensorData}`,
     `paladium.NumberLike.given`.
   - Rewrite assertions that used `td.dims` / `td.data`:
     `readFloat` now returns `(shape, data)` — rebind `val (shape, data) =
     SafeTensors.readFloat(bytes, header, "W")` and assert on `shape ==
     List(3, 2)` / `data(i) == expected`. Drop the `List(Dim("out", 3),
     Dim("inp", 2))` assertions — names live in the caller, not the lib.
   - Delete `loadWeights replaces Ein.Param data in expression tree` and
     `loadWeights leaves unmatched params unchanged` — these belong with
     paladium's adapter tests.
   - Rewrite `loadAll loads all tensors as Double` to call
     `SafeTensors.loadAllDouble(bytes)` and assert on
     `loaded("W") == (List(3, 2), Array(1.0, 2.0, ...))` shape + data.
   - Run: `mill safetensors.jvm[3.8.3].test` — expect green.

6. **Cross-platform compile check.**
   - `mill safetensors.jvm[3.8.3].compile`
   - `mill safetensors.js[3.8.3].compile`
   - `mill safetensors.native[3.8.3].compile`
   - All three must succeed. Scala Native compile is the slowest; if it
     reports a `-release` flag error, the `scalacOptions` filter in the
     `NativeModule` trait is missing — re-check against the design doc's
     build template.

7. **Empty-jar footgun check** (mandatory — sourceline-manager 0.1.0 lost
   work to this).
   - `mill show safetensors.jvm[3.8.3].sources` — expect the output to
     list `safetensors/src/` (the shared dir), not just `safetensors/jvm/`.
   - After publishLocal in step 8, run:
     `jar tf ~/.ivy2/local/no.virtual-architect/safetensors-scala_3/0.1.0-SNAPSHOT/jars/safetensors-scala_3.jar
       | grep -v META-INF`
     Expect `no/virtual_architect/safetensors/SafeTensors.class`,
     `SafeTensors$.class`, `SafeTensorsHeader.class`, `DType.class`,
     `HeaderParser$.class`. Empty output = footgun hit, fix `sharedSrc`
     path math per [[tech/guides/mill-cross-platform]] §Pitfalls.

8. **Run platform tests and publishLocal.**
   - `mill safetensors.jvm[3.8.3].test` — green.
   - `mill safetensors.js[3.8.3].test` — green. (May need Node in `flake.nix`.)
   - `mill safetensors.native[3.8.3].test` — green. (Slowest; the JS tests
     can run in parallel while this compiles.)
   - `mill safetensors.jvm[3.8.3].publishLocal`
   - `mill safetensors.js[3.8.3].publishLocal`
   - `mill safetensors.native[3.8.3].publishLocal`
   - Verify all three artifacts in `~/.ivy2/local/no.virtual-architect/`
     have non-empty jars (step 7 check).

9. **Paladium: add dependency.**
   - Edit `/p/v42/paladium/deps/Dependencies.mill`: add
     `val safetensorsScala = mvn"no.virtual-architect::safetensors-scala::0.1.0-SNAPSHOT"`
     under the appropriate group (or a new `object SafeTensors:`).
   - Edit `/p/v42/paladium/build.mill` `Shared` trait: add
     `SafeTensors.safetensorsScala` (or the chosen identifier) to its
     `mvnDeps`. Confirm the dependency is picked up by JVM, JS, and Native
     variants (Mill resolves the platform suffix automatically).

10. **Paladium: write the adapter.**
    - Delete `/p/v42/paladium/paladium/src/paladium/ein/safetensors/SafeTensors.scala`
      and `HeaderParser.scala`.
    - Write `/p/v42/paladium/paladium/src/paladium/ein/safetensors/WeightsLoader.scala`
      per the design doc's "Paladium re-integration adapter" section. The
      object name `SafeTensors` is preserved (paladium callers do
      `import paladium.ein.safetensors.SafeTensors`) — only the implementation
      delegates to `no.virtual_architect.safetensors.SafeTensors`.
    - Inline the `loadWeights` body from the original file's lines 172–217
      verbatim — it is structural recursion over `Ein` and has no SafeTensors
      coupling beyond the `TensorData` argument.
    - Keep the existing test suite path
      `paladium/test/src/paladium/ein/safetensors/SafeTensorsSuite.scala`.
      Trim it to keep only the `loadWeights` integration tests; the
      header-parsing and dtype tests are now covered upstream in
      safetensors-scala.

11. **Paladium full-build verification.**
    - `mill paladium.jvm[3.8.3].test` — green.
    - `mill paladium.js[3.8.3].test` — green.
    - `mill paladium.native[3.8.3].test` — green.
    - Spot-check downstream modules: `mill benchmark.compile`,
      `mill 'web-server.test'`. Any call site that imported
      `paladium.ein.safetensors.SafeTensors.{readFloat, readDouble, loadAll,
      loadWeights}` must compile unchanged (the adapter preserves
      signatures).

12. **Commit and publish.**
    - On `/p/hg/safetensors-scala`: `git add -A && git commit -m
      "Initial extraction from paladium.ein.safetensors"` — unsigned,
      author `tigidar`, **no** `Co-Authored-By` trailer (per personal repo
      commit policy in user memory).
    - On `/p/v42/paladium`: commit the swap (per paladium's own commit
      policy — not the personal-repo policy).
    - Defer Maven Central publish to a follow-up session; `publishLocal`
      is sufficient for paladium to consume.

## Acceptance Criteria

- [ ] `/p/hg/safetensors-scala` builds on JVM/JS/Native:
  - `mill safetensors.jvm[3.8.3].compile` succeeds.
  - `mill safetensors.js[3.8.3].compile` succeeds.
  - `mill safetensors.native[3.8.3].compile` succeeds.
- [ ] `mill safetensors.{jvm,js,native}[3.8.3].test` all green.
- [ ] PublishLocal jars are **non-empty** — verified by
  `jar tf ... | grep -v META-INF` showing at least
  `SafeTensors$.class`, `SafeTensorsHeader.class`, `DType.class`,
  `HeaderParser$.class`.
- [ ] `grep -r paladium /p/hg/safetensors-scala/safetensors/src/
       /p/hg/safetensors-scala/safetensors/test/src/` produces zero matches.
- [ ] Paladium builds and tests pass on JVM/JS/Native after the swap:
  `mill paladium.{jvm,js,native}[3.8.3].test`.
- [ ] Existing paladium callers of `paladium.ein.safetensors.SafeTensors.*`
  compile without changes.
- [ ] `docs/adr/0001-inline-versions.md` recorded in the new repo,
  acknowledging deviation from [[tech/decisions/deps-single-file]].

## Risks

- **scodec version eviction.** If safetensors-scala pins a different
  scodec-core major than paladium's monorepo resolution, one wins and the
  other gets an `AbstractMethodError` at runtime. Mitigation: pin to the
  exact value paladium currently uses; bump them together. Check
  `paladium/deps/Dependencies.mill`'s `Scodec.core` before authoring V.
- **The `moduleDir` path-math footgun** ([[tech/guides/mill-cross-platform]]
  §Pitfalls). Sourceline-manager 0.1.0 shipped three empty jars while
  tests passed (tests passed because zero tests were discovered → zero
  failures). Mitigation: step 7 is mandatory; do not skip even if tests
  green. The signal is `mill show safetensors.jvm[3.8.3].sources` listing
  exactly the shared `src/` path, plus a non-empty `jar tf` output.
- **Scala.js and Native test compile times slow feedback.** Mitigation:
  step 6 runs JVM tests first (sub-second feedback); JS/Native are
  verification gates run once compilation succeeds.
- **Caller API change appears bigger than it is.** Inside paladium the
  adapter preserves `paladium.ein.safetensors.SafeTensors.{readFloat,
  readDouble, loadAll, loadWeights}` with identical signatures. Outside
  paladium (if any code already depends on the package's path), the public
  API now lives at `no.virtual_architect.safetensors.SafeTensors` and the
  return types changed from `TensorData[A]` to `(List[Int], Array[A])` —
  document this in the new repo's README.
- **Test rewrite in step 5 introduces gaps.** The original suite asserted
  on `Dim("out", 3)`-style values, exercising the `dimNames.zip(shape)`
  path. After the refactor, that path lives only in the paladium adapter.
  Mitigation: the paladium adapter tests in step 10 cover that path;
  safetensors-scala tests should add an assertion that `shape ==
  List(3, 2)` (i.e. the file-side authority) for every original test that
  asserted dim names.
- **Empty per-platform directories under `safetensors/{jvm,js,native}/`
  may be lost by git.** Mitigation: commit a `.gitkeep` in each; Mill needs
  the directories to instantiate the Cross variants.
- **`flake.nix` mismatch.** If `flake.nix` does not provide Node, JS tests
  fail in the devShell. Mitigation: confirm by running
  `mill safetensors.js[3.8.3].test` inside the devShell during step 8.
