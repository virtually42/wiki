---
id: hypervisor-stratovirt
title: "stratovirt"
category: hypervisor
layer: integration
tags: [stratovirt, rust, openeuler, minimal]
source_files:
  - /p/gh/microvm.nix/lib/runners/stratovirt.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
source_commit: 0d49083
api_surface:
  - microvm.stratovirt.package
related: [concept-hypervisor-matrix]
see_also: []
---

## Overview

openEuler's Rust hypervisor. Minimal feature set in microvm.nix:
no shares, no control socket. Driver:
`/p/gh/microvm.nix/lib/runners/stratovirt.nix`.

## Key Options

| Option | Purpose |
|---|---|
| `microvm.stratovirt.package` | Defaults to `pkgs.stratovirt` |

## Restrictions

- **No 9p, no virtiofs.** Use `microvm.volumes` for state.
- **No control socket.** `microvm.socket` is ignored.
- No PCI/USB passthrough.
- No CPU emulation.

## When To Pick It

- Niche; for most use-cases qemu, cloud-hypervisor, or firecracker
  are easier defaults.
