---
id: deploymentbox-adr-0003
title: GPG signing key on YubiKey 5, reached via SSH-forwarded gpg-agent
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

Maven Central requires signed artifacts. The operator must hold a
GPG key whose public half is registered on a keyserver under the
`no.virtual-architect` identity. The question this ADR answers is
**where the private half lives** at signing time.

The 2026-05-29 conversation walked through the threat-model
implications of each option in detail. This ADR records the chosen
posture and the alternatives that were rejected.

## Decision

The signing private key lives **only on a YubiKey 5** (OpenPGP
smartcard applet, signature slot). At release time, the box reaches
the key via SSH-forwarded gpg-agent socket from the operator's
laptop. Each Maven artifact signature requires a YubiKey touch.

Concretely:

- The signing key is **generated offline** (live USB or air-gapped
  laptop session), copied to the YubiKey + a backup YubiKey, master
  key + revocation cert stored offline (encrypted USB + paper),
  working software copy destroyed.  *(Ceremony deferred per the
  design doc's open question #1; this ADR records the architectural
  contract that whatever the ceremony, the key lives in hardware and
  is never installed on the deploymentbox.)*
- The deploymentbox runs `gpg` from `environment.systemPackages` but
  never has a private key in `~release/.gnupg/`.
- The `release` user's shell profile points `gpg` at the forwarded
  agent socket (`SSH_AUTH_SOCK` is for SSH keys; gpg uses its own
  socket path under `$GNUPGHOME` and SSH's `-R` forwarding maps the
  laptop's `extra-socket` to it).
- The operator's SSH invocation:
  ```
  ssh -R "$(gpgconf --list-dirs agent-socket):$(gpgconf --list-dirs agent-extra-socket)" \
      release@deploymentbox
  ```
  paired with `StreamLocalBindUnlink yes` on the server (per
  [[projects/deploymentbox/adr/0002-public-ssh-hardened]]).
- `mill __.publishSigned` invokes `gpg --detach-sign` per artifact.
  Each call traverses the forwarded socket; the YubiKey blinks; the
  operator touches; the signature returns; Mill proceeds.

## Consequences

- **Absolute key isolation.** The private key never sits on disk on
  the deploymentbox, in a GitHub Secret, in a cloud HSM, or on the
  operator's laptop filesystem in usable form. The only place it
  can be exfiltrated from is the YubiKey hardware itself, which
  requires physical access and resists extraction by design.
- **Compromise containment.** A compromised deploymentbox cannot
  forge signatures, because the private key isn't there. Worst-case
  recovery: rebuild the box from flake; rotate the Sonatype token;
  done.
- **Compromise containment of the laptop.** A compromised laptop
  could, in theory, ask the YubiKey for signatures while it's
  plugged in. Touch-required mode (configurable; recommended) means
  the attacker can't sign artifacts the operator hasn't authorised.
  Without touch-required, malware could sign while the YubiKey is
  inserted.
- **Operational cost.** Operator must be at their laptop with
  YubiKey plugged in at release time. Per release: ~30s of touches
  (one per artifact). Acceptable given release cadence.
- **No CI signing path.** GitHub Actions and the deploymentbox itself
  cannot sign without operator involvement. This is intentional and
  load-bearing. A future "automate signed releases on tag push"
  request must be rejected unless either (a) the YubiKey-on-laptop
  posture changes (e.g. dedicated USB-over-IP rig with the YubiKey
  always plugged in), or (b) a separate release-only subkey lives on
  the box (downgrade we don't want).
- **Backup story is non-trivial.** Lost YubiKey = identity
  unrecoverable unless backups exist. Mandates the offline
  generation + dual-YubiKey approach (or equivalent paper backup of
  the master). Captured as design-doc open question #1 — to be
  resolved at ceremony time.

## Alternatives Considered

- **Software key with passphrase on the deploymentbox.** Rejected:
  the private key sits on a network-reachable filesystem. Even
  passphrase-protected, a sufficient compromise (root + memory
  read) extracts the key. The whole point of the box is to remove
  this risk.
- **Software key in GitHub Secrets.** Rejected: same exfiltration
  surface as above plus a third-party (GitHub) holds the only copy.
  No offline backup possible from a write-only secret store.
- **Cloud HSM (AWS KMS, GCP KMS, Azure Key Vault).** Rejected:
  introduces third-party trust into the signing path, defeats the
  "single chokepoint we control" property, adds vendor lock-in,
  costs more than the rest of the infrastructure combined.
- **USB-over-IP with YubiKey plugged into a home-network appliance.**
  Considered. Would let the deploymentbox sign without operator
  involvement. Adds physical infrastructure (Raspberry Pi or
  similar), a network/power dependency for releases, and a remote
  attack surface against the YubiKey via the IP stack. Out of scope
  for v1; reconsider only if release cadence grows or if the
  manual-touch flow becomes a bottleneck.
- **Generate the key directly on the YubiKey (on-device).**
  Strongest security property — the key provably never existed off
  the device. *But* no backup possible; YubiKey loss = identity
  loss. Rejected as the primary path for v1 because no-backup is a
  single point of failure the operator can't tolerate. The
  offline-generate-then-import path gives nearly equivalent
  isolation with recoverable identity.

## Links

- [[projects/deploymentbox/designs/release-pipeline]]
- [[projects/deploymentbox/adr/0001-host-hetzner-nixos]]
- [[projects/deploymentbox/adr/0002-public-ssh-hardened]] — provides
  `StreamLocalBindUnlink yes` and agent forwarding settings this
  ADR depends on
- [[projects/deploymentbox/adr/0004-tag-driven-central-releases]] —
  defines the artifact set being signed
