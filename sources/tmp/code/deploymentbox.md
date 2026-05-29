---
id: source-deploymentbox
type: code
repo: /p/hg/deploymentbox
last_observed: 2026-05-29
commit: a978a76
branch: main
git_init_state: initialised + v1 committed by operator (SHA `a978a76` "init"); v2 changes staged on top — 8 files modified (`flake.nix`, `hosts/deploymentbox/default.nix`, `modules/build-toolchain.nix`, `modules/firewall.nix`, `modules/release-user.nix`, `scripts/release.sh`, `scripts/bootstrap.md`, `README.md`) and 4 new paths (`modules/microvm-host.nix`, `modules/minio.nix`, `modules/hardening.nix`, `microvms/build-sandbox/` containing `configuration.nix` and `build-job.sh`).  v2 awaiting operator commit.
entry_points:
  - README.md
  - flake.nix
  - hosts/deploymentbox/default.nix
  - hosts/deploymentbox/hardware.nix
  - hosts/deploymentbox/disko.nix
  - modules/ssh-hardened.nix
  - modules/firewall.nix
  - modules/release-user.nix
  - modules/build-toolchain.nix
  - modules/microvm-host.nix
  - modules/minio.nix
  - modules/hardening.nix
  - microvms/build-sandbox/configuration.nix
  - microvms/build-sandbox/build-job.sh
  - scripts/release.sh
  - scripts/bootstrap.md
design_source_of_truth: projects/deploymentbox/designs/release-pipeline-v2-microvm.md (wiki-side; v1 doc preserved as historical record)
---

## Structure Overview

`deploymentbox` is a flake-based declarative NixOS configuration for a
single Hetzner Cloud CX32 host whose only purpose is to build and
publish signed Maven Central artifacts for the `no.virtual-architect`
libraries living under `/p/hg/`. The host does not hold the signing
key — the YubiKey stays on the operator's laptop and is reached at
release time via SSH-forwarded gpg-agent socket.

The repository is **not yet git-initialised** as of 2026-05-29.
Initial commit is the operator's call per the personal-repo policy
(unsigned, no Co-Authored-By, author `tigidar`).

### Wiki-side architectural sources of truth

Unlike library projects, this repo's `README.md` is operational
(how to bootstrap and operate the box), not architectural. The
architectural source of truth lives in the wiki:

- [[projects/deploymentbox/designs/release-pipeline]] — end-to-end
  architecture, secrets map, alternatives considered, open questions.
- [[projects/deploymentbox/adr/0001-host-hetzner-nixos]] — host choice.
- [[projects/deploymentbox/adr/0002-public-ssh-hardened]] — SSH posture.
- [[projects/deploymentbox/adr/0003-signing-yubikey-forwarded]] — signing model.
- [[projects/deploymentbox/adr/0004-tag-driven-central-releases]] — distribution shape.

## Key Modules

### `flake.nix`

Inputs: `nixpkgs` (stable channel), `disko`, `nixos-anywhere`.

Outputs:

- `nixosConfigurations.deploymentbox` — the host config.
- `apps.<system>.bootstrap` — convenience wrapper around
  `nixos-anywhere` for fresh provisioning.

### `hosts/deploymentbox/default.nix`

Top-level host config. Imports `disko.nix` and all `modules/*.nix`.
Sets:

- `system.stateVersion = "25.05"` (or whichever the operator pins).
- `time.timeZone = "Europe/Oslo"`.
- `networking.hostName = "deploymentbox"`.
- Boot loader: `boot.loader.grub` for BIOS / EFI depending on
  Hetzner's image (Hetzner Cloud uses BIOS by default; configurable).

### `hosts/deploymentbox/disko.nix`

Single-disk EFI/BIOS layout for Hetzner Cloud's `/dev/sda`:
biosboot + small ESP + root ext4. Disko handles partitioning,
formatting, and mounting declaratively.

### `modules/ssh-hardened.nix`

The single most important file in the repo for the signing flow.
Sets `services.openssh.settings.StreamLocalBindUnlink = "yes";` —
without this, gpg-agent socket forwarding silently fails on the
second SSH session. Also: key-only auth, no root, `AllowUsers =
[ "release" ]`, fail2ban enabled.

