---
id: deploymentbox-adr-0007
title: Build public OSS artifacts on GitHub Actions with sigstore attestations; sign and publish from the operator's laptop
kind: normative
status: accepted
project: deploymentbox
created: 2026-05-30
compliance:
  adopts: []
  exceptions: []
  deviations: []
  ignores: []
supersedes:
  - projects/deploymentbox/adr/0001-host-hetzner-nixos.md
  - projects/deploymentbox/adr/0002-public-ssh-hardened.md
  - projects/deploymentbox/adr/0003-signing-yubikey-forwarded.md
  - projects/deploymentbox/adr/0005-build-in-firecracker-microvm.md
  - projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening.md
---

## Context

[[projects/deploymentbox/adr/0001-host-hetzner-nixos]] picked a
self-managed Hetzner CX32 NixOS host as the build environment
on the grounds that GitHub-hosted runners had two disqualifying
properties:

1. **Implicit unpinned toolchain** — the runner's preinstalled
   tools were whatever GitHub had baked in that month.
2. **Secrets-only key custody** — the GPG signing key, if used
   on the runner, would have to live in GitHub Secrets.

Both objections have aged into something weaker:

- **(1) is no longer load-bearing.** The Volpe pattern
  ([[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]])
  pins the entire toolchain through the repo's `flake.nix` and
  `flake.lock`. The runner provides only `nix` itself (installed
  per-run via a pinned installer action); the build environment
  is hermetic and identical to what runs on the operator's
  laptop.
- **(2) was the *real* objection.** It still is — but it's now
  separable. The runner doesn't need the signing key if signing
  happens *after* download to the operator's laptop. The runner
  produces an artifact; sigstore attestations
  (`actions/attest-build-provenance`, generally available 2024)
  produce a cryptographically-verifiable proof of *what was
  built from what source on which workflow run*, signed by the
  sigstore transparency log via the runner's short-lived OIDC
  identity. The operator pulls artifact + attestation, verifies
  the chain on the laptop, *then* signs with the YubiKey, then
  publishes.

In parallel, v2's microVM design
([[projects/deploymentbox/adr/0005-build-in-firecracker-microvm]])
closed the *malicious dependency reaches host* gap, but the
fix required a fairly elaborate operator-managed substrate
(Hetzner host + Firecracker microvm.nix + MinIO + paranoid
hardening per
[[projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening]]).
Once attestations exist as a primitive, that substrate is no
longer the simplest way to get build-time isolation: an
ephemeral GitHub runner is by construction fresh-per-run with
no persistent state.

The scope of `no.virtual-architect` artifacts is **entirely
public open-source**
([[projects/deploymentbox/index]] §"Out of scope" already
excludes `dependency-manager`, which is intentionally
unlicensed and not published). For public artifacts, GitHub
already hosts the source. Extending trust to GitHub for the
*build* of code it already serves is a much smaller step than
the trust extensions v2 demanded (Hetzner provider, NixOS
config drift, MinIO uptime, etc.).

## Decision

**For all public `no.virtual-architect` library artifacts, the
deploymentbox project moves to a GitHub-Actions-builds,
sigstore-attested, laptop-signs, clean-machine-re-verifies
pipeline.**

Concrete shape:

1. **Build location: GitHub Actions, hosted runner.** Each
   library has `.github/workflows/release.yml` triggered by a
   pushed tag (`on: push: tags: ['v*']`). The workflow runs
   `nix develop -c mill -i __.compile/test/publishM2Local`
   inside the per-library Nix dev shell — same hermetic
   toolchain pattern as v2's microVM, just on GitHub's
   infrastructure.
2. **Provenance: sigstore attestation.** The workflow calls
   `actions/attest-build-provenance` over the built artifacts.
   This issues a SLSA-3 build provenance statement, signs it
   with sigstore via the runner's GitHub OIDC identity,
   records it in the sigstore transparency log, and stores
   the bundle alongside the artifacts.
