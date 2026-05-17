# compositor — Wiki Schema

Inherits from root CLAUDE.md and POLICY.md. May extend but must not weaken
the compliance contract.

## Purpose

A Wayland compositor built with Scala Native and Kyo. Currently in prototype
phase. The wiki captures architectural decisions, subsystem boundaries,
and integration patterns with the wlroots C library.

## Stack

- Language: Scala Native
- Effects: Kyo
- Platform: Wayland / wlroots
- Build: Mill + Nix
- Target OS: NixOS

## Tagging

- `subsystem:` input | rendering | ipc | wm | widget-runtime
- `surface:` wlroots | kyo | wasm | airstream
- `phase:` design | prototype | stable

## ADR Conventions

- Filename: `adr/NNNN-kebab-title.md` (monotonic)
- Every ADR has the `compliance` block from POLICY.md
- Superseding: new ADR cites old in `supersedes:`

## Ticket Conventions

- Filename: `tickets/open/NNNN-kebab-title.md`
- Move to `closed/` on completion, keep the number
- Frontmatter: status, created, closed, related_adr

## Local Overrides

> This project uses Scala Native, so JVM-specific tech pages are marked
> `ignores` in ADR-001 wholesale. Subsequent ADRs do not need to re-ignore them.

> The rendering subsystem uses mutable wlroots buffers. This is documented as
> an exception in ADR-003, not a deviation — the immutable-state preference is
> `recommended`, not `required`.
