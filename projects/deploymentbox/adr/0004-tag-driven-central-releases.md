---
id: deploymentbox-adr-0004
title: Tag-driven Maven Central releases, one signing key, no snapshots
kind: normative
status: accepted
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

The deploymentbox publishes `no.virtual-architect` library artifacts
to Maven Central. The 2026-05-29 conversation surfaced several
distribution-shape decisions that need to be recorded as a
coherent set:

- **Distribution target.** Maven Central via Sonatype Central
  Portal vs. alternatives (GitHub Packages, JitPack, self-hosted
  Nexus, no-publish).
- **groupId.** `no.virtual-architect` (reverse DNS of the
  operator's `virtual-architect.no` domain) vs. `io.github.tigidar`
  (GitHub-hosted, no DNS required).
- **Release vs. snapshot.** Releases only (immutable, signed,
  Central-validated) vs. also snapshots (mutable, separate
  repository, optional for downstream live-tracking).
- **Trigger.** Tag-driven (operator-controlled) vs. auto-publish on
  push.
- **Signing key fan-out.** One key for all libraries vs. per-library
  keys.

## Decision

1. **Distribution target:** Maven Central via Sonatype Central
   Portal (the new system, *not* the legacy OSSRH path).
2. **groupId:** `no.virtual-architect`. The DNS TXT verification on
   `virtual-architect.no` (via uniweb.no) is the namespace claim
   mechanism; Sonatype does not care which GitHub user owns the
   source repos — namespace ownership is proven via DNS, not git.
3. **Release-only.** No snapshots. Local cross-library iteration
   uses `mill __.publishLocal` to `~/.ivy2/local/` on the
   developer's machine. Downstream consumers either pin a released
   version or work locally against `publishLocal`. No third party
   ever consumes a SNAPSHOT.
4. **Trigger:** git tags. The release script is invoked as
   `release <repo> <tag>`, fetches `--branch <tag> --depth 1`, and
   builds from the tag's tree. No CI auto-publish on push.
5. **One signing key for all libraries.** A single GPG identity
   published under `no.virtual-architect`. Per-library keys would
   multiply the YubiKey ceremony burden without changing the
   threat model (a single compromise of one key would still let
   the attacker forge under that library only — but the attacker
   would need to have separately compromised the operator's
   ceremony for that key, which is the same single point of
   failure as one key).

## Consequences

- **One thing to lose, one thing to back up.** Single key = single
  backup story (offline master + revocation cert + spare YubiKey).
  Per-library keys multiply this by N libraries.
- **Operator-paced releases.** The operator decides when to publish;
  no surprise releases from a commit they forgot was on `main`. The
  workflow is `git tag → ssh → release`. Tag = release-intent
  signal.
- **No snapshot machinery.** No second pipeline to maintain, no
  snapshot resolver for consumers to configure, no risk of stale
  SNAPSHOT artifacts confusing downstream. Local cross-library
  development is solved by `publishLocal`, which is free and
  doesn't involve Central at all.
- **DNS-backed namespace claim.** `no.virtual-architect` is
  controlled by the operator-owned domain. If `virtual-architect.no`
  expires or is transferred, the namespace claim does not transfer
  — Sonatype's verification is at *claim time* but they may
  re-verify; the operator must keep the TXT record in place. The
  Sonatype account itself is durable and tied to the operator's
  login.
- **Release immutability.** Once an artifact is published to Central,
  it cannot be edited or removed (only superseded). Mistakes
  manifest as `0.1.1` releases.
- **Per-library Mill wiring.** Each library's `build.mill` declares
  `groupId = "no.virtual-architect"`, `developers`, `licenses`,
  `scmInfo = github.com/tigidar/<repo>`, and `publishVersion =
  <tag-derived>`. This is per-library work; the deploymentbox
  doesn't impose any of this — it just runs `mill __.publishSigned`
  and accepts whatever the library's `PomSettings` says.

## Alternatives Considered

- **groupId `io.github.tigidar`.** Considered. Rejected because the
  operator owns `virtual-architect.no` and prefers a domain-derived
  groupId, both for branding (the libraries publish under the
  organisation identity, not the personal pseudonym) and because
  the `io.github.*` claim is delegated through GitHub's
  ownership, which is one more dependency.
- **GitHub Packages instead of Maven Central.** Rejected:
  consumers must authenticate to GitHub to pull. Defeats
  open-source distribution.
- **JitPack.** Rejected: not Maven Central; consumers must add a
  resolver; loses signature verification on the consumer side; ties
  the publishing identity to GitHub's view of the repo.
- **Self-hosted Nexus/Reposilite.** Overkill for the scale; another
  service to maintain; consumers must add a resolver.
- **Snapshots in addition to releases.** Considered earlier in the
  conversation. Rejected: doubles the CI surface, adds a separate
  Central endpoint to authenticate against, and the user has
  no cross-library consumers outside their own `publishLocal` story
  that would benefit from snapshots. Can be added later without
  breaking changes if a real need emerges.
- **Per-library GPG keys.** Rejected: multiplies the ceremony
  burden by N libraries (key generation, backup, YubiKey slot, key
  expiry rotation) with marginal threat-model improvement.

## Links

- [[projects/deploymentbox/designs/release-pipeline]]
- [[projects/deploymentbox/adr/0001-host-hetzner-nixos]]
- [[projects/deploymentbox/adr/0003-signing-yubikey-forwarded]] —
  defines *where the signing key lives*; this ADR defines *what
  gets signed*
- Sonatype Central Portal: https://central.sonatype.com
