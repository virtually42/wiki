---
id: deploymentbox-design-release-pipeline-v2-microvm
title: Release pipeline v2 — Firecracker microVM + MinIO + SHA verify
kind: descriptive
status: superseded
superseded_by: projects/deploymentbox/designs/release-pipeline-v3-github-attested.md
project: deploymentbox
created: 2026-05-29
updated: 2026-05-30
related_adrs:
  - projects/deploymentbox/adr/0001-host-hetzner-nixos.md
  - projects/deploymentbox/adr/0002-public-ssh-hardened.md
  - projects/deploymentbox/adr/0003-signing-yubikey-forwarded.md
  - projects/deploymentbox/adr/0004-tag-driven-central-releases.md
  - projects/deploymentbox/adr/0005-build-in-firecracker-microvm.md
  - projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening.md
related_plans: []
supersedes:
  - projects/deploymentbox/designs/release-pipeline.md
sources:
  - sources/summaries/github_actions_nix_cachix_dhall_gvolpe.md
  - sources/summaries/paranoid_nixos_xe_iaso.md
  - microvm.nix/llm-wiki/index.md
---

## What's different from v1

The [v1 design](release-pipeline.md) had the host run `mill` directly
under the `release` user — the build environment and the host were
the same trust boundary. v2 moves the build into a Firecracker
microVM and treats the host as a *signing and publishing
appliance*. Decision recorded in
[[projects/deploymentbox/adr/0005-build-in-firecracker-microvm]];
paired runtime hardening in
[[projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening]].

v1 sections that **remain** valid: host choice (Hetzner CX32
NixOS), SSH posture (public hardened, no VPN), signing model
(YubiKey forwarded over gpg-agent socket), distribution shape
(Maven Central tag-driven, no snapshots, one key).

v1 sections that v2 **replaces**: §"Per-release flow" (orchestration
is multi-tier now), the secrets map (extended with MinIO
credentials), the trade-off table (the threat model improves at
build-time cost).

## v2 architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Operator's laptop                                                           │
│                                                                             │
│   YubiKey 5 ──► gpg-agent ──► ssh -R agent-socket release@<deploymentbox>   │
│                                                                             │
└─────────────────────────────────────────────┬───────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ deploymentbox host (Hetzner CX32 NixOS, hardened per ADR-0006)              │
│                                                                             │
│  sshd (StreamLocalBindUnlink yes)                                           │
│   │                                                                         │
│   ▼                                                                         │
│  release user (no sudo, no nix, no wheel)                                   │
│   │                                                                         │
│   └─► release.sh <repo> <tag>                                               │
│         │                                                                   │
│         │  ┌───────────────────────────────────────────────────┐            │
│         │  │ MinIO (single-node, bound 10.0.0.1:9000)          │            │
│         │  │  bucket: builds/                                  │            │
│         │  │    incoming/job.json   ←┐                         │            │
│         │  │    <build_id>/manifest.json                       │            │
│         │  │    <build_id>/m2/...                              │            │
│         │  │    <build_id>/.done                               │            │
│         │  └─────────────────────────┼─────────────────────────┘            │
│         │                            │                                      │
│         ├──(1) write job to incoming/┘                                      │
│         │                                                                   │
│         ├──(2) systemctl start microvm@build-sandbox                        │
│         │            │                                                      │
│         │            ▼                                                      │
│         │     ┌──────────────────────────────────────────────────┐          │
│         │     │ Firecracker microVM "build-sandbox"              │          │
│         │     │   bridge: microvm0 (10.0.0.0/24)  ip: 10.0.0.10  │          │
│         │     │   NixOS rootfs (read-only base + writable        │          │
│         │     │      overlay on scratch volume)                  │          │
│         │     │   tools: nix, git, jq, mc, coreutils, openssh    │          │
│         │     │   on-boot: build-job.service                     │          │
│         │     │     ├─ mc cp host/builds/incoming/job.json       │          │
│         │     │     ├─ mc rm  host/builds/incoming/job.json      │          │
│         │     │     ├─ git clone --depth 1 --branch <tag>        │          │
│         │     │     │     github.com/tigidar/<repo>.git          │          │
│         │     │     ├─ nix develop -c mill -i __.compile         │          │
│         │     │     ├─ nix develop -c mill -i __.test            │          │
│         │     │     ├─ nix develop -c mill -i __.publishM2Local  │          │
│         │     │     ├─ build manifest.json with sha256 of each   │          │
│         │     │     │     emitted .jar / .pom / .module          │          │
│         │     │     ├─ mc cp --recursive ~/.m2/repository/       │          │
│         │     │     │     host/builds/<build_id>/m2/             │          │
│         │     │     ├─ mc cp manifest.json                       │          │
│         │     │     │     host/builds/<build_id>/manifest.json   │          │
│         │     │     ├─ mc cp /dev/null                           │          │
│         │     │     │     host/builds/<build_id>/.done           │          │
│         │     │     └─ systemctl poweroff                        │          │
│         │     └──────────────────────────────────────────────────┘          │
│         │                                                                   │
│         ├──(3) wait for .done marker in MinIO                               │
│         │                                                                   │
│         ├──(4) download manifest + m2/ to /var/lib/deploymentbox/work/<id>  │
│         │                                                                   │
│         ├──(5) verify sha256sum -c against manifest                         │
│         │       (abort on mismatch; never sign)                             │
│         │                                                                   │
│         ├──(6) for each artifact: gpg --detach-sign --armor                 │
│         │       (gpg-agent socket forwarded to laptop YubiKey;              │
│         │        operator touches once per artifact)                        │
│         │                                                                   │
│         ├──(7) upload signed bundle to Sonatype Central Portal              │
│         │                                                                   │
│         ├──(8) mc rm --recursive --force host/builds/<build_id>/            │
│         │                                                                   │
│         └──(9) rm -rf /var/lib/deploymentbox/work/<build_id>                │
│                                                                             │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
                            Maven Central (Sonatype)
