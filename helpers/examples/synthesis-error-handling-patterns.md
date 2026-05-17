---
id: error-handling-patterns-2026q2
title: Error handling patterns across projects (2026-Q2)
kind: descriptive
status: active
scope: cross-project
confidence: high
created: 2026-05-15
updated: 2026-05-15
sources:
  - projects/compositor/syntheses/error-handling.md
  - projects/webapp/adr/003-typed-errors.md
  - projects/cli-tool/log.md
---

# Synthesis: Error Handling Patterns Across Projects (2026-Q2)

## Observation

Three of four active projects have independently converged on the same error handling pattern: sealed error ADTs at module boundaries using Kyo's `Abort` effect. The compositor and webapp projects formalized this in ADRs; the cli-tool adopted it informally (visible in code but not documented in an ADR).

## Evidence

### Compositor (ADR-003)
- Defines per-subsystem error ADTs: `InputError`, `RenderError`, `IpcError`, `WmError`
- Converts wlroots C errors to domain errors at the Scala Native binding layer
- Adopted [[tech/patterns/typed-errors]] explicitly

### Webapp (ADR-003)
- Defines per-service error ADTs: `UserError`, `AuthError`, `OrderError`
- HTTP layer maps domain errors to status codes via exhaustive pattern match
- Adopted [[tech/patterns/typed-errors]] explicitly

### CLI Tool (no ADR yet)
- Uses typed error enums in the command handler layer
- No formal ADR or compliance declaration — this is a drift item
- Pattern matches on errors to produce user-facing messages

### Infra
- Not applicable — NixOS configuration, not Scala application code

## Analysis

The convergence is strong evidence that the typed error boundary pattern is a natural fit for Kyo-based Scala projects. Key observations:

1. **The pattern scales down.** Even the small CLI tool benefits from typed errors for user-facing messages.
2. **Boundary placement varies appropriately.** The compositor uses subsystem boundaries; the webapp uses service boundaries; the CLI uses command boundaries. The abstraction level matches the project's architecture.
3. **The conversion-at-boundary principle is consistent.** All three projects convert infrastructure/library errors to domain errors at the outermost layer of each module.

## Recommendations

1. **Promote to tech pattern.** Already done: [[tech/patterns/typed-errors]] was created from this evidence.
2. **Document the CLI tool's usage.** Create an ADR for cli-tool that adopts the pattern and resolves the drift item.
3. **Consider a normative decision.** The pattern is successful enough to warrant `kind: normative` on [[tech/patterns/typed-errors]], which would require all in-scope projects to address it in ADRs.

## Confidence Assessment

**High.** Based on direct observation of three independent implementations, two with explicit ADRs, one visible in code. No counter-evidence found.