3. **Artifact handoff: GitHub Artifacts API (`gh run download`).**
   No MinIO, no SSH, no rsync. The operator pulls with the
   GitHub CLI from their laptop.
4. **Verification: `gh attestation verify`.** Operator runs
   this on the laptop against the downloaded artifacts before
   touching the YubiKey. The verification chain proves:
   (artifact bytes) → (build workflow) → (source commit SHA)
   → (sigstore transparency log entry). On failure: abort,
   do not sign, do not publish.
5. **Signing: operator's laptop, direct YubiKey, no SSH
   forwarding.** Since there is no host, `gpg --detach-sign`
   runs locally and reaches the YubiKey via the local
   gpg-agent. The operator touches once per artifact. Touch-
   required mode on the YubiKey is mandatory (carried over
   from ADR-0003's recommendation).
6. **Publishing: Sonatype Central Portal REST upload from the
   laptop.** Bundle = signed artifacts + `.asc` signatures +
   poms + module files, uploaded as a single zip via
   `POST /api/v1/publisher/upload` with the operator's Portal
   token from a password manager.
7. **Post-publish re-verification on a clean machine.** Pull
   the published artifact from Maven Central on a host
   independent of the laptop (spare machine, live USB session,
   throwaway VM); verify GPG signature; recompute SHA-256 and
   compare against the value captured on the laptop before
   sign; run `gh attestation verify` against the
   Central-served artifact to prove the Central copy matches
   what GitHub Actions originally built.

### What this ADR explicitly supersedes

| Superseded ADR | What it said | Why v3 supersedes |
|---|---|---|
| [[projects/deploymentbox/adr/0001-host-hetzner-nixos]] | Provision Hetzner CX32 NixOS as the build host | No host needed — GitHub Actions is the build environment. €7-8/mo saved; OS-update treadmill removed |
| [[projects/deploymentbox/adr/0002-public-ssh-hardened]] | Public SSH on port 22, key-only, hardened, `StreamLocalBindUnlink yes` for gpg-agent forwarding | No host, no sshd, no forwarding |
| [[projects/deploymentbox/adr/0003-signing-yubikey-forwarded]] | GPG signing key on YubiKey 5, **reached via SSH-forwarded gpg-agent** from laptop to host | YubiKey custody is preserved — the *forwarding* part is gone. v3 signs locally on the laptop; no host to forward to |
| [[projects/deploymentbox/adr/0005-build-in-firecracker-microvm]] | Build inside a Firecracker microVM, MinIO handoff, SHA-256 manifest verify | Ephemeral GitHub runner gives equivalent build-time isolation for public OSS; sigstore attestation is *stronger* than v2's bare SHA-256 because it cryptographically binds artifact → source SHA → workflow |
| [[projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening]] | Selected paranoid-NixOS layers on the host (auditd, noexec, restricted nix users, etc.) | No host to harden |

### What this ADR does **not** supersede

| Kept ADR | Why it carries over |
|---|---|
| [[projects/deploymentbox/adr/0004-tag-driven-central-releases]] | Distribution shape unchanged: groupId `no.virtual-architect`, tag-driven, release-only (no snapshots), one GPG key for all libraries, Sonatype Central Portal as endpoint. v3 inherits all of this |

ADR-0003's *key-custody contract* (private signing key lives
only on YubiKey hardware; never on filesystem; never in CI
secrets) is also carried over — only the *transport mechanism*
(SSH-forwarded gpg-agent) is dropped. v3 strengthens the
contract: the signing key never even appears in the same
process tree as a network-reachable service.

### What v3 requires of each library repo

Per-library invariants this ADR commits each
`no.virtual-architect` library to:

- A pinned-action `.github/workflows/release.yml` with:
  - `permissions: { id-token: write, attestations: write, contents: read }`
  - `concurrency: { group: release-${{ github.ref }}, cancel-in-progress: false }`
  - Every `uses:` pinned to a commit SHA, not a tag
  - `actions/attest-build-provenance` over every artifact
    intended for publishing
  - `actions/upload-artifact` of the artifacts + attestation
    bundle
