---
id: toolbox-adr-0001
title: Adopt Functional Domain Design (declarative encoding)
kind: normative
status: accepted
project: toolbox
created: 2026-05-29
compliance:
  adopts:
    - tech/patterns/functional-domain-design.md
  exceptions: []
  deviations: []
  ignores: []
supersedes: []
---

## Context

[[tech/patterns/functional-domain-design]] (accepted 2026-05-28,
`scope: global`, `applies_to.languages: [scala, scala-native,
scala-js]`) is in scope for `toolbox` — every module compiles on at
least two of the three Scala platforms.

The codebase already realises the pattern in its declarative form
across every module that introduces a domain type. A scan of the
ten-module tree:

| Module | ADT / value type | Evidence of pattern |
|--------|------------------|---------------------|
| `core` | `enum Cmd derives CanEqual` (15 constructors + `Raw` escape hatch); `Pipeline` ADT | Total `toShell: String` pattern match; `>` / `>>` operators lift `Cmd` to `Pipeline`; no `Product`-introspection rendering |
| `core` | `enum Pipeline` with stdout-redirection cases | Pattern realised as an algebra walked by an interpreter (`toShell`) |
| `proc` | `enum StreamTarget derives CanEqual` (`Inherit` / `Pipe` / `DevNull` / `ToFile` / `FromFile`) | Pure data, no platform surface |
| `proc` | `final case class ProcessSpec(..., stdin/stdout/stderr: StreamTarget) derives CanEqual` | Immutable model + smart `apply` constructors (varargs convenience, command-string parser); no public mutable state |
| `proc` | `enum ProcessDescription` (`Single` / `Chain` / `ChainAll` / `AndThen` / `OrElse`) | The platform-agnostic algebra all `proc-*` interpreters target |
| `vfs` | `final case class VirtualFileSystem(entries: Map[VPath, VEntry], cwd: VPath) derives CanEqual` | Pure immutable filesystem; every "mutation" returns a new value; reads return `Either[VfsError, A]` instead of throwing |
| `proc-kyo` | `final case class KyoCommandResult(exitCode, stdout, stderr) derives CanEqual` | Smart projectors (`isSuccess`, `text`, `lines`, `toEither`) — total functions over the value, no exceptions |

The cross-cutting shape: every domain type is an `enum` or
`final case class` with `derives CanEqual`, total functions for
projection / rendering, and `Either[E, A]` for fallible reads.
Effects (Kyo, fs2/CE) live exclusively in the `proc-*` interpreter
modules; the `core` / `proc` / `vfs` algebra modules carry no effect
machinery.

This is the same encoding [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]]
records — `toolbox` is its second worked example.

## Decision

Adopt [[tech/patterns/functional-domain-design]] unconditionally as
the default for **algebra and value-type modules** (`core`, `proc`,
`vfs`, and the value layer of `proc-kyo`). The encoding is
**declarative**:

- ADTs (`enum` / sealed case-class hierarchies) carry data, not
  opaque function closures.
- Operators (`>` / `>>` on `Cmd`, `andThen` / `orElse` on
  `Pipeline`) construct new values; they do not execute.
- Interpretation is a separate pass — `toShell` on `core`,
  `ProcessRunner[F]` instances on `proc-*` modules,
  `EmulatedInterpreter` on `vfs`.

Future constructors / operators must continue to be both
*orthogonal* (not expressible in terms of the existing set) and
*expressive* (necessary for some real downstream use case).

The pattern's `excludes: [shell-scripts, nix-modules]` clause does
**not** apply here — the build script (`build.mill`) is Scala, the
Nix glue is in `flake.nix` outside the schema's scope.

## Consequences

- `toolbox` is the second worked example of the pattern in this
  wiki (sourceline-manager is the first). Future projects looking
  for a multi-module / multi-platform realisation should land here.
- Adding a new process interpreter (e.g. `proc-zio`, `proc-direct`)
  is free at the `proc` algebra level — the existing types are
  reused; only a new `ProcessRunner` instance is required.
  Adding a new constructor to `ProcessDescription`, by contrast,
  requires updating every interpreter, by design.
- Effects must continue to be confined to interpreter modules.
  Any future `core` / `proc` / `vfs` change that introduces an
  `IO[_]` / `Kyo[_]` parameter or a side-effecting `def` is a
  pattern violation and should be relocated to the appropriate
  `proc-*` module.
- Allocation cost is accepted as a default. If a hot-path
  benchmark later demands deviation in a specific module, the
  deviation should be recorded as a follow-up ADR
  (compare [[projects/compositor/adr/0001-adopt-functional-domain-design]]
  which adopts with an allocation deviation).

## Alternatives Considered

- **Executable encoding** (operators carry functions, not data) —
  rejected: would defeat the `ProcessDescription` algebra. The
  whole point of the `proc-*` interpreter family is that the same
  description can be reified by os-lib, Node, fs2, or Kyo. An
  executable encoding would couple `ProcessDescription` to a
  specific runtime.
- **Not declaring and remaining silent** — would be flagged as drift
  per `POLICY.md` (missing declaration for an in-scope pattern).

## Links

- [[tech/patterns/functional-domain-design]]
- [[sources/summaries/toolbox]]
- [[sources/tmp/toolbox]]
- [[sources/summaries/sourceline-manager]]
- [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]] — sibling adoption
- [[projects/compositor/adr/0001-adopt-functional-domain-design]] — sibling adoption with allocation deviation
