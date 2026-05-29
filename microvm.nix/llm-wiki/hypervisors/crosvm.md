---
id: hypervisor-crosvm
title: "crosvm"
category: hypervisor
layer: integration
tags: [crosvm, rust, chromium-os, virtiofs, graphics]
source_files:
  - /p/gh/microvm.nix/lib/runners/crosvm.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
source_commit: 0d49083
api_surface:
  - microvm.crosvm.extraArgs
  - microvm.crosvm.pivotRoot
  - microvm.crosvm.package
related: [concept-hypervisor-matrix]
see_also: []
---

## Overview

Google's ChromeOS hypervisor. Supports virtiofs and a sandbox
`pivotRoot` mode, plus graphics via the cloud-hypervisor `crosvm`
graphics build. Driver: `/p/gh/microvm.nix/lib/runners/crosvm.nix`.

## Key Options

| Option | Purpose |
|---|---|
| `microvm.crosvm.extraArgs` | Extra command-line args |
| `microvm.crosvm.pivotRoot` | Sandbox directory for crosvm to pivot into; null disables the sandbox |
| `microvm.crosvm.package` | Defaults to `pkgs.crosvm` |

## Restrictions

- **9p shares are broken** (per upstream README table — use virtiofs).
- No `bridge` networking; tap and user only on this hypervisor.
- No CPU emulation.
- No control socket for `microvm-balloon` adjustment.

## When To Pick It

- You want graphics with a maintained Rust hypervisor on Linux.
- For most other use-cases qemu or cloud-hypervisor are simpler.
