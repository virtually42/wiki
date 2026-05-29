---
id: hypervisor-qemu
title: "qemu"
category: hypervisor
layer: integration
tags: [qemu, kvm, vhost-net, microvm-machine]
source_files:
  - /p/gh/microvm.nix/lib/runners/qemu.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
source_commit: 0d49083
api_surface:
  - microvm.qemu.machine
  - microvm.qemu.machineOpts
  - microvm.qemu.extraArgs
  - microvm.qemu.serialConsole
  - microvm.qemu.pcieRootPorts
  - microvm.qemu.package
related: [concept-hypervisor-matrix, recipe-vhost-net, recipe-cpu-emulation]
see_also: []
---

## Overview

The most featureful hypervisor. Linux + macOS (via TCG); on Linux uses
KVM acceleration. Default machine type is `microvm` (x86_64) or `virt`
(aarch64). Driver: `/p/gh/microvm.nix/lib/runners/qemu.nix`.

Supports every `microvm.*` option in this wiki, including CPU emulation
(`microvm.cpu`), all four interface types (`user`/`tap`/`macvtap`/`bridge`),
both share protocols (`9p`/`virtiofs`), PCI + USB passthrough, graphics,
virtio-mem hotplug, balloon, vhost-net acceleration.

## Key Options

| Option | Purpose |
|---|---|
| `microvm.qemu.machine` | `microvm` (x86_64-linux default), `virt` (aarch64-linux default), or `q35` for more PCI flexibility |
| `microvm.qemu.machineOpts` | Override default machine flags (`accel`, `pit`, `pic`, `pcie`, `rtc`, `usb`, …) |
| `microvm.qemu.extraArgs` | Raw extra args appended to the qemu command line |
| `microvm.qemu.serialConsole` | Enable virtual serial console (default `true`) |
| `microvm.qemu.pcieRootPorts` | List of PCIe root ports for runtime hotplug (mostly Q35) |
| `microvm.qemu.package` | Defaults to `pkgs.qemu_kvm` on Linux when `microvm.cpu == null`, else `pkgs.qemu` (or cross-compiled host package) |

## CPU Selection

From `lib/runners/qemu.nix`:

- If `microvm.cpu` is set, that string is passed to `-cpu`.
- Else on x86_64-linux: `-cpu host,+x2apic,-sgx` (SGX disabled due to
  a qemu crash on microvm machines).
- Else `-cpu host`.

Accel string: `kvm:tcg` on Linux, `hvf:tcg` on Darwin, `tcg` elsewhere.

## When the Machine Type Switches

The default `microvm` machine type is **switched off** (PCIe enabled
instead) when any of:

- `microvm.graphics.enable = true`
- `microvm.qemu.machine` is not `microvm` (e.g. you set `q35`)
- `microvm.shares` is non-empty (virtiofs needs PCI)
- A PCI device is in `microvm.devices`

This is logical in `lib/runners/qemu.nix` (`requirePci`). It means
adding any share or PCI device implicitly pulls in a heavier machine
type — relevant if you're chasing boot speed.

## Networking

- All four `interface.type` values (`user`/`tap`/`macvtap`/`bridge`) work.
- `tap.vhost = true` enables vhost-net offload (~10 Gbps vs ~1.5 Gbps).
  Only supported on qemu. Requires the host's `vhost_net` kernel module
  (loaded automatically by the host module when present). See
  [[recipe-vhost-net]].
- `type = "bridge"` requires `qemu-bridge-helper`; the host module
  installs it as a setuid wrapper with `cap_net_admin`. qemu runs
  *without* `-sandbox on` in this mode.
- `type = "user"` plus `microvm.forwardPorts` gives SLiRP port
  forwarding for IPv4. See [[option-forward-ports]].

## Restrictions

- USB devices require building qemu with `--enable-libusb` — handled
  automatically when any device has `bus = "usb"`.
- `microvm.optimize.enable` builds qemu without GUI (`nixosTestRunner`
  trick) unless graphics are on — saves hundreds of MB from the
  closure.
