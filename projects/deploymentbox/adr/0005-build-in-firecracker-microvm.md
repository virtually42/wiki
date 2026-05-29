---
id: deploymentbox-adr-0005
title: Build inside a Firecracker microVM, handed off via MinIO with SHA-256 verification
kind: normative
status: accepted
project: deploymentbox
created: 2026-05-29
compliance:
  adopts: []
  exceptions: []
  deviations: []
  ignores: []
supersedes:
  - projects/deploymentbox/designs/release-pipeline.md   # superseded scope: the "host runs the build directly" assumption
---

## Context

[[projects/deploymentbox/designs/release-pipeline]] v1 (this
project's original design, accepted 2026-05-29 earlier the same
day) had the *host* run `nix develop --command mill compile/test/publishSigned`
directly under the `release` user. The host was hardened against
remote attackers, but not against the build itself: a malicious
transitive dependency in any `/p/hg/<lib>/flake.nix` could execute
arbitrary code on the deploymentbox during `mill compile` or
during `nix develop`'s dependency resolution. The Sonatype token,
the host SSH keys, the system's other Nix store contents — all
reachable from the build process.

The threat model that motivated the deploymentbox in the first
place (*supply-chain attack* via a compromised dev environment)
was incompletely addressed: we removed the *laptop* as a build
environment, but the *deploymentbox itself* became a fresh single
point of attack for any malicious dep that landed in a library's
dependency closure.

[[microvm.nix]] (now in the wiki as an external-lib at
`microvm.nix/llm-wiki/`, source at `/p/gh/microvm.nix`) makes
declarative ephemeral microVMs trivial. Firecracker — AWS's
minimalist microVM monitor — is in the supported hypervisor
matrix. Its restrictions (no shares, TAP-only networking,
no PCI/USB passthrough) are *aligned* with our use-case rather
than against it: the build sandbox shouldn't have host filesystem
access, host PCI, or host USB — those would be attack surface.

## Decision

**Builds run inside a Firecracker microVM on the deploymentbox
host. The host orchestrates and signs but does not build.**

Architecture:

```
laptop (YubiKey) ──ssh+gpg-fwd──▶  deploymentbox host
                                       │
                                       │ (release user invokes
                                       │  release.sh)
                                       ▼
                       ┌──────────────────────────────────┐
                       │ release.sh on host:              │
                       │  1. write job to MinIO incoming/ │
                       │  2. systemctl start microvm@…    │
                       │  3. wait for .done marker        │
                       │  4. download from MinIO          │
                       │  5. verify SHA-256 manifest      │
                       │  6. gpg --detach-sign (YubiKey)  │
                       │  7. upload to Central Portal     │
                       │  8. clean MinIO bucket entry     │
                       └──────────┬───────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
  MinIO (localhost)       Firecracker microVM       Central Portal
  bind 10.0.0.1:9000      "build-sandbox"           (after sign)
  bucket: builds/         on internal bridge
  incoming/job.json       10.0.0.10
  <build-id>/manifest     reads incoming/job.json
  <build-id>/m2/…         clones, builds, hashes,
  <build-id>/.done        uploads, poweroffs
```

### What lives in the microVM (sandbox)

- A minimal NixOS rootfs with: `nix`, `git`, `bash`, `coreutils`,
  `jq`, `minio-client` (`mc`), `openssh-client` (for git over SSH if
  ever needed; HTTPS is the default).
- TAP networking only; static IP `10.0.0.10`.
- A scratch volume for `/nix/store` (writable, persistent across
  runs to cache Nix substituter pulls; wiped on a flag if poisoned).
