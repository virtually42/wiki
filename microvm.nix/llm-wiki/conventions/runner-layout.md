---
id: convention-runner-layout
title: "Runner Package File Layout"
category: convention
layer: integration
tags: [runner, layout, contract, integration-points]
source_files:
  - /p/gh/microvm.nix/doc/src/conventions.md
  - /p/gh/microvm.nix/lib/runner.nix
  - /p/gh/microvm.nix/nixos-modules/host/default.nix
source_commit: 0d49083
api_surface: []
related: [concept-runner-package, host-systemd-services, convention-custom-runner]
see_also: []
---

## The Contract

A `microvm.nix` runner package must expose specific files for the
host module's systemd template services to find. This is the
**contract** between guest module and host module — and what makes
it possible to run non-NixOS guests on a microvm.nix host.

## Table

| `microvm.*` source | Runner file | Host service that consumes it | Purpose |
|---|---|---|---|
| `microvm.hypervisor` | `bin/microvm-run` | `microvm@.service` (ExecStart) | Start the hypervisor |
| `microvm.hypervisor` | `bin/microvm-shutdown` | `microvm@.service` (ExecStop) | Graceful shutdown (power button) |
| `microvm.interfaces.*.id` | `share/microvm/tap-interfaces` | `microvm-tap-interfaces@.service` | Names of TAP interfaces to create |
| `microvm.interfaces.*.id` | `bin/tap-up` / `bin/tap-down` | `microvm-tap-interfaces@.service` | Create / tear down TAPs |
| `microvm.interfaces.*` (macvtap) | `bin/macvtap-up` / `bin/macvtap-down` | `microvm-macvtap-interfaces@.service` | Create / tear down MACVTAPs |
| `microvm.devices.*.path` (bus="pci") | `share/microvm/pci-devices` | `microvm-pci-devices@.service` | PCI devices to bind to `vfio-pci` |
| `microvm.devices.*` | `bin/pci-setup` | `microvm-pci-devices@.service` | Run the vfio bind |
| `microvm.shares.*.source` (proto=virtiofs) | `share/microvm/virtiofs/${tag}/source` | `microvm-virtiofsd@.service` | Source dir per tag |
| `microvm.shares.*.socket` | `share/microvm/virtiofs/${tag}/socket` | `microvm-virtiofsd@.service` | virtiofsd socket per tag |
| (virtiofsd) | `bin/virtiofsd-run` | `microvm-virtiofsd@.service` | Exec the virtiofsd daemons |
| `microvm.systemSymlink` | `share/microvm/system` | (compare with `current`) | `config.system.build.toplevel` symlink for `microvm -l` |
| (systemd-machined) | `bin/microvm-register` / `bin/microvm-unregister` | `microvm@.service` ExecStartPost/StopPost | Optional registration with systemd-machined |

## Why It's Stable

The host module's systemd unit definitions are templated on
`${stateDir}/%i/current/bin/<X>` and
`${stateDir}/%i/current/share/microvm/<Y>` — they don't care **who**
built the runner, only that the files are present. The host module
uses `unitConfig.ConditionPathExists` so absent files turn into no-op
units rather than errors.

## Compatibility Activation Check

`system.activationScripts.microvm-update-check` in
`nixos-modules/host/default.nix` warns about MicroVMs that have the
old `share/microvm/{virtiofs,tap-interfaces,macvtap-interfaces,pci-devices}`
metadata without the matching `bin/{virtiofsd-run,tap-up,macvtap-up,pci-setup}`
scripts. Marked `TODO: remove in 2026`. Means: if you cloned an old
flake template, rebuild + redeploy the affected VMs.
