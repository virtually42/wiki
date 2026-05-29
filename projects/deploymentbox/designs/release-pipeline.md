---
id: deploymentbox-design-release-pipeline
title: Release pipeline v1 — host builds directly (SUPERSEDED)
kind: descriptive
status: superseded
superseded_by: projects/deploymentbox/designs/release-pipeline-v2-microvm.md
project: deploymentbox
created: 2026-05-29
updated: 2026-05-29
related_adrs:
  - projects/deploymentbox/adr/0001-host-hetzner-nixos.md
  - projects/deploymentbox/adr/0002-public-ssh-hardened.md
  - projects/deploymentbox/adr/0003-signing-yubikey-forwarded.md
  - projects/deploymentbox/adr/0004-tag-driven-central-releases.md
related_plans: []
sources:
  - sources/summaries/github_actions_nix_cachix_dhall_gvolpe.md
---

> **Superseded 2026-05-29** by
> [[projects/deploymentbox/designs/release-pipeline-v2-microvm]]. v2
> moves the build inside a Firecracker microVM with MinIO artifact
> handoff and SHA-256 verification (per
> [[projects/deploymentbox/adr/0005-build-in-firecracker-microvm]])
> and adopts selected paranoid-NixOS hardening (per
> [[projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening]]).
> The four v1 ADRs (0001-0004) remain accepted — they describe
> orthogonal concerns (host choice, SSH posture, signing,
> distribution) that v2 inherits unchanged.
>
> The text below is preserved as the historical record of the v1
> threat model and decision walk. Do not act on it as current
> guidance.

## Problem

`no.virtual-architect` will publish multiple Scala 3 libraries to
Maven Central, signed under one organisation identity. The operator
must be able to release new versions with:

- **No artifact tampering** introduced by laptop compromise — a
  supply-chain attack on the developer machine must not be able to
  smuggle malware into a signed release.
- **Hardware-isolated signing keys** — the private key must never sit
  on disk in software form on a host the network can reach.
- **Minimum management overhead** — the operator is one person; the
  release cadence is sporadic (a few releases per library per year);
  the infrastructure cannot demand maintenance time on its own.
- **Reproducible build environment** — toolchain pinning must be
  identical between any "before-release rehearsal" and the actual
  release.
- **Single chokepoint** — exactly one host produces signed Central
  artifacts. No second path that might escape the discipline.

## Constraints

- **Operator is solo.** Multi-operator workflows (HSM-backed CI,
  signing-as-a-service) are over-engineered for the scale.
- **Open source.** Compliance / audit demands don't drive the design;
  the threat model is "credible supply-chain attack against a
  single-operator open-source publisher."
- **YubiKey 5 in hand.** Hardware-isolated signing is available
  without new procurement.
- **No artifact must depend on a third-party CDN at publish time.**
  Specifically: rejects Cachix on release jobs per the negative
  recommendation in
  [[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]].
- **Personal-repo commit policy** applies to anything that lands at
  `/p/hg/deploymentbox/` (unsigned, no Co-Authored-By, author
  `tigidar`).

## Options Explored

### Option A: All-local releases from the operator's laptop

`mill __.publishSigned` runs on the laptop with YubiKey plugged in.
No external infrastructure. **Rejected:** the build runs in the same
environment the rest of the operator's work runs in, which is the
exact attack surface the operator wants to remove.

### Option B: GitHub-hosted runner with software signing key in Secrets

Standard model. Mill build inside `nix develop`; CI signs and
publishes; `GPG_PRIVATE_KEY` + `GPG_PASSPHRASE` in GitHub Secrets.
**Rejected:** puts the signing key on a cloud system as the *sole*
custodian, no offline backup possible, single point of compromise
(leaked secret = forgeable signatures forever). Also delegates the
build environment to GitHub's runner image whose preinstalled
toolchain is implicit and unpinned.

### Option C: Self-hosted GitHub Actions runner on a VPS

Solves the "GitHub runner toolchain trust" problem but inherits the
"key in cloud filesystem or in CI" problem. Adds a runner agent to
maintain. **Rejected as solving the wrong half of the problem alone;
considered as a Phase-2 extension.**

