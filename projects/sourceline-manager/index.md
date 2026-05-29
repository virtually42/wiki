# sourceline-manager

Foundation library: source code as a typed value algebra. `Token` /
`SourceLine` / `SourceFile` ADT plus a fluent builder, rendered to
text as a last step. Cross-published JVM / Scala.js / Scala Native
from one shared source tree.

**Status:** active

## Stack

- Language: Scala 3 (3.8.3, cross-publish-wired for next LTS)
- Platforms: JVM, Scala.js, Scala Native
- Build: Mill 1.1.2, Nix dev shell (JDK 21 + Mill + sn toolchain)
- Tests: MUnit (monoid laws)

## Code Location

`/p/hg/sourceline-manager` — see [[sources/raw/code/sourceline-manager]]
and [[sources/summaries/sourceline-manager]] for the distilled view.

The library lives outside `projects/sourceline-manager/`; this wiki
folder holds only the project's wiki-side artefacts (ADRs, plans,
syntheses, log). In-tree ADRs at `/p/hg/sourceline-manager/docs/adr/`
remain authoritative for project-local decisions; wiki ADRs here
record this project's stance on globally-accepted normative pages.

## Pages

### ADRs (wiki-side; record stance on global normative pages)

- [adr/0001-adopt-functional-domain-design.md](adr/0001-adopt-functional-domain-design.md) — Adopt [[tech/patterns/functional-domain-design]] (declarative encoding; cites in-tree ADR-0001 and ADR-0002 as evidence)
- [adr/0002-deviate-deps-single-file.md](adr/0002-deviate-deps-single-file.md) — **superseded** by adr/0006 after the dm migration; retained for reasoning history
- [adr/0003-adopt-tdd-rhythm.md](adr/0003-adopt-tdd-rhythm.md) — Adopt [[tech/patterns/tdd-rhythm]] (all five stages realised; cites `MonoidLawsSuite[A]` + `SourceLinePrimitivesLawsSpec` for Stage 2)
- [adr/0004-adopt-symmetric-refactoring.md](adr/0004-adopt-symmetric-refactoring.md) — Adopt [[tech/patterns/symmetric-refactoring]] (operator catalogue is the realisation of moves 1 and 2)
- [adr/0005-adopt-test-economics.md](adr/0005-adopt-test-economics.md) — Adopt [[tech/patterns/test-economics]] (two-layer amortisation: monoid laws + primitive laws + StringUtils composition)
- [adr/0006-adopt-deps-single-file.md](adr/0006-adopt-deps-single-file.md) — Adopt [[tech/decisions/deps-single-file]] for library coordinates (via dm-generated `deps/Dependencies.mill`); narrow platforms-only exception

### Designs
*No wiki-side designs. In-tree ADRs at `/p/hg/sourceline-manager/docs/adr/` cover the design space.*

### Plans
*No plans yet.*

### Tickets
*No tickets yet.*

### Syntheses
- [syntheses/monoid-laws-as-pbt-evidence.md](syntheses/monoid-laws-as-pbt-evidence.md) — Monoid-law tests: strong evidence for algebra-naming and Stage 0; partial evidence for PBT-as-peer and FP-stack test amortisation. Recommends promoting `symmetric-refactoring`, `tdd-rhythm`, `test-economics` from `draft` to `accepted`.

### Other
- [log.md](log.md)

## In-tree ADRs (authoritative; not mirrored here)

| # | Decision | Status | Mapped to |
|---|----------|--------|-----------|
| [0001](/p/hg/sourceline-manager/docs/adr/0001-adt-source-code-representation.md) | Source code is data, not strings | Accepted | (project-local; no global counterpart) |
| [0002](/p/hg/sourceline-manager/docs/adr/0002-functional-domain-design.md) | Functional domain design | Accepted | [[tech/patterns/functional-domain-design]] (see adr/0001) |
| [0003](/p/hg/sourceline-manager/docs/adr/0003-cross-platform-via-shared-sources.md) | Cross-platform via shared sources | Accepted | [[tech/guides/mill-cross-platform]] §Pitfalls |
| [0004](/p/hg/sourceline-manager/docs/adr/0004-scala-version-policy.md) | Scala version policy | Accepted | (project-local; no global counterpart yet) |
