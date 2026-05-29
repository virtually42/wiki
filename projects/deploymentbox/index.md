# deploymentbox

Hardened single-purpose NixOS host on Hetzner Cloud that builds and
publishes signed Maven Central artifacts for the `no.virtual-architect`
libraries living under `/p/hg/`. The host **orchestrates and signs**;
the actual build runs inside a Firecracker microVM that hands off
artifacts via a local MinIO bucket with SHA-256 manifests. The signing
key stays on the operator's YubiKey and is reached over an SSH-forwarded
gpg-agent socket at sign time — *neither* the host nor the microVM
ever holds it.

**Status:** active (design-stage v2; pre-deploy — v2 repo scaffold
staged at `/p/hg/deploymentbox/`, not yet committed)

## Stack

- Host: Hetzner Cloud CX32 (4 vCPU, 8 GB RAM, EU-Helsinki or EU-Nuremberg)
- OS: NixOS (flake-based, declarative, reproducible) + selected hardening from [[sources/summaries/paranoid_nixos_xe_iaso]]
- Disk: Disko-managed single-disk layout
- Access: public SSH, key-only, fail2ban, `AllowUsers = [ "release" ]`
- Signing surface: gpg-agent socket forwarded from laptop YubiKey (no key material on host *or* microVM)
- Build isolation: Firecracker microVM (`microvm.vms.build-sandbox`) on an internal `microvm0` bridge (10.0.0.0/24) NATed through the host
- Build toolchain: JDK + Mill via per-library `nix develop` inside the microVM (toolchain not installed on the host)
- Artifact handoff: MinIO (single-node, bound to internal bridge IP) — microVM puts to `builds/<id>/`, host reads + verifies SHA-256 manifest before signing
- Install: `nixos-anywhere` over a fresh Hetzner Cloud server
- Cost: ~€7-8/mo (single CX32 covers host + microVM + MinIO comfortably)

## Code Location

`/p/hg/deploymentbox/` — repo scaffold per
[[projects/deploymentbox/designs/release-pipeline]]. Bridge file at
[[sources/tmp/code/deploymentbox]] (staged for promotion to
`sources/raw/code/` once the human makes the initial commit).
Personal-repo commit policy applies (unsigned, no Co-Authored-By,
author `tigidar`).

## Role in the Wiki

The deploymentbox is the **single chokepoint for publishing** any
`no.virtual-architect` artifact. Every Mill-built library that ships
to Maven Central does so through this box. The build itself is
isolated inside a Firecracker microVM; the host orchestrates and
signs:

```
laptop (YubiKey)
    │
    ├─ ssh+gpg-fwd ─▶ deploymentbox host (release.sh)
    │                       │
    │                       ├─ writes job to MinIO incoming/
    │                       ├─ starts microvm@build-sandbox
    │                       │      │
    │                       │      └─ Firecracker microVM:
    │                       │           git clone, nix develop,
    │                       │           mill compile/test/publishM2Local,
    │                       │           SHA-256 each artifact,
    │                       │           upload to MinIO builds/<id>/,
    │                       │           poweroff
    │                       │
    │                       ├─ wait .done in MinIO
    │                       ├─ download artifacts + manifest
    │                       ├─ verify sha256sum -c
    │                       └─ gpg --detach-sign per artifact ──┐
    │                                                            │
    └──── YubiKey signature (operator touches) ◀─────────────────┘
                                                                 │
                          Maven Central (Sonatype) ◀─────────────┘
```

The detailed flow with timing and secrets map lives in
[[projects/deploymentbox/designs/release-pipeline-v2-microvm]].

Libraries currently in scope: [[projects/safetensors-scala]],
[[projects/sourceline-manager]], [[projects/toolbox]] and any future
`/p/hg/` library that is open-sourced under `no.virtual-architect`.
[[projects/dependency-manager]] is **out of scope** — it is intentionally
unlicensed and not for distribution.

## Pages

### Designs

- [designs/release-pipeline-v2-microvm.md](designs/release-pipeline-v2-microvm.md)
  — **current** end-to-end architecture: host + Firecracker microVM
  + MinIO + SHA-256 verification. Secrets map, trade-offs, file
  inventory, open questions.
- [designs/release-pipeline.md](designs/release-pipeline.md) — **v1
  superseded.** Preserved as the historical record of the
  host-builds-directly threat model.

### ADRs

#### Inherited from v1 (still accepted, scope unchanged)

- [adr/0001-host-hetzner-nixos.md](adr/0001-host-hetzner-nixos.md) —
  Hetzner Cloud CX32 NixOS as the build host. Rejects GitHub-hosted
  runners (toolchain trust), self-hosted on laptop (supply-chain),
  AWS/GCP (cost / complexity), dedicated servers (overkill).
