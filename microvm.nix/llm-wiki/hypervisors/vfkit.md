---
id: hypervisor-vfkit
title: "vfkit"
category: hypervisor
layer: integration
tags: [vfkit, macos, virtualization-framework, apple-silicon, rosetta]
source_files:
  - /p/gh/microvm.nix/lib/runners/vfkit.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
  - /p/gh/microvm.nix/doc/src/vfkit-rosetta.md
source_commit: 0d49083
api_surface:
  - microvm.vfkit.extraArgs
  - microvm.vfkit.logLevel
  - microvm.vfkit.package
  - microvm.vfkit.rosetta.enable
  - microvm.vfkit.rosetta.install
  - microvm.vfkit.rosetta.ignoreIfMissing
related: [concept-hypervisor-matrix, recipe-vfkit-rosetta, recipe-macos-linux-builder]
see_also: []
---

## Overview

The only macOS-supported hypervisor. Frontend to Apple's
Virtualization.framework, written in Go. Built-in virtiofs support
(no virtiofsd sidecar required). User-mode networking only.

Driver: `/p/gh/microvm.nix/lib/runners/vfkit.nix`.

## Key Options

| Option | Purpose |
|---|---|
| `microvm.vfkit.extraArgs` | Extra command-line args |
| `microvm.vfkit.logLevel` | `debug` / `info` / `error` (default `info`) |
| `microvm.vfkit.package` | Defaults to `pkgs.vfkit` |
| `microvm.vfkit.rosetta.enable` | Enable Rosetta x86_64 binfmt on Apple Silicon |
| `microvm.vfkit.rosetta.install` | Auto-install Rosetta if missing |
| `microvm.vfkit.rosetta.ignoreIfMissing` | Continue even if Rosetta is unavailable (Intel Mac fallback) |

## Restrictions

- **macOS only.** Linux hosts can't use vfkit.
- **Only `type = "user"` networking.** The runner `throw`s on
  `tap`, `bridge`, or `macvtap` (vmnet-helper not yet wired).
- **Only `proto = "virtiofs"` shares.** 9p throws.
- No PCI/USB passthrough.
- No CPU emulation; matches host arch.
- Console: `tty0` when graphics is on, else `hvc0` (virtio-serial).

## Graphics

`microvm.graphics.enable = true` adds `--device virtio-gpu`,
`virtio-input,keyboard`, `virtio-input,pointing`. `microvm.graphics.backend`
defaults to `cocoa` on Darwin.

## Rosetta (Apple Silicon)

With `microvm.vfkit.rosetta.enable = true`:

- The runner appends `--device rosetta,mountTag=rosetta[,install][,ignoreIfMissing]`.
- The NixOS module (`rosetta.nix`) auto-mounts the virtiofs share and
  configures `binfmt` to handle x86_64 ELF binaries via Rosetta.

No guest changes are needed beyond enabling the option. See
[[recipe-vfkit-rosetta]].

## Building the Guest

`vfkit` runs natively on macOS but the *guest* is still Linux. You
need a Linux builder — see [[recipe-macos-linux-builder]].
