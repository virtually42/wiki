---
id: hypervisor-firecracker
title: "firecracker"
category: hypervisor
layer: integration
tags: [firecracker, minimal, tap-only, no-shares]
source_files:
  - /p/gh/microvm.nix/lib/runners/firecracker.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
source_commit: 0d49083
api_surface:
  - microvm.firecracker.cpu
  - microvm.firecracker.driveIoEngine
  - microvm.firecracker.extraArgs
  - microvm.firecracker.extraConfig
  - microvm.firecracker.package
related: [concept-hypervisor-matrix]
see_also: []
---

## Overview

AWS's minimalist microVM monitor. JSON-configured, no PCI, no shares,
TAP-only networking. Smallest closure, fastest boot, narrowest feature
set. Configuration is generated as a JSON file passed via `--config-file`.

Driver: `/p/gh/microvm.nix/lib/runners/firecracker.nix`.

## Generated Config Highlights

The runner builds a `baseConfig` containing:

- `boot-source` — kernel image, initrd, fixed boot args
  (`console=ttyS0,115200 reboot=k panic=1 i8042.no*`).
- `machine-config` — vcpu count, mem in MiB, `smt` disabled on
  aarch64-linux (Firecracker doesn't support it there).
- `drives` — first drive is the read-only store disk; further drives
  come from `microvm.volumes` (the `serial` and `direct` options
  produce eval warnings — not supported).
- `network-interfaces` — only `type = "tap"` accepted; any other
  type triggers `throw`.
- `vsock` — populated from `microvm.vsock.cid`.
- `cpu-config` — from `microvm.firecracker.cpu` (custom CPU template
  JSON).

`microvm.firecracker.extraConfig` is `recursiveUpdate`-merged into the
base config — escape hatch for any Firecracker field this wiki
doesn't document.

## Key Options

| Option | Purpose |
|---|---|
| `microvm.firecracker.cpu` | Custom CPU template (JSON attrset) |
| `microvm.firecracker.driveIoEngine` | `Async` (default, io_uring) or `Sync` |
| `microvm.firecracker.extraConfig` | Free-form JSON merged into the config |
| `microvm.firecracker.extraArgs` | Extra command-line switches to the binary |

## Restrictions

- **No shares** at all (no 9p, no virtiofs). Use `microvm.volumes`
  for persistent data.
- **Only `type = "tap"` interfaces**; runner throws on any other type.
- No `microvm.cpu` emulation (only qemu does that).
- No PCI/USB passthrough.
- No graphics.
- Balloon supported, but virtio-mem hotplug isn't.

## When To Pick It

- You want minimal attack surface and don't need shares or PCI.
- You're running many cheap, network-only workloads (Firecracker's
  original niche).
- Other hypervisors here are easier defaults; reach for Firecracker
  intentionally.
