---
id: factory-adr-0005
title: Secrets in /factory/secrets/ adopt deploymentbox YubiKey custody contract
kind: normative
status: accepted
project: factory
created: 2026-05-30
compliance:
  adopts:
    - projects/deploymentbox/adr/0007-build-on-github-with-attestations.md
  exceptions: []
  deviations: []
  ignores: []
supersedes: []
---

## Context

The factory monorepo needs a place for secrets used by workspace
tooling (Maven Central credentials, GitHub PATs for `pub/<lib>`
pushes, SSH keys for remotes, sops-encrypted host configs for
deployed services). The interview (Q9, Q11) raised two questions:

1. Where do the secrets files live (root-owned `/factory/secrets/`?
   user-owned? on a separate volume?).
2. How do we prevent backup leakage from exposing them?

Standard practice in the sops/age ecosystem is **encrypted at rest**:
ciphertext on disk is harmless; decryption keys live elsewhere
(YubiKey or `~/.config/sops/age/keys.txt`). deploymentbox v3 already
formalised the YubiKey custody contract for GPG signing of public
releases (deploymentbox ADR-0007). Factory secrets are a natural
extension.

The user accepted (Q9 follow-up): "I confirm and support your
vision on all points, I didn't remember that the secrets actually
are encrypted."

## Decision

1. **Location.** `/factory/secrets/` is a gitignored directory
   inside the monorepo tree. Permissions: user-owned, mode 0700
   (`drwx------`). No root-only restriction.
2. **Contents.** Only sops-encrypted ciphertext files
   (`.yaml`, `.json`, `.env`). Plaintext secrets are forbidden in
   `/factory/secrets/` and in any tracked file in the monorepo.
3. **Decryption keys.** Live **outside** `/factory/`:
   - **Local dev:** `~/.config/sops/age/keys.txt`, mode 0600.
   - **Production (deployed hosts):** YubiKey only, via sops-nix
     activation at boot. No keys on disk on the deployed host.
4. **YubiKey custody contract.** Inherited from deploymentbox
   ADR-0007:
   - The key never lives on a server filesystem.
   - The key never lives in CI secrets.
   - Backup story for the YubiKey itself is the same as
     deploymentbox's (open question carried forward — offline
     generation vs. on-device).
5. **Backup posture.** `/factory/secrets/` is **included** in
   off-site backups (via restic) **because it contains only
   ciphertext**. A leaked backup yields nothing without the
   YubiKey or `keys.txt`.

## Consequences

**Gains:**

- Backup leakage is no longer a paranoia point — the ciphertext is
  designed to be safely backup-able.
- One custody contract across the workspace (factory) and the
  publish pipeline (deploymentbox) — operator only manages one set
  of mental rules.
- Normal user-mode `sops decrypt` workflow during development; no
  `sudo` reflex.
- Adding a new secret is a `sops -e -i <file>` command; no special
  ceremony.

**Costs:**

- Requires age + sops + YubiKey GPG tooling available in the dev
  shell. Already there in deploymentbox's flake; factory's root
  `flake.nix` adds them workspace-wide.
- The YubiKey is now load-bearing for two workflows (publish +
  secret-decrypt on deployed hosts). Loss of the YubiKey is more
  costly. Mitigation: backup key on a second YubiKey kept offline
  (carried over from deploymentbox open question).
- sops requires per-file recipient metadata. Adding a new
  decryption identity (e.g. a new deployed host) means re-encrypting
  affected files. Acceptable — standard sops workflow.

## Alternatives Considered

- **Root-owned `/factory/secrets/` (initial Q9 proposal).**
  Rejected — root ownership is the wrong control surface
  (encryption is). Forces `sudo` for normal development.
- **Separate LUKS-encrypted volume for secrets.** Rejected — adds
  operational complexity (mount/unmount, separate key
  management, separate restore drill). The sops + YubiKey model
  already provides cryptographic separation.
- **Secrets outside `/factory/` entirely (e.g. `~/.factory-secrets/`).**
  Rejected — loses the workspace-rooted layout and the discovery
  via `tools/` scripts that expect `/factory/secrets/`.

## Links

- [[projects/factory/adr/0001-single-git-monorepo]]
- [[projects/deploymentbox/adr/0007-build-on-github-with-attestations]]
- [[projects/deploymentbox/index]]
- [[projects/factory/designs/factory-monorepo-topology]]