```

## Per-release flow

From the operator's laptop, YubiKey plugged in:

```bash
ssh -R "$(gpgconf --list-dirs agent-socket):$(gpgconf --list-dirs agent-extra-socket)" \
    release@deploymentbox \
    release safetensors-scala v0.1.0
```

The remote `release` command runs the host-side script. The
operator stays on the SSH session because:

- **Step 6** (gpg sign) requires the YubiKey touch — multiple
  prompts (one per artifact), each blinking the YubiKey on the
  operator's desk. The session must stay open for the forwarded
  socket to remain reachable.

Typical timing for a small library (e.g. `sourceline-manager`,
one JVM module):

| Step | Time | Notes |
|---|---|---|
| Job write to MinIO | <1s | |
| microVM boot | ~5s | Firecracker is fast |
| Cold build | 5-15 min | first run per library — pulls JDK+Mill from cache.nixos.org |
| Warm build | 30-90s | scratch volume cached nix store |
| Tests | varies | per library |
| Manifest + upload | 5-30s | LAN to MinIO is fast |
| Host download + verify | 5-15s | |
| Sign | 10-30s | ~4 YubiKey touches per module per platform |
| Central upload | 10-60s | |
| Cleanup | 1-2s | |

## Secrets map (v2)

| Credential | Lives on | Used for | Lifetime |
|---|---|---|---|
| GPG signing private key | YubiKey hardware | every Central artifact | identity-lifetime |
| GPG public key | keyservers + host GNUPGHOME | verification | identity-lifetime |
| GPG revocation cert | operator's offline backup | emergency revocation | identity-lifetime |
| SSH private key (laptop) | operator's laptop `~/.ssh/` | login to host | rotatable |
| SSH public key (release) | host `release` authorized_keys (declared in flake) | accept logins | rotatable |
| Sonatype Central Portal token | host sops-encrypted secret (Phase 1: paste-once file) | upload to Central | rotatable |
| MinIO root credentials | host sops-encrypted (Phase 1: paste-once file) | host's bucket admin | rotatable |
| MinIO microvm-build credentials | host sops-encrypted, copied to microvm rootfs at build time | microvm put-only on `builds/<build_id>/*` | rotatable, scoped |

What the *microVM* holds (ephemeral, per-build):

- The `MINIO_BUILD_ACCESS_KEY` / `MINIO_BUILD_SECRET_KEY` (put-only)
- Whatever transitive deps `nix develop` pulled into its scratch
  store
- The cloned source tree (in `/work`)

What the *microVM* does **not** hold:

- The signing key (not anywhere on the host either; it's on the YubiKey)
- Sonatype credentials (host-only; only used after sign step)
- The release user's SSH keys
- The MinIO root credentials

## Trade-off table (revised from v1)

| Property | v1 (host builds) | v2 (microVM builds) |
|----------|------------------|---------------------|
| Build environment isolation from host | none — same trust boundary | Firecracker microVM — narrow virtio surface |
| Malicious dep blast radius | host filesystem + nix store + gpg-agent reachable | microVM ephemeral; no host access except MinIO put-only |
| Key hardware isolation | YubiKey | YubiKey (unchanged) |
| Cold build time | ~30s warm | 5-15 min cold (first per library), ~30-90s warm |
| Operational ceremony | ssh + 1 command | ssh + 1 command (same) |
| Host complexity | one user + sshd + gpg | host + MinIO + microvm.host module + bridge + NAT |
| Audit story (post ADR-0006) | none | execve audit on host (microVM logs to its serial console too) |

The cost is **first-build time** + **host complexity** + **operator
patience** during cold builds. The benefit is **threat-model
closure**: a malicious dep in any library's flake cannot escape
its microVM.

## Implementation map (where each piece lives in `/p/hg/deploymentbox/`)

| Component | File |
|---|---|
| Flake inputs (nixpkgs, disko, nixos-anywhere, microvm.nix) | `flake.nix` |
| Top-level host config | `hosts/deploymentbox/default.nix` |
| Disk layout | `hosts/deploymentbox/disko.nix` |
| Hetzner hardware bits | `hosts/deploymentbox/hardware.nix` |
| SSH hardening | `modules/ssh-hardened.nix` (unchanged) |
| Firewall (now includes 9000 internal + 67 DHCP) | `modules/firewall.nix` |
| Release user | `modules/release-user.nix` (gains `mc`) |
| Host minimal toolchain | `modules/build-toolchain.nix` |
| MinIO service | `modules/minio.nix` (NEW) |
| microvm.nix host module + bridge + NAT | `modules/microvm-host.nix` (NEW) |
| Paranoid-nixos hardening selections | `modules/hardening.nix` (NEW) |
| Firecracker build microVM config | `microvms/build-sandbox/configuration.nix` (NEW) |
| Build script that runs INSIDE the microVM | `microvms/build-sandbox/build-job.sh` (NEW) |
| Host-side orchestration script | `scripts/release.sh` (rewritten) |
| Operator bootstrap checklist | `scripts/bootstrap.md` (extended) |

## Open questions

All open questions from v1 still apply (YubiKey ceremony,
Sonatype namespace verification, etc.). v2 adds:

1. **Scratch volume reset policy.** The microVM's `/nix/store`
   lives on a writable scratch volume that persists across runs.
   This is wanted for cold-build speed. But a previously
   compromised dep could leave artefacts in the store. Policy:
   reset the scratch volume periodically (cron monthly?) or on
   explicit operator request via `reset-build-sandbox` script.
   Mechanism: a host systemd unit that stops microvm,
   `dd if=/dev/zero of=scratch.img` (or `truncate -s 0`), recreates,
   restarts. **Not implemented in v1 scaffold; logged here.**
2. **Manifest integrity in transit.** SHA-256 verification proves
   the host got what the microVM uploaded. But the manifest
   itself isn't signed inside the microVM — a tampering proxy
   between microVM and MinIO (none currently exists; everything
   is on a local bridge) could rewrite both. Acceptable risk for
   a local bridge; revisit if any inter-VM communication ever
   crosses an untrusted network.
3. **Build-time reproducibility check.** v2 does not yet
   re-build the artifact on the host and compare. Adding that
   gives "the microVM's build is reproducible" assurance, but
   doubles build time. Defer.
4. **Failure-mode telemetry.** When does the operator notice a
   `.done` marker isn't materialising? release.sh times out at
   30 minutes by default; the operator gets a non-zero exit.
   Diagnostics live in the microVM's journal (accessible from
   the host via `journalctl -u microvm@build-sandbox`).
   **Document this in `bootstrap.md`'s troubleshooting section
   when it gets written.**
5. **Per-library trust scoping.** Currently all libraries build
   in the same microVM (same scratch volume). Per-library
   sandboxes (separate microVMs) would cap cross-library
   contamination but multiply scratch-volume costs. Single
   microVM is fine for v1 since reset gives the same guarantee
   on demand.

## Decision Record

v2 is the **accepted** architecture as of 2026-05-29. v1 stays
in the repo as `release-pipeline.md` for the historical record;
its `superseded_by` field points here. The four v1 ADRs (0001-0004)
remain accepted with their scope intact — they describe orthogonal
concerns. The two v2 ADRs (0005, 0006) extend the architecture
into the build-time isolation and host-hardening dimensions
respectively.
