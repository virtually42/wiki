---
id: compositor-adr-0002
title: Adopt single-file Dependencies.mill
kind: normative
status: accepted
project: compositor
created: 2026-05-28
compliance:
  adopts:
    - tech/decisions/deps-single-file.md
  exceptions: []
  deviations: []
  ignores: []
supersedes: []
---

## Context

`tech/decisions/deps-single-file.md` (accepted 2026-05-24, global scope)
requires Scala projects to use a single `deps/Dependencies.mill` file
with inline `mvn"…"` coordinates, dropping the historical
`Versions.mill + Dependencies.mill` split.

The compositor project is in scope (Scala Native, any domain). At the
time of this ADR no code repository exists for the compositor — only
the wiki design / plan documents. This ADR is therefore **forward-looking**:
when the compositor codebase is stood up, it will follow the
single-file pattern from day one.

## Decision

Adopt `tech/decisions/deps-single-file.md` unconditionally. When the
compositor code repository is created:

- Create `deps/Dependencies.mill` only — do **not** create
  `deps/Versions.mill`.
- Multi-artifact libraries (Kyo, Tapir-equivalents) use a single
  `private val xV = "…"` for the shared version.
- Platform versions live in the same file under `object Platform`.

## Consequences

- Scala Steward / Renovate can parse compositor dependency coordinates
  out-of-the-box.
- Zero divergence from any sibling project's deps shape (once others
  exist).
- If a compelling reason to split appears later (e.g. compositor pins
  pre-release versions diverging from the monorepo), a follow-up ADR
  must revise this adoption — it cannot be silently violated.

## Alternatives Considered

- **Defer the ADR until code exists** — rejected; would leave the
  project drifting per `POLICY.md` and signal nothing about intent.
- **`ignores`** — rejected; the decision applies.

## Links

- [[tech/decisions/deps-single-file]]
- [[tech/stack/mill]]
- [[tech/guides/mill-dependency-management]]
