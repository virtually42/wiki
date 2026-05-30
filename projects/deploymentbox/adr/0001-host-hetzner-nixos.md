---
id: deploymentbox-adr-0001
title: Hetzner Cloud CX32 NixOS as the build host
kind: normative
status: superseded
superseded_by: projects/deploymentbox/adr/0007-build-on-github-with-attestations.md
project: deploymentbox
created: 2026-05-29
compliance:
  adopts: []
  exceptions: []
  deviations: []
  ignores: []
supersedes: []
---

## Context

The deploymentbox must run somewhere. Candidates that surfaced in the
2026-05-29 design conversation:

- The operator's own laptop (build runs in the same env the operator
  uses for everything else).
- GitHub-hosted Actions runners (cloud-managed, ephemeral, but with
  implicit unpinned toolchain and Secrets-only key custody).
- Self-hosted GitHub Actions runner on a VPS.
- A standalone NixOS host on a cloud VPS, accessed over SSH.
- A self-managed dedicated server.

Cost ceiling for v1: low (~ €10/mo). Operator location: Norway → EU
hosting is preferred for latency and jurisdiction.

## Decision

Provision a **Hetzner Cloud CX32** (4 vCPU, 8 GB RAM, ~€7-8/mo, EU
location) and install **NixOS** declaratively via `nixos-anywhere`.

The host runs only the services required for its purpose:

- `sshd` (per [[projects/deploymentbox/adr/0002-public-ssh-hardened]])
- `gpg` available in PATH (no agent of its own; uses forwarded socket
  per [[projects/deploymentbox/adr/0003-signing-yubikey-forwarded]])
- `git`, `curl`
- `nix` with flakes enabled
- `fail2ban`

Mill, JDK, and library-specific toolchains are **not** installed at
the OS level. Each release fetches its toolchain through the
library's own flake (`nix develop --command mill …`). This is the
Volpe pattern (see
[[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]]) applied
to a single-host setup.

## Consequences

- **Reproducible host config.** The host is a derivative of
  `/p/hg/deploymentbox/flake.nix`. Rebuild from scratch is trivial:
  provision new Hetzner server, run `nixos-anywhere`, restore the
  decrypted Sonatype token. No state to preserve beyond config.
- **Cost discipline.** €7-8/mo is small relative to other costs the
  user already pays. Easy to justify; easy to cancel.
- **EU jurisdiction.** Personal data, repository data, and signing
  operations stay in the EU. Aligns with the operator's location.
- **Low-friction upgrade path.** NixOS rolling/stable channels handle
  kernel + OS updates. The flake bumps annually with the stable
  channel; emergency patches via `nixos-rebuild switch`.
- **Hetzner-specific quirks:** Hetzner's NixOS install path uses
  `nixos-anywhere` over a default Debian rescue image (or their
  bring-your-own-ISO path). Disk layout is single `/dev/sda` with
  EFI; Disko handles partitioning declaratively. No surprise here —
  standard documented pattern.

## Alternatives Considered

- **Laptop only.** Rejected: defeats the whole supply-chain isolation
  goal. The point of this project is to *not* build on the operator's
  primary work machine.
- **GitHub Actions hosted runner.** Rejected as sole signing path
  (see [[projects/deploymentbox/adr/0003-signing-yubikey-forwarded]]).
  Used in parallel for *test-only* PR workflows in each library
  repo, which is out of scope here.
- **Self-hosted GitHub Actions runner on the VPS.** Considered.
  Possible to bolt on later if PR-time builds need to leave hosted
  runners (e.g. private deps in Phase 2). For v1 the runner agent's
  maintenance burden is not justified.
- **AWS EC2 / GCP Compute Engine.** Rejected: higher complexity,
  higher cost, US-headquartered providers (jurisdiction mismatch).
  Hetzner is the obvious choice in this size/jurisdiction band.
- **DigitalOcean / Linode / Vultr.** Comparable to Hetzner. Hetzner
  has better price/perf for CPU-bound workloads in EU. No strong
  reason to prefer either.
- **Self-managed dedicated server.** Overkill for the release
  cadence; rack/colo overhead pointless for one tiny build box.
- **Hetzner CX22 instead of CX32.** Smaller cheaper instance. The
  user explicitly requested "slightly more powerful" — CX32 sized
  to handle Scala Native cross-compilation comfortably if/when a
  library needs it. Within the same price band; not worth penny-
  pinching.

## Links

- [[projects/deploymentbox/designs/release-pipeline]]
- [[projects/deploymentbox/adr/0002-public-ssh-hardened]]
- [[projects/deploymentbox/adr/0003-signing-yubikey-forwarded]]
- [[projects/deploymentbox/adr/0004-tag-driven-central-releases]]
- [[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]] — the
  Nix-pinned per-repo toolchain pattern adopted here for the
  release-time build environment