### Option D: VPS with USB-over-web-console for YubiKey

Operator's initial intuition. **Not technically possible:** cloud
VPS web consoles (Hetzner, AWS, GCP, DigitalOcean) expose the VM's
framebuffer but do not redirect USB devices from the operator's
browser host into the VM. USB-over-IP exists but is not exposed by
mainstream cloud providers.

### Option E: NixOS build host + SSH-forwarded gpg-agent socket (selected)

NixOS box on Hetzner Cloud (per
[[projects/deploymentbox/adr/0001-host-hetzner-nixos]]). Public
hardened SSH (per
[[projects/deploymentbox/adr/0002-public-ssh-hardened]]). The
`release` user on the box runs the release script. At release time,
the operator SSHes in with `-R` forwarding the gpg-agent socket;
`mill __.publishSigned` invokes `gpg` which reaches the YubiKey on
the operator's desk via the forwarded socket (per
[[projects/deploymentbox/adr/0003-signing-yubikey-forwarded]]).
Each artifact signature requires a YubiKey touch.

## Proposed Approach

Selected: Option E. The architecture diagram:

```
┌────────────────────────────────────────────────────────────────────────┐
│  Operator's laptop                                                     │
│                                                                        │
│    YubiKey 5 (USB)                                                     │
│        │                                                               │
│        ▼                                                               │
│    gpg-agent ────────► SSH (with -R agent-socket forwarding)           │
│                                                  │                     │
└──────────────────────────────────────────────────┼─────────────────────┘
                                                   │ public internet
                                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│  deploymentbox (Hetzner CX32, NixOS)                                   │
│                                                                        │
│    sshd (port 22, key-only, AllowUsers release,                        │
│          StreamLocalBindUnlink yes, fail2ban)                          │
│        │                                                               │
│        └─► release user                                                │
│              │                                                         │
│              └─► /etc/profile.d sets GNUPGHOME, points gpg to          │
│                  the forwarded socket                                  │
│              │                                                         │
│              └─► release.sh <repo> <tag>                               │
│                    │                                                   │
│                    ├─► git clone --depth 1 --branch <tag>              │
│                    │        github.com/tigidar/<repo>.git              │
│                    ├─► nix develop --command mill -i __.compile        │
│                    ├─► nix develop --command mill -i __.test           │
│                    └─► nix develop --command mill -i __.publishSigned  │
│                              │                                         │
│                              │ each signature → gpg → forwarded        │
│                              │ socket → YubiKey on operator's desk     │
│                              ▼                                         │
│                          [touch YubiKey]                               │
│                              │                                         │
└──────────────────────────────┼─────────────────────────────────────────┘
                               │ HTTPS upload (Central Portal token)
                               ▼
                       Maven Central (Sonatype)
```

### Per-release flow

1. **Tag the library locally.**
   `cd /p/hg/safetensors-scala && git tag v0.1.0 && git push origin v0.1.0`
2. **SSH to the deploymentbox with gpg-agent forwarding.**
   `ssh -R "$(gpgconf --list-dirs agent-socket):$(gpgconf --list-dirs agent-extra-socket)" release@deploymentbox`
3. **Trigger the release.**
   `release safetensors-scala v0.1.0` (the `release` command is the
   script in `/etc/profile` PATH; expanded inline as
   `bash ~/release.sh …` in v1).
4. **Touch the YubiKey** at each signature prompt (typically one per
   artifact: jar, sources.jar, javadoc.jar, pom — so ~4 touches per
   module per platform variant).
5. **Watch Mill complete the upload** to Central Portal.
6. **Disconnect.** Verify the release on
   https://central.sonatype.com.

### Secrets map (where each credential lives)

