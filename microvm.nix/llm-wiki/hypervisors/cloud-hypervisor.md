---
id: hypervisor-cloud-hypervisor
title: "cloud-hypervisor"
category: hypervisor
layer: integration
tags: [cloud-hypervisor, chv, rust, virtiofs, hugepage, vsock]
source_files:
  - /p/gh/microvm.nix/lib/runners/cloud-hypervisor.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
source_commit: 0d49083
api_surface:
  - microvm.cloud-hypervisor.extraArgs
  - microvm.cloud-hypervisor.platformOEMStrings
  - microvm.cloud-hypervisor.package
  - microvm.hugepageMem
related: [concept-hypervisor-matrix, recipe-share-nix-store]
see_also: []
---

## Overview

Rust hypervisor focused on cloud workloads. Strong virtiofs support
(no 9p). Supports vhost-user GPU, hugepages, virtio-mem hotplug,
ballooning, AF_VSOCK with systemd-notify integration.

Driver: `/p/gh/microvm.nix/lib/runners/cloud-hypervisor.nix`.

## Key Options

| Option | Purpose |
|---|---|
| `microvm.cloud-hypervisor.extraArgs` | Raw extra args; parsed by the runner to extract `--vsock` and `--platform` values so they merge with defaults |
| `microvm.cloud-hypervisor.platformOEMStrings` | Strings concatenated into `--platform oem_strings=[...]` (e.g. systemd credentials) |
| `microvm.cloud-hypervisor.package` | Defaults to `pkgs.cloud-hypervisor`, or `pkgs.cloud-hypervisor-graphics` when `microvm.graphics.enable = true` |
| `microvm.hugepageMem` | Use hugepages as memory backend (only respected on CHV) |

## Notable Behaviour

- **AF_VSOCK + systemd-notify**: setting `microvm.vsock.cid` enables
  the runner to advertise `supportsNotifySocket`, which lets the host
  module use `Type=notify` instead of `Type=simple` for cleaner
  startup. Without it the runner warns at eval time.
- **Memory `shared` flag**: forced `on` when virtiofs is in use or
  graphics is enabled (vhost-user needs shared memory). Else
  `mergeable = on` is set to enable KSM. The two flags are mutually
  exclusive in CHV.
- **Hugepages**: `microvm.hugepageMem = true` selects hugepage backend.
  Useful for low-latency workloads; needs host-side `vm.nr_hugepages`.

## Restrictions

- No 9p shares. Use `proto = "virtiofs"` for `microvm.shares`.
- No `type = "bridge"` interfaces; tap, macvtap, and user (limited) only.
- No PCI/USB passthrough comparable to qemu.
- CPU emulation not supported.