### `modules/firewall.nix`

`networking.firewall.allowedTCPPorts = [ 22 ]`. Nothing else.

### `modules/release-user.nix`

The `release` user: non-root, no `wheel`, SSH key only, shell PATH
contains `release.sh`. No password, no sudo.

### `modules/build-toolchain.nix`

`environment.systemPackages = [ git curl gnupg pinentry-curses ]`.
Notably *not* JDK, *not* Mill. Each library brings its toolchain
through its own `flake.nix` consumed via `nix develop --command
mill …` inside `release.sh`.

### `scripts/release.sh`

Invoked over SSH as `release <repo> <tag>`. Clones the tag, runs
`nix develop --command mill -i __.compile/__.test/__.publishSigned`
inside a tmpdir, deletes the tmpdir on exit. Each
`mill publishSigned` invocation calls `gpg` which traverses the
forwarded socket to the laptop YubiKey.

### `scripts/bootstrap.md`

Operator-facing checklist (not a script — needs laptop-side
commands the box can't run for itself): provision the Hetzner
server, capture its IP, run `nix run github:nix-community/nixos-anywhere
-- --flake .#deploymentbox root@<ip>` from the laptop, log in once
to verify, populate the Sonatype token via sops.

## Build System

Nix flake. The host is rebuilt declaratively from `flake.nix` +
`flake.lock`. No imperative state survives a rebuild. State that
must persist (Sonatype token, host SSH keys) is either decrypted from
sops at boot or generated at first boot and persisted to
`/etc/ssh/`.

## State Survives Across Rebuilds

| What | Where | Survives `nixos-rebuild switch`? | Survives `nixos-anywhere` reinstall? |
|------|-------|----------------------------------|----------------------------------------|
| Host SSH keys | `/etc/ssh/ssh_host_*` | yes | **no** — regenerated; the laptop's `known_hosts` needs updating |
| `release` user authorized_keys | declared in nix | yes | yes (declared) |
| Sonatype token | sops-encrypted in flake → decrypted at boot | yes | yes (declared) |
| Nix store | `/nix/store` | yes | no (rebuilt; transparent except for cold-start time) |
| Cloned library repos during release | `/tmp/<tmpdir>` | no (intentional) | no |

## Compliance Scan

Against current wiki normative pages:

| Page | Stance |
|------|--------|
| [[tech/decisions/deps-single-file]] | **Not applicable.** This is an infra repo, not a Scala project; no `mvnDeps` to declare. |
| [[tech/patterns/functional-domain-design]] | **Not applicable.** Same reason. |
| [[tech/patterns/tdd-rhythm]] | **Not applicable.** Same reason. |
| [[tech/patterns/symmetric-refactoring]] | **Not applicable.** Same reason. |
| [[tech/patterns/test-economics]] | **Not applicable.** Same reason. |

The current tech-layer normative pages all target Scala source
code. No NixOS-side normative pages exist yet. If a second infra
project lands (per the deploymentbox project log's observation),
patterns common across NixOS configs (module organisation,
secret-management posture, SSH-hardening posture) become candidates
for promotion.

## Open Questions

1. **Initial commit.** Per the personal-repo commit policy, the
   operator decides when to `git init` and make the first commit.
2. **Promote bridge to `sources/raw/code/`.** After the initial
   commit, this bridge gets promoted with the real SHA filled into
   `commit:` and the `git_init_state:` field removed.
3. **First deploy.** The flake compiles in principle but has not
   been provisioned against a real Hetzner Cloud server. First
   provision will surface any disko / boot-mode mismatches.
4. **Sonatype token shape.** Provision a token after namespace
   verification; decide on sops vs. agenix vs. operator-pasted
   one-time secret. Captured in `scripts/bootstrap.md`.
5. **YubiKey ceremony.** Out of scope for the repo itself; captured
   as an open question in
   [[projects/deploymentbox/designs/release-pipeline]] §"Open
   Questions" item 1.