- [adr/0002-public-ssh-hardened.md](adr/0002-public-ssh-hardened.md) —
  Public SSH on port 22, key-only, fail2ban, `AllowUsers`, no root,
  `StreamLocalBindUnlink yes`. Rejects WireGuard-only and Tailscale for
  v1 on simplicity grounds; revisit if attack surface concerns emerge.
- [adr/0003-signing-yubikey-forwarded.md](adr/0003-signing-yubikey-forwarded.md) —
  GPG signing keys live on a YubiKey 5; the box reaches the key over
  an SSH-forwarded gpg-agent socket. The private key never traverses
  the network. Rejects software key on box, cloud HSM, USB-over-IP,
  GitHub-hosted CI signing.
- [adr/0004-tag-driven-central-releases.md](adr/0004-tag-driven-central-releases.md) —
  groupId `no.virtual-architect`; release flow keyed on git tags;
  releases only (no snapshots); one GPG key for all libraries.

#### New for v2

- [adr/0005-build-in-firecracker-microvm.md](adr/0005-build-in-firecracker-microvm.md)
  — **Build runs inside a Firecracker microVM**, not on the host
  directly. Host writes build job to MinIO `incoming/`; microVM
  pulls, builds, hashes, uploads to `builds/<id>/`; host verifies
  SHA-256 manifest before signing. Closes the build-time supply-
  chain threat surface. Rejects nix-sandbox-only, systemd-nspawn,
  cloud-hypervisor (wanted shares we don't want), QEMU (larger
  surface), vsock-only transport.
- [adr/0006-adopt-paranoid-nixos-hardening.md](adr/0006-adopt-paranoid-nixos-hardening.md)
  — Adopts selected layers from [[sources/summaries/paranoid_nixos_xe_iaso]]:
  restricted `nix.settings.allowed-users`, auditd execve logging,
  `noexec` on writable mounts, stripped `defaultPackages`, MinIO
  service hardening, kernel sysctls. **Defers**: tmpfs-root +
  impermanence (medium severity, expiry condition recorded);
  measured boot (Hetzner Cloud doesn't expose primitives).
  **Excepts**: Tailscale-only SSH (already explicitly rejected
  in ADR-0002); per-service-users carve-up (upstream NixOS
  modules already do this).

### Tickets, plans, syntheses

*None yet.* Plans land when work is broken down for the actual
deploy / bootstrap session.

### Other

- [log.md](log.md)

## Out of scope (and where the boundary is)

- **Library-side Mill `PublishModule` wiring.** Each `/p/hg/<lib>`
  decides for itself how it declares `pomSettings`, `groupId`,
  `developers`, etc. The deploymentbox only runs `mill __.publishSigned`
  — the *what* lives in the library's own `build.mill`.
- **GitHub Actions.** A separate, minimal test-only workflow lives
  in each library repo and is not in scope here. It runs tests on PR;
  it never publishes; it holds no signing secrets.
- **`dependency-manager` releases.** dm is unlicensed and internal —
  it does not publish to Central. The deploymentbox does not handle it.
- **Snapshot publishing.** Explicitly excluded per
  [[projects/deploymentbox/adr/0004-tag-driven-central-releases]].
  Local cross-library iteration uses `mill __.publishLocal` on the
  developer machine, not snapshots through the box.

## Open Questions

1. **Sonatype namespace verification timing.** The
   `no.virtual-architect` namespace claim is a parallel-track DNS
   TXT exercise on `virtual-architect.no` via uniweb.no. Until the
   namespace verifies, the Central upload step fails. The box can
   be built and the *microVM build + SHA verify + local sign* path
   exercised without it — only the final Central PUT requires the
   namespace.
2. **YubiKey key generation ceremony.** On-device vs.
   offline-then-import. Recorded in
   [[projects/deploymentbox/designs/release-pipeline-v2-microvm]]
   §"Open questions"; the answer affects the backup story but not
   the box's config.
3. **microVM scratch-volume reset policy.** The microVM's
   `/nix/store` cache survives across runs (cold-build cost was
   too painful otherwise). A reset script lets the operator wipe
   on suspicion of poisoning, but no scheduled reset is wired up
   yet. Tracked in the v2 design doc.
4. **MinIO root-credential bootstrap.** v1 scaffold has the
   operator paste credentials once during bootstrap; sops-nix
   migration is Phase 2. Cleanly delineated in `bootstrap.md`.
5. **Phase-2 future:** when company releases start, the box may
   need additional capacity, a second key (release-only subkey),
   per-customer microVMs, or extension to handle private repos.
   Out of scope for v2 baseline.