- A separate `.github/workflows/test.yml` for PR-time testing,
  *without* `id-token`/`attestations` permissions — keeps the
  high-privilege surface attached only to tag-triggered runs
- `flake.nix` already at the library root (carried over from
  v2 expectations; the Volpe pattern is the toolchain
  hermeticity guarantee)
- `pomSettings` in `build.mill` declaring `groupId
  no.virtual-architect`, `developers`, `licenses`, `scmInfo`
  per ADR-0004

The deploymentbox project's "code" is now primarily a
**workflow template** + an operator-side release script,
not a Hetzner host configuration. The actual workflow YAML
and the laptop script are out of this ADR's scope — they
land in each library repo (workflow) and the operator's
dotfiles or a small tool (script). Both are tracked as v3
follow-up work in the design doc's "Open Questions".

## Consequences

- **Cost: €0/mo.** Hetzner CX32 line item disappears.
  GitHub Actions for public repositories is free at the scale
  these libraries release.
- **Maintenance: ~zero.** No NixOS host to keep patched. No
  microvm.nix toolchain to track. No MinIO uptime. No
  hardening surface to maintain. The workflow YAML is the
  entire "infrastructure".
- **Stronger provenance than v2.** v2's SHA-256 manifest
  proved "the host signs what the microVM emitted" —
  integrity, not provenance. v3's sigstore attestation proves
  "this artifact was built by *this* workflow from *this*
  source commit, witnessed in a public transparency log."
  This is the SLSA Build L3 property and the strongest
  provenance primitive currently available without operating
  a private signing CA.
- **Public reproducibility.** Any community member can fork
  the library, push the same tag, and observe whether their
  fork's build produces byte-identical artifacts. v2's build
  happened inside a private Firecracker microVM — only the
  operator could rerun it. v3's build is fully observable.
- **New trust extension to GitHub Actions infrastructure.**
  The largest concrete cost. Mitigation: source already lives
  on GitHub; the trust delta is "GitHub built what GitHub
  serves the source for", which is small compared to "GitHub
  builds and *signs* releases" (the latter is what we still
  do *not* do — signing stays on the YubiKey).
- **Signing key never traverses a network.** v2 had the
  signing-key socket forwarded over SSH; the YubiKey was on
  the laptop but the signing requests flowed laptop → host →
  laptop. v3 signs entirely locally; the YubiKey response
  never leaves the laptop's USB bus.
- **No CI signing path.** Like v2 (per ADR-0003), v3 still
  requires operator presence + YubiKey touch per artifact.
  This is intentional and load-bearing. A future "automate
  signed releases on tag push" request must continue to be
  rejected unless an explicit ceremony change is made.
- **One GitHub workflow per library to maintain.** ~50 lines
  of YAML per library. Versioning concerns: pinned action
  SHAs need periodic refresh (security updates to
  `actions/checkout`, `nix-installer-action`,
  `attest-build-provenance`). Manageable; one Dependabot or
  similar config can automate the PRs.
- **Operator wall-time per release: comparable to v2.**
  Workflow boot (~30s) + cold Nix install (~2-5 min on first
  run per cache window) is similar to microVM cold boot +
  cold Nix store pull. Warm-cache runs are faster in v3
  (DeterminateSystems Magic Nix Cache vs scratch volume).
- **Disposition of v2 scaffold.** The `/p/hg/deploymentbox/`
  repo with staged v2 changes is preserved — the
  recommendation in the v3 design's open question #6 is to
  commit the staged changes as a historical record and a
  starting point for any future private-artifact path, then
  let the repo go dormant. The repo is not deleted.
- **Scope is explicitly public OSS.** This ADR does not apply
  to any future private artifact. If `dependency-manager` (or
  any other private library) ever needs a signed-release
  pipeline, it must reach for the v2-shaped solution (a
  self-managed build environment that does not depend on a
  public CI substrate). Recorded here so a future "let's just
  use v3 for the private stuff too" request has explicit
  ground to argue against.