- A oneshot systemd unit `build-job.service` that runs on boot:
  1. Pulls `builds/incoming/job.json` from MinIO (and removes it).
  2. Parses `repo`, `tag`, `build_id`.
  3. `git clone --depth 1 --branch <tag>
     https://github.com/tigidar/<repo>.git`.
  4. `nix develop --command mill -i __.compile/test/publishM2Local`.
  5. For each emitted artifact (`*.jar`, `*.pom`, `*.module`),
     compute SHA-256 and accumulate into `manifest.json`.
  6. `mc cp --recursive ~/.m2/repository/ host/builds/<build_id>/m2/`.
  7. `mc cp manifest.json host/builds/<build_id>/manifest.json`.
  8. Touch `host/builds/<build_id>/.done`.
  9. `systemctl poweroff`.

### What lives on the host

- The `release` user (unchanged from
  [[projects/deploymentbox/adr/0002-public-ssh-hardened]]).
- MinIO (single-node, bound to the internal bridge IP only).
- The Firecracker microVM definition (declared in the host's flake
  via `microvm.vms.build-sandbox`).
- The release script (orchestration + verify + sign + publish).
- `gpg`, reaching the YubiKey via the SSH-forwarded socket (per
  [[projects/deploymentbox/adr/0003-signing-yubikey-forwarded]] —
  unchanged).

### What the host does NOT do anymore

- The host does **not** run `mill`, `nix develop`, or any
  library-specific tool. The host's nix store contains only the
  microVM runner + MinIO + release.sh + SSH/firewall basics, not
  the build toolchain.
- The host does **not** clone source repos. The microVM does the
  clone; the host only ever sees compiled artifacts plus a
  manifest.
- The host does **not** trust any byte produced inside the
  microVM until the SHA manifest matches the downloaded
  artifacts. Network corruption, MinIO storage corruption, or
  process-boundary tampering would all surface at the SHA check.

### SHA-256 verification semantics

The SHA chain is **integrity, not provenance**:

- Microvm computes `SHA256(artifact_i)` for each artifact.
- Microvm uploads `(artifact_i, manifest_with_sums)` to MinIO.
- Host downloads `(artifact'_i, manifest')`.
- Host verifies `SHA256(artifact'_i) == manifest'.sums[i]`.
- On success: the host has the exact bytes the microVM produced.
- On failure: abort. Don't sign. Don't publish. Log the build_id.

