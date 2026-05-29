---
id: option-cpu-memory
title: "CPU and Memory Options"
category: option
layer: core
tags: [vcpu, mem, balloon, hotplug, virtio-mem, hugepage]
source_files:
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
source_commit: 0d49083
api_surface:
  - microvm.vcpu
  - microvm.mem
  - microvm.cpu
  - microvm.hugepageMem
  - microvm.hotplugMem
  - microvm.hotpluggedMem
  - microvm.balloon
  - microvm.initialBalloonMem
  - microvm.deflateOnOOM
related: [recipe-cpu-emulation, hypervisor-cloud-hypervisor, hypervisor-qemu]
see_also: []
---

## CPU

| Option | Type | Default | Notes |
|---|---|---|---|
| `microvm.vcpu` | positive int | `1` | Number of virtual CPU cores |
| `microvm.cpu` | nullable str | `null` | Emulated CPU model (qemu only). Setting a foreign arch triggers cross-build mode. See [[recipe-cpu-emulation]] |

If `microvm.cpu == null` on qemu, the runner picks `host` (with
`+x2apic,-sgx` on x86_64-linux due to a known qemu microvm crash).

## Memory

| Option | Type | Default | Notes |
|---|---|---|---|
| `microvm.mem` | positive int | `512` | Base RAM in MiB |
| `microvm.hugepageMem` | bool | `false` | Use hugepages backend — cloud-hypervisor only |
| `microvm.hotplugMem` | unsigned int | `0` | Max additional MiB hot-pluggable via virtio-mem |
| `microvm.hotpluggedMem` | unsigned int | `microvm.hotplugMem` | Initial amount of hotplug memory the VM starts with |

## Ballooning

| Option | Type | Default | Notes |
|---|---|---|---|
| `microvm.balloon` | bool | `false` | Enable virtio-balloon. Inflating reclaims guest RAM to the host |
| `microvm.initialBalloonMem` | unsigned int | `0` | Initial balloon size in MiB |
| `microvm.deflateOnOOM` | bool | `true` | Auto-deflate on guest OOM |

> "virtio-mem is recommended over ballooning if supported by the
> hypervisor." (`microvm.balloon` description)

Memory mechanisms by hypervisor (see [[concept-hypervisor-matrix]]):

| Mechanism | qemu | CHV | firecracker | others |
|---|:---:|:---:|:---:|:---:|
| Balloon | ✓ | ✓ | ✓ | ✗ |
| Virtio-mem (`hotplugMem`) | ✓ | ✓ | ✗ | ✗ |
| Hugepages (`hugepageMem`) | (✓) | ✓ | ✗ | ✗ |

## Removed Options

`microvm.balloonMem` (an old numeric option) was removed and replaced
by the boolean `microvm.balloon`. The `imports` block in
`options.nix` carries a `mkRemovedOptionModule` for the rename, so
old configs get a clear error.
