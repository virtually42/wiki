---
id: source-microvm-nix
type: external-lib
repo: /p/gh/microvm.nix
origin: https://github.com/microvm-nix/microvm.nix.git
upstream: https://github.com/microvm-nix/microvm.nix.git
wiki_path: microvm.nix/llm-wiki/
last_observed: 2026-05-29
commit: 0d49083
wiki_sections:
  - concepts
  - hypervisors
  - options
  - host
  - recipes
  - conventions
---

## Purpose

Nix flake to build NixOS guests and run them as MicroVMs on one of
eight Type-2 hypervisors (qemu, cloud-hypervisor, firecracker, crosvm,
kvmtool, stratovirt, alioth, vfkit). Provides:

- A `microvm` NixOS guest module (`nixos-modules/microvm/`).
- A `host` NixOS module (`nixos-modules/host/`) with systemd template
  units to run MicroVMs as services.
- A `microvm` CLI for imperative management.
- A runner-package contract that lets non-NixOS guests integrate.

## Wiki Location

The wiki lives in this repo at `microvm.nix/llm-wiki/`. Source code
lives at `/p/gh/microvm.nix`.

Pages reference source files with absolute paths
(e.g. `/p/gh/microvm.nix/nixos-modules/microvm/options.nix`).

Key sections:
- **concepts** — MicroVM model, hypervisor matrix, runner package,
  store-on-disk, compartmentalisation rationale
- **hypervisors** — one page per supported hypervisor (capabilities,
  restrictions, options)
- **options** — guest `microvm.*` option groups
  (hypervisor selection, CPU/memory, volumes, interfaces, shares,
  devices, graphics, vsock, store disk, forward-ports, misc,
  per-hypervisor knobs, virtiofsd)
- **host** — host module options, systemd template services,
  `microvm.vms` declarative VMs, the `microvm` CLI, state-directory
  layout, autostart
- **recipes** — task-oriented: declaring/running, declarative VMs,
  three networking topologies, vhost-net, sharing `/nix/store`,
  writable overlay, CPU emulation, vfkit + Rosetta, SSH deploy,
  journald merge, device passthrough, macOS Linux builder
- **conventions** — runner-package file layout (the integration
  contract with the host module) and custom-OS runners

## Refresh Procedure

```bash
# 1. Update source repo
cd /p/gh/microvm.nix
git fetch origin
git rebase origin/main

# 2. Back in wiki, update stale pages against new source.
#    Compare each page's source_commit (0d49083 at last ingest)
#    against current HEAD; re-read the listed source_files.
```

## Note

Cloned directly from upstream (`microvm-nix/microvm.nix`), no
personal fork. If a fork is created later, update `origin` to point
to the fork and add the upstream remote.