This proves only that the bytes the host signs are the bytes the
microVM emitted — not that the microVM's *build* was honest. The
latter is what the **microVM isolation** itself provides: a
compromised dep can attack the microVM filesystem (ephemeral),
the microVM kernel (Firecracker's narrow virtio surface), or the
microVM network (TAP to the host, MinIO put-only). It cannot
reach the host filesystem, the GPG key (which isn't anywhere on
the box), the Sonatype token (host-only), or any other library's
build.

## Consequences

- **Threat-model gap closed.** A malicious transitive dependency
  in any `/p/hg/<lib>/flake.nix` now executes only inside the
  Firecracker microVM. The microVM has no access to host
  filesystem, host Nix store, host MinIO credentials beyond the
  bucket-prefix it can write to, or any signing key. Worst case
  for the attacker: a corrupted artifact gets uploaded to MinIO
  — caught by SHA verification, never signed, never published.
- **First-build cost is higher.** The microVM has its own nix
  store and pulls toolchain (JDK, Mill, every transitive dep)
  from `cache.nixos.org` and `central.sonatype.com` over the
  external NAT. The scratch volume caches across runs, so
  subsequent builds reuse the populated store. Expect a 5-15
  minute cold start on first build per library; sub-2-minute
  warm starts thereafter.
- **MinIO becomes part of the trusted base.** It is configured as
  a local-only service bound to the internal bridge IP. The
  release user can read all bucket contents; the microVM has a
  separate service account with put-only on its own build-id
  prefix. Compromise of MinIO leaks build artifacts (which are
  going to be published anyway) and the microVM's put credentials
  (rotatable). Does not compromise signing.
- **Per-library `nix develop` still load-bearing.** Each library
  brings its toolchain through its own `flake.lock`. The
  microVM is environment-agnostic; it just hosts the `nix develop`
  invocation. This preserves the
  [[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]]
  pattern, now one level deeper (microVM-inside-host-inside-Hetzner).
- **Build microVM is itself a derivation**, declared in
  `microvms/build-sandbox/configuration.nix` in this repo. Its
  closure is reproducible. If we ever suspect the microVM image
  itself was tampered with, rebuilding from the host's
  `flake.lock` gives a bit-identical image.
- **One artifact path between microVM and host: MinIO over the
  internal bridge.** No virtio-fs, no shared `/nix/store`, no
  vsock channel. Smallest practical surface for inter-tier
  communication.
- **Operational visibility is now two-tier.** The microVM logs to
  serial (captured by the `microvm@build-sandbox.service` journal)
  and uploads a manifest. The host's release script tails both.

## Alternatives Considered

- **Build directly on the host (the v1 design).** Rejected as
  failing the supply-chain motivation. See "Context".
- **Build inside a `nix build` sandbox without a microVM.** Nix's
  build sandbox isolates against the host *filesystem* (mostly)
  but runs in the host kernel and can reach host resources via
  any unsandboxed daemon call. Adequate for casual builds;
  insufficient for an attacker-controlled dep that wants to
  reach `gpg-agent` or `~/.aws/credentials`.
- **Build inside a `systemd-nspawn` container.** A real
  improvement over plain `nix build`, but shares the host kernel
  and host PID/UID namespace surface. Not as tight as a microVM.
- **Cloud-hypervisor instead of Firecracker.** CH supports
  virtio-fs (host filesystem share) and is a fine choice if we
  wanted to share `/nix/store` with the microVM for build speed.
  We don't: the lack of shares is a *feature* — the microVM
  cannot reach host files even if compromised. Firecracker's
  narrower device matrix is the right answer here.
- **QEMU/KVM with the standard NixOS VM module.** Larger
  attack surface (QEMU exposes many emulated devices), slower
  boot, more complex config. The user explicitly preferred
  Firecracker.
- **vsock for artifact transport instead of MinIO over TAP.**
  vsock is narrower (no IP stack involved on the data plane),
  but requires a custom protocol on both ends. MinIO gives us
  S3 — a standard protocol with well-understood tooling, audit
  logs, and bucket policies — for the cost of one extra port
  on the internal bridge.
- **Pass the build job via kernel cmdline.** Considered but
  rejected: kernel cmdline is config-time in the microvm.nix
  flake; injecting it per-build means either rebuilding the
  microVM image per build (slow) or using an out-of-band
  override (fragile). MinIO incoming/job.json is per-build by
  construction and survives microVM redeploys.

## Links

- [[projects/deploymentbox/designs/release-pipeline]] — v1 design
  (superseded scope: the "host runs the build directly"
  assumption). v1 sections on Hetzner choice, SSH, YubiKey
  forwarding, and Central distribution remain valid.
- [[projects/deploymentbox/designs/release-pipeline-v2-microvm]] —
  v2 design covering the microVM + MinIO + SHA-verify flow.
- [[projects/deploymentbox/adr/0001-host-hetzner-nixos]] — host
  unchanged.
- [[projects/deploymentbox/adr/0002-public-ssh-hardened]] — SSH
  unchanged.
- [[projects/deploymentbox/adr/0003-signing-yubikey-forwarded]] —
  signing unchanged; still happens on the host with forwarded
  YubiKey.
- [[projects/deploymentbox/adr/0004-tag-driven-central-releases]]
  — distribution unchanged.
- [[projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening]]
  — paired hardening adoption.
- [[microvm.nix/llm-wiki/hypervisors/firecracker]] — Firecracker
  capability surface.
- [[microvm.nix/llm-wiki/recipes/declarative]] — declarative
  `microvm.vms.<name>` pattern.
- [[microvm.nix/llm-wiki/recipes/advanced-network]] — internal
  bridge + NAT, which the deploymentbox adopts.