## Alternatives Considered

- **Stay on v2 (Hetzner host + Firecracker microVM + MinIO).**
  Rejected: cost (€7-8/mo + operator maintenance time),
  complexity (multiple ADRs of paranoid hardening), and — most
  importantly — *weaker* provenance than v3 (v2's SHA-256
  manifest is integrity-only; v3's attestation is full
  source-to-artifact provenance). The microVM isolation is
  *equivalent* to ephemeral runners for the malicious-dep
  threat; everything else net-favors v3 for public OSS.
- **Self-hosted GitHub Actions runner on Hetzner.** Combines
  the worst of both worlds: operator-managed substrate *plus*
  GitHub control plane. Doesn't earn sigstore attestation
  unless using GitHub's OIDC issuance (which works for self-
  hosted runners too, but the runner trust story gets
  complicated). Adds an operator-managed surface back into a
  design whose whole point is to remove one.
- **Sign on the GitHub runner with a key in Secrets.**
  Rejected for the same reason ADR-0003 originally rejected
  it: the signing key would exist in usable form somewhere
  other than the YubiKey. The whole architecture's
  defensibility rests on hardware-only key custody.
- **Use a GitHub Actions OIDC-bridged HSM (e.g. AWS KMS).**
  Considered. Possible (sigstore + GitHub OIDC + KMS is a
  documented pattern). Rejected: introduces cloud-HSM cost +
  vendor lock-in + a third-party trust dependency into the
  signing path, for marginal benefit over "operator touches
  YubiKey once per release". The whole point of YubiKey
  custody is operator-pacing of signature events.
- **Build on GitHub but skip sigstore attestation.** Rejected
  as the weak version of this approach. Without attestation,
  v3 collapses to "trust GitHub completely + SHA-256 from a
  webpage", which is what the user's initial sketch
  proposed. The attestation is what makes this *as strong*
  as v2 for the relevant threats, not just *easier*.
- **Pre-build locally with `nix develop` and *also* match
  against GitHub's build before signing.** Considered as a
  reproducibility cross-check. Recorded as v3 design open
  question #1; deferred. Cheap insurance but doubles operator
  wall-time; not load-bearing for the threat model.
- **Migrate to a different CI provider (Cirrus, Buildkite,
  CircleCI, etc.).** Not seriously considered: GitHub Actions
  is already the CI for the source repos; the operator has
  no preference for a different CI substrate; and sigstore
  attestation tooling is most mature on GitHub Actions.

## Links

- [[projects/deploymentbox/designs/release-pipeline-v3-github-attested]]
  — v3 design doc this ADR formalises.
- [[projects/deploymentbox/designs/release-pipeline-v2-microvm]]
  — superseded v2 design (Firecracker + MinIO).
- [[projects/deploymentbox/designs/release-pipeline]] — superseded
  v1 design (host builds directly).
- [[projects/deploymentbox/adr/0004-tag-driven-central-releases]]
  — distribution shape, unchanged.
- [[projects/deploymentbox/adr/0001-host-hetzner-nixos]] —
  superseded host decision; the GitHub-runner rejection is
  reconsidered in this ADR's §Context.
- [[projects/deploymentbox/adr/0003-signing-yubikey-forwarded]] —
  superseded for the *transport* part (SSH forwarding); the
  *key-custody contract* (YubiKey-only, never on filesystem,
  never in CI secrets) carries over and is strengthened.
- [[projects/deploymentbox/adr/0005-build-in-firecracker-microvm]]
  — superseded build-isolation decision; ephemeral runners
  give equivalent malicious-dep containment for public OSS.
- [[projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening]]
  — superseded; no host to harden.
- [[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]]
  — the per-repo flake-pinned toolchain pattern that makes
  the GitHub-hosted runner hermetic; load-bearing for v3.
- Sigstore: https://www.sigstore.dev — transparency log + signing infra.
- GitHub artifact attestations: https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations
- SLSA framework: https://slsa.dev — the provenance level v3 reaches (Build L3).