| Credential | Lives on | Used for | Lifetime |
|---|---|---|---|
| GPG signing private key | YubiKey hardware only | every Central artifact | identity-lifetime |
| GPG public key | keyservers + box GNUPGHOME | verification | identity-lifetime |
| GPG revocation cert | operator's offline backup (paper + encrypted USB) | emergency revocation | identity-lifetime |
| SSH private key | operator's laptop `~/.ssh/` | login to deploymentbox | rotatable per laptop |
| SSH public key | `release` user `authorized_keys` on box | accept logins | rotatable per laptop |
| Sonatype Central Portal token | box (sops-nix encrypted, decrypted at release time) | upload to Central | rotatable |
| Sonatype Central Portal account password | operator's password manager | recovery / re-issue tokens | rare |

The deploymentbox holds:

- **Public** key material (GPG pubkey, SSH authorized_keys)
- **Replaceable token** (Sonatype) — if leaked, rotate; no signature forgery possible because the GPG key is elsewhere
- **No private signing key** — even at rest, even encrypted

### Phases

**Phase 1 (this design):** open-source `/p/hg/` libraries only. One
box, one operator, one signing identity, public SSH.

**Phase 2 (future, not designed):** company software releases on the
same box or a sibling. Likely needs: distinct signing subkey for
company releases (kept on a separate YubiKey?), private dependency
access, possibly self-hosted Maven proxy. Out of scope here.

## Trade-offs

| Property | Got | Gave up |
|----------|-----|---------|
| Build env isolation | clean NixOS, declarative, pinned | none — solved cleanly |
| Key hardware isolation | absolute — key in YubiKey | none — strictly better than software keys |
| Operator-machine decoupling | mostly — no build state on laptop | laptop needed at release time for ~30s of YubiKey touches |
| Infrastructure complexity | one VPS to maintain | vs zero infra for Option A; vs zero infra for Option B |
| Cost | €7-8/mo | vs zero for hosted CI |
| Release ergonomics | `ssh + one command` | vs a button-click on GitHub UI |
| Audit story | clean — signed by hardware key, source verifiable from tag | (no formal audit story; this is a single-operator project) |

The traded-up properties (key isolation, build isolation) are
load-bearing for the threat model. The traded-down properties
(€7/mo, an SSH session per release) are cheap given the release
cadence (handful per library per year).

## Open Questions

1. **YubiKey key generation ceremony.** On-device generation
   (`gpg --card-edit` → `generate`) is the most secure but produces
   keys that *cannot be backed up*. If the YubiKey dies or is lost,
   the identity is unrecoverable. Alternative: generate offline
   (live USB, air-gapped machine), copy to YubiKey, store the master
   key on encrypted offline backup + revocation cert separately,
   then destroy the working software copy. **Not decided here** —
   this is a discrete future ceremony with its own checklist.
   Recommended: offline generation with offline backup. Records as
   a follow-up decision item.
2. **Subkey strategy.** Whether to use a single key for both
   signing and certification (simpler) or a master cert key + signing
   subkey on the YubiKey (more flexible — subkey rotation possible
   without changing identity). For one publisher with low key churn,
   single-key is fine. **Defer to ceremony day.**
3. **Sonatype namespace verification.** Parallel-track DNS TXT
   exercise. Until it verifies, `publishSigned` reaches the upload
   step and fails. Rehearsal up to `publishM2Local` works without it.
4. **Multi-YubiKey backup.** A second YubiKey as backup is highly
   recommended (one stays at home in a safe, one travels). Offline
   key ceremony makes this easy; on-device generation does not. The
   two-key argument reinforces the offline-generation
   recommendation.
5. **What happens if the box is compromised?** The box holds the
   Sonatype token and the box's SSH host key. Compromise →
   rotate token, rebuild the box from flake, regenerate host key.
   Signature forgery remains impossible because the GPG key is not
   there. Worst case: the attacker publishes nothing (no token they
   can't get) or publishes a stub (with a signature from a different
   key, which downstream consumers will reject if they check). This
   is the load-bearing property — record it explicitly.

## Decision Record

This design is the basis for the four ADRs under
[[projects/deploymentbox]]. Status: *accepted* on 2026-05-29 as the
v1 architecture. Revisions land here, with ADRs updated only when an
individual decision flips.
