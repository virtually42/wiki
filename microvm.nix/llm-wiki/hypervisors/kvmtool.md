---
id: hypervisor-kvmtool
title: "kvmtool"
category: hypervisor
layer: integration
tags: [kvmtool, lkvm, minimal, c, 9p]
source_files:
  - /p/gh/microvm.nix/lib/runners/kvmtool.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
source_commit: 0d49083
api_surface:
  - microvm.kvmtool.package
related: [concept-hypervisor-matrix]
see_also: []
---

## Overview

The original Linux KVM "tools" project; minimal C hypervisor. Supports
9p but **no virtiofs**, and lacks a control socket. User-mode networking
is supported but requires manual static IP setup in the guest (kvmtool
has no built-in DHCP server).

Driver: `/p/gh/microvm.nix/lib/runners/kvmtool.nix`.

## Key Options

| Option | Purpose |
|---|---|
| `microvm.kvmtool.package` | Defaults to `pkgs.kvmtool` |

## Restrictions

- **No virtiofs shares.** Use `proto = "9p"`.
- **No control socket.** `microvm-balloon` runtime adjustment is
  unavailable; `microvm.socket` is ignored.
- No PCI/USB passthrough.
- No CPU emulation.

## Networking Quirks

- `type = "user"`: no DHCP server, so the guest needs static IP
  config (e.g. `systemd.network` with a fixed address on the eth
  interface — see the handbook's `interfaces.md`).

## When To Pick It

- You want a tiny C hypervisor and 9p is acceptable.
- For most use-cases qemu is a more capable default.
