---
id: option-hypervisor-extra-args
title: "Per-Hypervisor Knobs"
category: option
layer: integration
tags: [extraArgs, package, hypervisor-config]
source_files:
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
source_commit: 0d49083
api_surface:
  - microvm.qemu.extraArgs
  - microvm.qemu.machine
  - microvm.qemu.machineOpts
  - microvm.qemu.pcieRootPorts
  - microvm.qemu.serialConsole
  - microvm.qemu.package
  - microvm.alioth.package
  - microvm.cloud-hypervisor.extraArgs
  - microvm.cloud-hypervisor.platformOEMStrings
  - microvm.cloud-hypervisor.package
  - microvm.crosvm.extraArgs
  - microvm.crosvm.pivotRoot
  - microvm.crosvm.package
  - microvm.firecracker.cpu
  - microvm.firecracker.driveIoEngine
  - microvm.firecracker.extraArgs
  - microvm.firecracker.extraConfig
  - microvm.firecracker.package
  - microvm.kvmtool.package
  - microvm.stratovirt.package
  - microvm.vfkit.extraArgs
  - microvm.vfkit.logLevel
  - microvm.vfkit.package
related: [hypervisor-qemu, hypervisor-cloud-hypervisor, hypervisor-firecracker, hypervisor-crosvm, hypervisor-kvmtool, hypervisor-stratovirt, hypervisor-alioth, hypervisor-vfkit]
see_also: []
---

Each hypervisor exposes a small `microvm.<hv>.*` namespace for per-
hypervisor tuning. See the per-hypervisor pages for details; this
page is a flat index for grep.

## Common Patterns

- `microvm.<hv>.package` — every hypervisor accepts a package
  override. Defaults derive from `microvm.vmHostPackages` which
  defaults to `pkgs` (or `pkgs.buildPackages` if CPU emulation).
- `microvm.<hv>.extraArgs` — qemu, CHV, crosvm, firecracker, vfkit,
  alioth accept extra command-line args. Used as the escape hatch
  for anything not modelled by the higher-level options.

## qemu

- `machine` (e.g. `microvm`, `q35`, `virt`)
- `machineOpts` (attrset of machine-flag overrides)
- `extraArgs` (raw extra args)
- `serialConsole` (default `true`)
- `pcieRootPorts` (PCIe root ports for runtime hotplug)
- `package` (defaults to `qemu_kvm` on Linux when no CPU emulation)

## cloud-hypervisor

- `extraArgs` (the runner extracts `--vsock` / `--platform` for
  merging with computed values)
- `platformOEMStrings` (list of strings concatenated into
  `--platform oem_strings=[...]`)
- `package` (selects `cloud-hypervisor` or
  `cloud-hypervisor-graphics`)

## firecracker

- `cpu` (custom CPU template attrs)
- `driveIoEngine` (`Async` / `Sync`)
- `extraArgs`
- `extraConfig` (free-form JSON merged into the Firecracker config)
- `package`

## crosvm

- `extraArgs`
- `pivotRoot` (sandbox directory, `null` disables sandbox)
- `package`

## kvmtool / stratovirt / alioth

- `package` (only).

## vfkit

- `extraArgs`
- `logLevel` (`debug` / `info` / `error`)
- `package`
- `rosetta.enable` / `.install` / `.ignoreIfMissing` — see
  [[recipe-vfkit-rosetta]]
